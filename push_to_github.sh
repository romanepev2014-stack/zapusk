#!/usr/bin/env bash
# EN: publish to GitHub. 1) create repo "zapusk" on github.com/new (no README!)
#     2) run: ./push_to_github.sh your_nick
# RU: публикация на GitHub. 1) создай репозиторий "zapusk" на github.com/new
#     (без README!) 2) запусти: ./push_to_github.sh твой_ник
set -e
NICK="${1:?usage: ./push_to_github.sh your_github_nick}"
git init
git add -A
git commit -m "Zapusk 2.6: cyberpunk Windows-games launcher for Arch Linux"
git branch -M main
git remote add origin "git@github.com:$NICK/zapusk.git"
git push -u origin main
echo "✅ https://github.com/$NICK/zapusk"
