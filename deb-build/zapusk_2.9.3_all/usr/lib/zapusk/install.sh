#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# EN: universal installer — any Linux distro + FreeBSD. Auto-detects the
#     package manager, installs Wine/Vulkan/tools, downloads DXVK if the
#     distro doesn't ship it (Zapusk does that at runtime too).
# RU: универсальный установщик — любой дистрибутив + FreeBSD. Определяет
#     пакетный менеджер, ставит Wine/Vulkan/утилиты.
set -e
info() { echo -e "\033[1;36m[ZAPUSK]\033[0m $*"; }
warn() { echo -e "\033[1;33m[ZAPUSK]\033[0m $*"; }

# --- детект ОС ---
if [ "$(uname -s)" = "FreeBSD" ]; then OS=freebsd; PM=pkg;
else
  . /etc/os-release 2>/dev/null || true
  OS="${ID:-linux} ${ID_LIKE:-}"
  case "$OS" in
    *arch*) PM=pacman;; *debian*|*ubuntu*) PM=apt;; *fedora*|*rhel*) PM=dnf;;
    *opensuse*|*suse*) PM=zypper;; *gentoo*) PM=emerge;; *alpine*) PM=apk;;
    *void*) PM=xbps;; *) PM=;; esac
fi
info "OS: ${PRETTY_NAME:-$OS} | package manager: ${PM:-unknown}"

[ -z "$PM" ] && { warn "Unknown distro — install wine + winetricks manually, Zapusk will handle the rest."; exit 0; }

# --- GPU ---
GPU=""
if lspci 2>/dev/null | grep -qi nvidia; then GPU=nvidia
elif lspci 2>/dev/null | grep -qiE "amd|radeon"; then GPU=amd
elif lspci 2>/dev/null | grep -qi intel; then GPU=intel; fi
info "GPU: ${GPU:-unknown}"

# --- пакеты ---
pkgs() {
  case "$PM" in
    pacman) echo "wine-staging winetricks vulkan-icd-loader lib32-vulkan-icd-loader vulkan-tools gamemode lib32-gamemode mangohud lib32-mangohud curl jq cabextract unzip p7zip";;
    apt)    echo "wine64 wine32:i386 winetricks vulkan-tools gamemode mangohud curl jq cabextract unzip p7zip-full";;
    dnf)    echo "wine winetricks vulkan-tools gamemode mangohud curl jq cabextract unzip p7zip";;
    zypper) echo "wine winetricks vulkan-tools gamemode mangohud curl jq cabextract unzip p7zip";;
    apk)    echo "wine winetricks vulkan-tools curl unzip";;
    xbps)   echo "wine winetricks vulkan-tools gamemode curl unzip";;
    pkg)    echo "wine-devel winetricks vulkan-tools curl jq unzip";;
    emerge) echo "app-emulation/wine-staging app-emulation/winetricks curl unzip";;
  esac
}
gpupkgs() {
  case "$PM:$GPU" in
    pacman:nvidia) echo "nvidia-utils lib32-nvidia-utils";;
    pacman:amd)    echo "lib32-mesa vulkan-radeon lib32-vulkan-radeon";;
    pacman:intel)  echo "lib32-mesa vulkan-intel lib32-vulkan-intel";;
    apt:*)         echo "mesa-vulkan-drivers mesa-vulkan-drivers:i386";;
    dnf:*)         echo "mesa-vulkan-drivers";;
    zypper:*)      echo "Mesa-vulkan-drivers";;
    *)             echo "";;
  esac
}

case "$PM" in
  apt) sudo dpkg --add-architecture i386; sudo apt update;;
  pacman) sudo pacman -Sy;;
esac

ALL="$(pkgs) $(gpupkgs)"
case "$PM" in
  pacman) sudo pacman -S --needed --noconfirm $ALL || warn "some packages failed";;
  apt)    sudo apt install -y $ALL || warn "some packages failed";;
  dnf)    sudo dnf install -y $ALL || warn "some packages failed";;
  zypper) sudo zypper install -y $ALL || warn "some packages failed";;
  apk)    sudo apk add $ALL || warn "some packages failed";;
  xbps)   sudo xbps-install -Sy $ALL || warn "some packages failed";;
  pkg)    sudo pkg install -y $ALL || warn "some packages failed";;
  emerge) sudo emerge --ask=n $ALL || warn "some packages failed";;
esac

info "Vulkan check: $(vulkaninfo --summary 2>/dev/null | grep -m1 deviceName || echo 'reboot may be needed')"
info "Done! / Готово! DXVK подтянется сам при первой починке игры."
