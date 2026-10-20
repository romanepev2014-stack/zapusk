#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# EN: build an AppImage (needs: python3+pip, appimagetool).
# RU: сборка AppImage (нужны: python3+pip, appimagetool).
set -e
cd "$(dirname "$0")"
VER=2.9.2
APPDIR=AppDir

rm -rf "$APPDIR" *.AppImage 2>/dev/null || true
mkdir -p "$APPDIR/usr/lib/zapusk" "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/scalable/apps"

# EN: bundle PySide6 (big, ~100MB) / RU: вшиваем PySide6 (~100 МБ)
python3 -m pip install --quiet --target "$APPDIR/usr/lib/python" PySide6
cp -r zapusk "$APPDIR/usr/lib/zapusk/"
cp install.sh requirements.txt "$APPDIR/usr/lib/zapusk/"

cat > "$APPDIR/usr/bin/zapusk" <<EOF
#!/bin/sh
export PYTHONPATH=$APPDIR/usr/lib/python:$APPDIR/usr/lib/zapusk
exec python3 -m zapusk gui "\$@"
EOF
chmod 755 "$APPDIR/usr/bin/zapusk"

cat > "$APPDIR/zapusk.desktop" <<EOF
[Desktop Entry]
Name=Zapusk
Exec=zapusk
Icon=zapusk
Type=Application
Categories=Game;Utility;
EOF
cp assets/zapusk.svg "$APPDIR/zapusk.svg"
ln -sf usr/bin/zapusk "$APPDIR/AppRun"

command -v appimagetool >/dev/null || { echo "Скачай appimagetool: https://github.com/AppImage/AppImageKit/releases"; exit 1; }
appimagetool "$APPDIR" "zapusk-$VER-x86_64.AppImage"
echo "✅ Готово: zapusk-$VER-x86_64.AppImage — запускается на любом Linux без установки"
