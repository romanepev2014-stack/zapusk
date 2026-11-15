#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# EN: run ON FreeBSD to build a .pkg from this source tree:
#       sh scripts/build_freebsd_pkg.sh
#     For the regular ports-based build use freebsd-port/Makefile instead.
# RU: запускается НА FreeBSD, собирает .pkg из текущего дерева исходников:
#       sh scripts/build_freebsd_pkg.sh
#     Штатная сборка через порты — в freebsd-port/Makefile.
set -e
[ "$(uname -s)" = "FreeBSD" ] || { echo "Run this on FreeBSD / Запускать только на FreeBSD"; exit 1; }
command -v pkg >/dev/null || { echo "pkg not found"; exit 1; }

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

VER=$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml | head -n 1)
[ -n "$VER" ] || { echo "Не удалось прочитать version из pyproject.toml"; exit 1; }
PYVER=$(python3 -c 'import sys; print(f"py{sys.version_info[0]}{sys.version_info[1]}")')

STAGE=/tmp/zapusk-pkg
PKG="zapusk-$VER.pkg"

rm -rf "$STAGE"
mkdir -p "$STAGE/usr/local/lib" "$STAGE/usr/local/bin" \
         "$STAGE/usr/local/share/applications" \
         "$STAGE/usr/local/share/icons/hicolor/scalable/apps" \
         "$STAGE/usr/local/share/licenses/zapusk"

cp -R src/zapusk "$STAGE/usr/local/lib/zapusk"
find "$STAGE/usr/local/lib/zapusk" -name __pycache__ -type d -prune -exec rm -rf {} +
find "$STAGE/usr/local/lib/zapusk" -name '*.pyc' -delete

cat > "$STAGE/usr/local/bin/zapusk" <<'EOF'
#!/bin/sh
PYTHONPATH="/usr/local/lib${PYTHONPATH:+:$PYTHONPATH}" exec python3 -m zapusk "$@"
EOF
chmod 755 "$STAGE/usr/local/bin/zapusk"

install -m644 assets/zapusk.desktop "$STAGE/usr/local/share/applications/zapusk.desktop"
install -m644 assets/zapusk.svg "$STAGE/usr/local/share/icons/hicolor/scalable/apps/zapusk.svg"
install -m644 LICENSE "$STAGE/usr/local/share/licenses/zapusk/LICENSE"

cat > /tmp/zapusk-manifest.json <<EOF
{
  "name": "zapusk",
  "version": "$VER",
  "origin": "games/zapusk",
  "comment": "Cyberpunk launcher for Windows games (Wine + DXVK auto-setup)",
  "desc": "Zapusk sets up wine prefixes, installs DXVK/VKD3D and Windows dependencies automatically so any Windows game runs with one click. 10 languages, any-distro support, FreeBSD Gaming Mode (GPU layer, bhyve GPU passthrough).",
  "maintainer": "romanepev2014@gmail.com",
  "www": "https://github.com/romanepev2014-stack/zapusk",
  "prefix": "/usr/local",
  "licenselogic": "single",
  "licenses": ["GPLv3+"],
  "deps": {
    "wine-devel":    { "origin": "emulators/wine-devel", "version": ">=10" },
    "winetricks":    { "origin": "emulators/winetricks", "version": ">=2023" },
    "$PYVER-pyside6": { "origin": "devel/pyside6",        "version": ">=6.5" },
    "curl":          { "origin": "ftp/curl",             "version": ">=8" }
  }
}
EOF

rm -f "$PKG"
pkg create -M /tmp/zapusk-manifest.json -r "$STAGE" -o .
echo "✅ Готово: $PWD/$PKG"
echo "   Установка: sudo pkg install ./$PKG   (или pkg add ./$PKG)"
