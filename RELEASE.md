# 🚀 Релиз Zapusk — во все репозитории

Собранные форматы: **pacman** (Arch), **deb** (Debian/Ubuntu), **rpm** (Fedora/openSUSE),
**Flatpak**, **Snap**, **AppImage**, **Nix**, **ebuild** (Gentoo), **APKBUILD** (Alpine),
**template** (Void), **FreeBSD port**.

## Сборка всех пакетов локально

| Команда | Результат |
|---|---|
| `bash build_package.sh` | pacman (.pkg.tar.zst) |
| `bash build_deb.sh` | Debian (.deb) |
| `bash build_rpm.sh` | Fedora/openSUSE (.rpm) |
| `bash build_appimage.sh` | универсальный .AppImage |
| `flatpak-builder ... flatpak/io.github.romaogon.zapusk.yml` | Flatpak |

## Публикация в репозитории

### AUR (Arch)
Регистрация откроется → `git clone ssh://aur@aur.archlinux.org/zapusk.git` →
положи `aur/PKGBUILD`, `makepkg --printsrcinfo > .SRCINFO` → commit + push.
Люди ставят: `yay -S zapusk`.

### Flathub (все дистрибутивы)
Форк https://github.com/flathub/flathub → ветка `io.github.romaogon.zapusk` →
добавь `flatpak/io.github.romaogon.zapusk.yml` → Pull Request → жди апрува ботов.
Люди ставят: `flatpak install flathub io.github.romaogon.zapusk`.

### Snap Store (Ubuntu и все)
`snapcraft login` → `cd snap && snapcraft upload zapusk_*.snap --release=stable`.
Нужен классический snap (wine на хосте) — при регистрации запроси classic confinement.

### PPA (Ubuntu)
launchpad.net → Create PPA → `dpkg-buildpackage -S` из deb-дерева →
`dput ppa:твой-ник/zapusk ../zapusk_2.9.2_source.changes`.

### COPR (Fedora)
copr.fedorainfracloud.org → New Project → загрузи `rpm/zapusk.spec` как SCM/inline build.
Люди ставят: `dnf copr enable твой-ник/zapusk && dnf install zapusk`.

### Nixpkgs
Форк NixOS/nixpkgs → добавь `pkgs/by-name/za/zapusk/package.nix` из flake → PR.
Люди ставят: `nix profile install nixpkgs#zapusk`.

### Gentoo (GURU overlay)
ПР в guru с ebuild → `eselect repository enable guru && emerge games-util/zapusk`.

### FreeBSD Ports
ПР в freebsd-ports с `freebsd-port/` → люди ставят `pkg install zapusk`.

### Void, Alpine
ПР с `void/template` в void-packages; APKBUILD — в aports (требует мейнтейнерства).

## Порядок действий
1. GitHub Release (tag `v2.9.2`)
2. AUR + Flathub — первые две (покрывают 90% пользователей)
3. Reddit: r/archlinux, r/linux_gaming, r/freebsd
4. Остальные по мере сил
