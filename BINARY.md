# Сборка одного файла (как .exe на винде) / Single-file build

## Вариант 1 — установочный пакет Arch (рекомендую)

```bash
./build_package.sh
sudo pacman -U zapusk-2.6.0-1-any.pkg.tar.zst
```
Появится команда `zapusk` + иконка в меню. Удаление: `sudo pacman -R zapusk`.

## Вариант 2 — один бинарник через PyInstaller

```bash
pip install --user pyinstaller
pyinstaller zapusk.spec
```
Файл `dist/zapusk` — запускается сам по себе (`./dist/zapusk`),
можно кидать куда угодно. Размер ~100 МБ (внутри Qt).
Для других машин на той же архитектуре — работает без установки Python.

## Публикация в AUR

```bash
# после пуша на GitHub:
git clone ssh://aur@aur.archlinux.org/zapusk.git
cd zapusk
cp /путь/к/zapusk/aur/PKGBUILD .
# поменяй url на свой ник, сделай makepkg --printsrcinfo > .SRCINFO
makepkg --printsrcinfo > .SRCINFO
git add PKGBUILD .SRCINFO && git commit -m "zapusk 2.6.0"
git push
```
Любой сможет поставить: `yay -S zapusk`.
