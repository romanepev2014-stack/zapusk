#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# EN: build every package format into dist/. RU: собрать все форматы пакетов в dist/.
set -e
cd "$(dirname "$0")"
mkdir -p dist

echo "=== pacman ==="
bash build_package.sh >/dev/null 2>&1 && cp *.pkg.tar.zst dist/ 2>/dev/null || echo "pacman: пропуск (нужен Arch)"

echo "=== deb ==="
bash build_deb.sh >/dev/null 2>&1 && cp deb-build/*.deb dist/ 2>/dev/null || echo "deb: пропуск"

echo "=== rpm ==="
bash build_rpm.sh >/dev/null 2>&1 && find rpm-build/RPMS -name "*.rpm" -exec cp {} dist/ \; 2>/dev/null || echo "rpm: пропуск"

echo "=== AppImage ==="
bash build_appimage.sh >/dev/null 2>&1 && cp *.AppImage dist/ 2>/dev/null || echo "AppImage: пропуск (нужен appimagetool)"

echo ""
echo "✅ Готово, файлы в dist/:"
ls -lh dist/
echo ""
echo "Прикрепи их на странице релиза: github.com/romanepev2014-stack/zapusk/releases"
echo "Edit release -> перетащи файлы из dist/ в Assets -> Save"
