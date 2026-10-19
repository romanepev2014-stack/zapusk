#!/usr/bin/env bash
# EN: install Zapusk as a user application (~/.local) — icon + menu entry.
# RU: ставим Zapusk приложением (~/.local) — иконка + пункт меню.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/.local/share/zapusk-app"
DESK="$HOME/.local/share/applications"
ICON="$HOME/.local/share/icons/hicolor/scalable/apps"

mkdir -p "$APP" "$DESK" "$ICON"
cp -r "$SRC/zapusk" "$APP/"
cp "$SRC/install_arch.sh" "$SRC/requirements.txt" "$APP/"
cp "$SRC/assets/zapusk.svg" "$ICON/zapusk.svg"

cat > "$DESK/zapusk.desktop" <<EOF
[Desktop Entry]
Name=Zapusk
Comment=Launch any Windows game on Arch Linux
Comment[ru]=Запуск любых Windows-игр на Arch Linux
Exec=python -m zapusk gui
Path=$APP
Icon=zapusk
Terminal=false
Type=Application
Categories=Game;Utility;
EOF

command -v update-desktop-database >/dev/null && update-desktop-database "$DESK" || true
echo "✅ Zapusk installed / установлено. Запуск из меню приложений или: python -m zapusk gui (в $APP)"
