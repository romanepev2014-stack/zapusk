#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# EN: build a self-hosted pacman repo. Usage: sh scripts/make_repo.sh
#     Then push repo/ to GitHub (branch gh-pages) and users add the server
#     URL to /etc/pacman.conf. No AUR needed.
# RU: сборка собственного репозитория pacman. Результат в repo/ — залей на
#     GitHub Pages, и пользователи ставят пакет напрямую. Без AUR.
set -e
cd "$(dirname "$0")/.."

echo "=== собираем пакет ==="
bash build_package.sh >/dev/null 2>&1

echo "=== собираем репозиторий ==="
rm -rf repo
mkdir -p repo
cp dist/zapusk-*.pkg.tar.zst repo/ 2>/dev/null || cp *.pkg.tar.zst repo/
# EN: small packages also live in the repo -> direct download from the site
# RU: маленькие пакеты кладём в репозиторий -> скачивание прямо с сайта
cp dist/zapusk_*.deb repo/ 2>/dev/null || true
cp dist/*.rpm repo/ 2>/dev/null || true
cd repo
repo-add zapusk.db.tar.gz zapusk-*.pkg.tar.zst
ln -sf zapusk.db.tar.gz zapusk.db
ln -sf zapusk.files.tar.gz zapusk.files 2>/dev/null || true

echo ""
echo "✅ Репозиторий готов в папке repo/:"
ls -lh
echo ""
echo "Дальше:"
echo "1. Создай на GitHub репозиторий zapusk-repo"
echo "2. В папке repo/: git init && git add -A && git commit -m repo && git push"
echo "3. Settings -> Pages -> Source: main branch -> Save"
echo "4. Пользователям добавить в /etc/pacman.conf:"
echo ""
echo "   [zapusk]"
echo "   Server = https://romanepev2014-stack.github.io/zapusk-repo/"
echo ""
echo "   и затем: sudo pacman -Sy && sudo pacman -S zapusk"
