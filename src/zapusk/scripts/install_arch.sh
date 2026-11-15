#!/usr/bin/env bash
# EN: Zapusk system stack installer for Arch Linux.
#     Usage: ./install_arch.sh          (interactive, asks for GPU)
#            ./install_arch.sh --auto    (no prompts, autodetect GPU — for GUI)
# RU: Установщик системного стека Zapusk для Arch Linux.
#     Запуск: ./install_arch.sh         (интерактивно, спросит видеокарту)
#             ./install_arch.sh --auto  (без вопросов, автоопределение GPU — для GUI)

set -e

info() { echo -e "\033[1;36m[ZAPUSK]\033[0m $*"; }
warn() { echo -e "\033[1;33m[ZAPUSK]\033[0m $*"; }
die()  { echo -e "\033[1;31m[ZAPUSK]\033[0m $*"; exit 1; }

command -v pacman >/dev/null || die "This script is Arch Linux only / Скрипт только для Arch Linux (pacman не найден)"

# --- EN: pick GPU. RU: выбираем видеокарту ---
GPU=""
if [[ "$1" == "--auto" ]]; then
  # EN: autodetect from lspci. RU: автоопределение через lspci
  VGA=$(lspci 2>/dev/null | grep -iE "vga|3d" || true)
  if   echo "$VGA" | grep -qi nvidia; then GPU=nvidia
  elif echo "$VGA" | grep -qiE "amd|radeon"; then GPU=amd
  elif echo "$VGA" | grep -qi intel; then GPU=intel
  else GPU=amd; warn "GPU not detected / GPU не определён, ставлю AMD-стек"; fi
  info "Autodetected GPU / Автоопределена видеокарта: $GPU"
else
  info "GPU / Видеокарта: 1) NVIDIA  2) AMD  3) Intel"
  read -rp "GPU [1/2/3]: " c
  case "$c" in
    1) GPU=nvidia ;; 2) GPU=amd ;; 3) GPU=intel ;;
    *) die "Enter 1, 2 or 3 / Нужно ввести 1, 2 или 3" ;;
  esac
fi

case "$GPU" in
  nvidia) GPU_PKGS="nvidia-utils lib32-nvidia-utils nvidia-settings" ;;
  amd)    GPU_PKGS="lib32-mesa vulkan-radeon lib32-vulkan-radeon" ;;
  intel)  GPU_PKGS="lib32-mesa vulkan-intel lib32-vulkan-intel" ;;
esac

info "Installing system stack / Ставим системный стек..."
sudo pacman -Sy
sudo pacman -S --needed --noconfirm \
  wine-staging winetricks \
  vulkan-icd-loader lib32-vulkan-icd-loader \
  vulkan-tools \
  $GPU_PKGS \
  gamemode lib32-gamemode mangohud lib32-mangohud \
  dxvk \
  cabextract unzip p7zip curl jq || warn "Some packages failed / Часть пакетов не встала"

# EN: vkd3d-proton may be absent on some mirrors -> try repo, then AUR.
# RU: vkd3d-proton может отсутствовать в зеркалах -> репозиторий, потом AUR.
if ! pacman -Q vkd3d-proton >/dev/null 2>&1; then
  sudo pacman -S --needed --noconfirm vkd3d-proton || \
  if command -v yay >/dev/null; then yay -S --needed --noconfirm vkd3d-proton; \
  elif command -v paru >/dev/null; then paru -S --needed --noconfirm vkd3d-proton; \
  else warn "vkd3d-proton: поставь вручную / install manually: yay -S vkd3d-proton"; fi
fi

# EN: dxvk/vkd3d-proton may live in AUR on some mirrors
# RU: на некоторых зеркалах dxvk/vkd3d-proton живут в AUR
if ! pacman -Q dxvk >/dev/null 2>&1; then
  warn "dxvk not in repos / dxvk не найден в репозиториях, пробуем AUR"
  if command -v yay >/dev/null; then yay -S --needed --noconfirm dxvk-bin
  elif command -v paru >/dev/null; then paru -S --needed --noconfirm dxvk-bin
  else warn "Install yay first / Сначала поставь yay (AUR helper)"; fi
fi

# EN: user-level Python deps only when not root (GUI already needs PySide6 to run)
# RU: Python-зависимости ставим от юзера, не от рута (GUI и так требует PySide6)
if [[ $EUID -ne 0 ]]; then
  info "Python deps / Python-зависимости..."
  pip install --user -r requirements.txt 2>/dev/null || warn "pip failed / pip не сработал — GUI потребует PySide6"
fi

info "Vulkan check / Проверка Vulkan..."
if vulkaninfo --summary >/dev/null 2>&1; then
  info "Vulkan OK"
else
  warn "Vulkan not responding / Vulkan не отвечает — перезагрузись и проверь: vulkaninfo"
fi
info "Done! / Готово! Перезагрузка рекомендуется / Reboot recommended."
