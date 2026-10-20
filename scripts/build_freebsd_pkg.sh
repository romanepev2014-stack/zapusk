#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# EN: run ON FreeBSD to build a real .pkg package:
#       sh scripts/build_freebsd_pkg.sh
#     Produces zapusk-2.9.3.pkg in the current dir.
# RU: запускается НА FreeBSD, собирает настоящий .pkg-пакет одной командой.
set -e
[ "$(uname -s)" = "FreeBSD" ] || { echo "Run this on FreeBSD / Запускать только на FreeBSD"; exit 1; }
command -v pkg >/dev/null || { echo "pkg not found"; exit 1; }

VER=2.9.3
STAGE=/tmp/zapusk-pkg
PKG="zapusk-$VER.pkg"

rm -rf "$STAGE"
mkdir -p "$STAGE/usr/local/lib/zapusk" "$STAGE/usr/local/bin" \
         "$STAGE/usr/local/share/applications" \
         "$STAGE/usr/local/share/icons/hicolor/scalable/apps"

cp -R zapusk "$STAGE/usr/local/lib/zapusk/"
cp install.sh requirements.txt "$STAGE/usr/local/lib/zapusk/"

cat > "$STAGE/usr/local/bin/zapusk" <<'EOF'
#!/bin/sh
cd /usr/local/lib/zapusk && exec python3 -m zapusk gui "$@"
EOF
chmod 755 "$STAGE/usr/local/bin/zapusk"
install -m644 zapusk.desktop "$STAGE/usr/local/share/applications/zapusk.desktop"
install -m644 assets/zapusk.svg "$STAGE/usr/local/share/icons/hicolor/scalable/apps/zapusk.svg"

cat > /tmp/zapusk-manifest.json <<EOF
{
  "name": "zapusk",
  "version": "$VER",
  "origin": "games/zapusk",
  "comment": "Cyberpunk launcher for Windows games (Wine + DXVK auto-setup)",
  "desc": "Zapusk sets up wine prefixes, installs DXVK/VKD3D and Windows dependencies automatically so any Windows game runs with one click. 10 languages, any-distro support, FreeBSD Gaming Mode (bhyve GPU passthrough).",
  "maintainer": "romanepev2014@gmail.com",
  "www": "https://github.com/romanepev2014-stack/zapusk",
  "prefix": "/usr/local",
  "licenselogic": "single",
  "licenses": ["GPLv3+"],
  "deps": {
    "wine-devel":   { "origin": "emulators/wine-devel",   "version": ">=10" },
    "winetricks":   { "origin": "emulators/winetricks",   "version": ">=2023" },
    "py311-pyside6":{ "origin": "devel/pyside6",          "version": ">=6.5" },
    "curl":         { "origin": "ftp/curl",               "version": ">=8" }
  }
}
EOF

rm -f "$PKG"
pkg create -M /tmp/zapusk-manifest.json -r "$STAGE" -o .
echo "✅ Готово: $PWD/$PKG"
echo "   Установка: sudo pkg install ./$PKG   (или pkg add ./$PKG)"
