#!/usr/bin/env bash
# EN: build an installable Arch package (like a Windows .exe installer).
#     Produces zapusk-2.9.3-1-any.pkg.tar.zst -> install with pacman.
# RU: собираем установочный пакет Arch (аналог exe-инсталлятора).
#     На выходе zapusk-2.9.3-1-any.pkg.tar.zst -> ставится через pacman.
set -e
cd "$(dirname "$0")"
VER=2.9.3

command -v makepkg >/dev/null || { echo "нужен base-devel: sudo pacman -S --needed base-devel"; exit 1; }

echo "→ собираю исходник zapusk-$VER.tar.gz"
tar czf "zapusk-$VER.tar.gz" --transform "s,^,zapusk-$VER/," \
    zapusk install_arch.sh requirements.txt run.sh \
    zapusk.desktop assets LICENSE PKGBUILD README.md README.ru.md scripts

echo "→ собираю пакет (makepkg)"
makepkg -s --noconfirm

echo ""
echo "✅ Готово! Установить:  sudo pacman -U zapusk-$VER-1-any.pkg.tar.zst"
echo "   Удалить:             sudo pacman -R zapusk"
