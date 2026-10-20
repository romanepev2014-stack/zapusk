# 📦 Flatpak / Flathub / Debian

## Flatpak (локальная сборка)

```bash
sudo pacman -S flatpak flatpak-builder   # или apt install flatpak flatpak-builder
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub io.qt.PySide6.BaseApp//6.8 org.kde.Platform//6.8 org.kde.Sdk//6.8
cd flatpak
flatpak-builder --force-clean --install --user build-dir io.github.romaogon.zapusk.yml
flatpak run io.github.romaogon.zapusk
```

Важно: Zapusk внутри Flatpak — это «пульт». Wine, DXVK и драйверы живут на хосте:
кнопка «Установить всё» запускает пакетный менеджер хоста через `flatpak-spawn`,
игры запускаются через хостовый wine. Файловая система хоста доступна.

## Flathub (публикация)

1. Форкни https://github.com/flathub/flathub
2. Новая ветка `io.github.romaogon.zapusk`, положи туда `io.github.romaogon.zapusk.yml`
   и `flathub.json` не нужен.
3. Pull Request → боты прогонят тест-сборку → после апрува:
   `flatpak install flathub io.github.romaogon.zapusk`

## .deb (Debian/Ubuntu)

```bash
bash build_deb.sh
sudo apt install ./zapusk_2.9.2_all.deb
```

Для PPA нужен аккаунт на launchpad.net → «Create PPA» → `dput ppa:твой-ник/zapusk zapusk_2.9.2_source.changes`
(собирается через `dpkg-buildpackage -S` из того же дерева — попроси, распишу).
