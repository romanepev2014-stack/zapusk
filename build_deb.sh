#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# EN: build a .deb package for Debian/Ubuntu. / RU: сборка .deb для Debian/Ubuntu.
set -e
cd "$(dirname "$0")"
VER=2.9.3
STAGE="deb-build/zapusk_${VER}_all"

rm -rf deb-build
mkdir -p "$STAGE/usr/lib/zapusk" "$STAGE/usr/bin" "$STAGE/usr/share/applications" \
         "$STAGE/usr/share/icons/hicolor/scalable/apps" "$STAGE/DEBIAN"

cp -r zapusk "$STAGE/usr/lib/zapusk/"
cp install.sh requirements.txt "$STAGE/usr/lib/zapusk/"

cat > "$STAGE/usr/bin/zapusk" <<'EOF'
#!/bin/sh
cd /usr/lib/zapusk && exec python3 -m zapusk gui "$@"
EOF
chmod 755 "$STAGE/usr/bin/zapusk"

cp zapusk.desktop "$STAGE/usr/share/applications/zapusk.desktop"
cp assets/zapusk.svg "$STAGE/usr/share/icons/hicolor/scalable/apps/zapusk.svg"

cat > "$STAGE/DEBIAN/control" <<EOF
Package: zapusk
Version: $VER
Section: games
Priority: optional
Architecture: all
Depends: python3, python3-pyside6, wine, winetricks, curl, jq, cabextract, unzip, p7zip-full, vulkan-tools, fonts-noto-color-emoji
Recommends: gamemode, mangohud
Maintainer: roma_ogon <romanepev2014@gmail.com>
Description: Cyberpunk launcher for Windows games (Wine + DXVK auto-setup)
 Zapusk sets up wine prefixes, installs DXVK/VKD3D and dependencies
 automatically so any Windows game runs with one click.
EOF
cat > "$STAGE/DEBIAN/postinst" <<'EOF'
#!/bin/sh
# EN: enable i386 for 32-bit games / RU: включаем i386 для 32-бит игр
dpkg --add-architecture i386 2>/dev/null || true
exit 0
EOF
chmod 755 "$STAGE/DEBIAN/postinst"

dpkg-deb --build "$STAGE"
echo "✅ Готово: deb-build/zapusk_${VER}_all.deb"
echo "   Установка: sudo apt install ./deb-build/zapusk_${VER}_all.deb"
