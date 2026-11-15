# 🎮 ZAPUSK 3.2

**Лаунчер игр для Linux и FreeBSD: кинул файл — Zapusk сам поймёт, что это, сам всё поставит и запустит.**

[![Release](https://img.shields.io/github/v/release/romanepev2014-stack/zapusk)](https://github.com/romanepev2014-stack/zapusk/releases)
[![License: GPL v3](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

> [!NOTE]
> If you need a translation of the README.md file, use this [link](https://github-com.translate.goog/romanepev2014-stack/zapusk/blob/main/README.md?_x_tr_sl=auto&_x_tr_tl=ru&_x_tr_hl=ru&_x_tr_pto=wapp),
> or the [English version](./README-EN.md).

Windows-игры, консольные образы PS/Xbox, Java-игры — одна библиотека, один клик «Починить и запустить».

## 🎮 Console Mode — кинь ISO, всё остальное наши проблемы

Zapusk читает **сигнатуры образов** (серийники PS, магические байты Xbox) и сам решает, как запустить игру:

| Платформа | Чем запускаем |
|---|---|
| PlayStation 1 | DuckStation |
| PlayStation 2 | PCSX2 |
| PlayStation 3 | RPCS3 (+ автоустановка официальной прошивки с Sony) |
| **PlayStation 4** | **shadPS4** (экспериментально) |
| **PlayStation 5** | ⏳ эмулятора не существует — честно. Работает **стриминг с вашей консоли через Chiaki** (кнопка «📺 Стрим с PS5») |
| PSP | PPSSPP |
| Xbox (original) | xemu |
| **Xbox 360** | **Xenia, запущенная через собственный префикс Wine с DXVK** |

Эмулятор ставится сам: пакетный менеджер → flatpak → скачивание с GitHub. `zapusk consoles` показывает статус всех платформ.

### 🪐 Project Prospero — честный фундамент PS5

PS5 — это x86-64 AMD, как ваш ПК: нужна прослойка (как Wine), а не эмуляция. Стена — Sony шифрует бинарники, публичных ключей нет. Что уже готово (`src/zapusk/core/prospero.py`): парсер PKG-контейнеров, каталог дампов по серийникам `PPSA`, черновик таблицы трансляции сисколов Orbis→Linux, Chiaki-стриминг. Когда стена падёт — Zapusk подхватит прослойку за один вечер.

## 🧨 Фичи 3.0–3.2

- 🔧 **Авто-лечение** — игра вылетела → Zapusk читает лог, определяет причину (DXVK, vcrun, d3dx9, .NET, память, fsync), чинит и перезапускает до 4 попыток
- 📥 **Импорт из всех магазинов** — Steam, Heroic, Lutris, Bottles, GOG одной кнопкой (Windows-версии; нативные Linux-игры Steam импортировать не нужно — они и так играют)
- ⏪ **Машина времени префикса** — снапшот перед рискованными действиями, откат в один клик
- 🔮 **Оракул совместимости** — предупреждает до запуска об играх, которые не заведутся (Vanguard, GFWL и т.д.)
- 💀 **Паник-килл** — мгновенно убивает зависшую игру целиком
- 📊 **Оверлей как MSI Afterburner** — FPS, фреймтайм, CPU/GPU, RAM/VRAM (правая Shift+F12)
- ⬆ **Самообновление** — кнопка в настройках скачивает свежий бинарник из GitHub Releases

## 🐧 FreeBSD GPU Layer

`zapusk fbsdgpu` — «индивидуальная FreeBSD для игр»: определяет вашу видеокарту, ставит **только её** драйвер, **удаляет ненужные**, запоминает железо — поменяли карту, следующий запуск всё перенастроит. Флаг `--kernel` собирает тюнингованное ядро. Игры на FreeBSD идут через обычную видеокарту (wine-devel + DXVK); проброс нужен только для тяжёлых/онлайн-игр.

## 🎨 7 тем оформления

**Cyber** (неоновый город с трафиком), **Matrix** (цифровой дождь), **Sunset** (закат в горах), **Sakura** (сакуры с лепестками), **Windows XP** (Блисс + рабочий Пуск + играбельный Сапёр с нарисованными флажками и минами), **Windows 95** (рабочий Пуск, бевелы), **Xbox 360** (стартовый экран: кольца сферы, свечение, пузыри). У каждой — тёмный и светлый режим, смена жидкой волной, параллакс за курсором.

## ⚡ Как пользоваться

1. Установите Zapusk любым удобным способом (таблица ниже)
2. Запустите `zapusk` из терминала или меню приложений
3. Перетащите в окно `.exe`, `.iso`, `.pkg` или папку с игрой
4. Нажмите «Починить и запустить» — всё остальное автоматически

## 📦 Установка

| Способ / Система | Команда |
|---|---|
| **Готовый бинарник (любой Linux x86_64)** | Скачайте `zapusk-linux-x86_64` из [Releases](https://github.com/romanepev2014-stack/zapusk/releases), затем:<br>`chmod +x zapusk-linux-x86_64 && ./zapusk-linux-x86_64` |
| **Arch Linux / Manjaro (AUR / PKGBUILD)** | `git clone https://github.com/romanepev2014-stack/zapusk.git && cd zapusk/AUR && makepkg -si` |
| **Сборка и установка в `~/.local/bin`** | `git clone https://github.com/romanepev2014-stack/zapusk.git && cd zapusk && uv sync && make install` |
| **Запуск из исходников (для разработки)** | `git clone https://github.com/romanepev2014-stack/zapusk.git && cd zapusk && uv sync && uv run zapusk gui` |
| **FreeBSD** | `pkg install wine-devel winetricks uv && uv sync && uv run zapusk fbsdgpu` |

Для удаления локальной установки выполните `make uninstall` в папке репозитория.

## 💻 CLI

```bash
zapusk gui                 # запуск графического интерфейса
zapusk doctor              # диагностика системы
zapusk import              # импорт игр из Steam/Heroic/Lutris/Bottles/GOG
zapusk consoles            # статус эмуляторов консолей
zapusk run "GTA5" --fix    # запуск с авто-лечением
zapusk kill "GTA5"         # паник-килл
zapusk snapshot "GTA5"     # снапшот префикса
zapusk rollback "GTA5"     # откат
zapusk fbsdgpu [--kernel]  # FreeBSD: авто-драйверы GPU (+ тюнинг ядра)
zapusk update              # самообновление
```

## ❓ Честные ответы

- **Античиты** (Vanguard, ядерные EAC/BattlEye) — не работают нигде вне официального Windows-клиента; Zapusk предупредит заранее
- **PS5** — эмулятора не существует; честный путь: стриминг со своей консоли (Chiaki) встроен
- **Xbox One / Series** — эмуляторов нет
- Проект написан 12-летним разработчиком при поддержке ИИ-ассистента. **GPL-3.0**: код всегда открыт
