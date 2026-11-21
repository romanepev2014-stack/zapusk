# 🎮 ZAPUSK 3.2

**A game launcher for Linux & FreeBSD: drop a file in — Zapusk figures out what it is, installs everything and launches it.**

[![Release](https://img.shields.io/github/v/release/romanepev2014-stack/zapusk)](https://github.com/romanepev2014-stack/zapusk/releases)
[![License: GPL v3](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

Windows games, PlayStation/Xbox disc images, Java games — one library, one "Fix & Launch" click.

## 🎮 Console Mode — drop an ISO, we handle the rest

Zapusk reads **image signatures** (PS serials, Xbox magic bytes) and decides how to run the game:

| Platform | Emulator |
|---|---|
| PlayStation 1 | DuckStation |
| PlayStation 2 | PCSX2 |
| PlayStation 3 | RPCS3 (+ auto-install of Sony's official firmware) |
| **PlayStation 4** | **shadPS4** (experimental) |
| **PlayStation 5** | ⏳ no emulator exists — honestly. **Streaming from your own console via Chiaki** works (button in the app) |
| PSP | PPSSPP |
| Original Xbox | xemu |
| **Xbox 360** | **Xenia running through our own Wine prefix with DXVK** |

Emulators install themselves: package manager → flatpak → GitHub download. `zapusk consoles` shows the status of all platforms.

### 🪐 Project Prospero — honest PS5 groundwork

The PS5 is x86-64 AMD, same as your PC: it needs a compatibility layer (like Wine), not emulation. The wall: Sony encrypts binaries and no public keys exist. Already prepared (`src/zapusk/core/prospero.py`): PKG container parser, dump catalog by `PPSA` serials, a draft Orbis→Linux syscall translation table, Chiaki streaming. When the wall falls, Zapusk will adopt the layer in one evening.

## 🧨 Features 3.0–3.2

- 🔧 **Auto-heal** — game crashes → Zapusk reads the log, diagnoses (DXVK, vcrun, d3dx9, .NET, memory, fsync), fixes and relaunches — up to 4 attempts
- 📥 **Universal import** — Steam, Heroic, Lutris, Bottles, GOG in one click (Windows builds; native Linux Steam games play as-is)
- ⏪ **Prefix Time Machine** — snapshot before risky changes, one-click rollback
- 🔮 **Compat oracle** — warns before launching unfixable games (Vanguard, GFWL...)
- 💀 **Panic kill** — instantly terminates a frozen game
- 📊 **MSI Afterburner-style overlay** — FPS, frametime, CPU/GPU, RAM/VRAM (right Shift+F12)
- ⬆ **Self-update** — a button in settings downloads the latest binary from GitHub Releases

## 🐧 FreeBSD GPU Layer

`zapusk fbsdgpu` — an "individual FreeBSD for gaming": detects your GPU, installs **only its** driver, **removes the rest**, remembers the hardware — swap the card and the next run reconfigures everything. `--kernel` builds a tuned kernel. On FreeBSD games run on the host GPU (wine-devel + DXVK); passthrough is only needed for heavy/online titles.

## 🎨 7 themes

**Cyber** (neon city with traffic), **Matrix** (digital rain), **Sunset** (mountains at dusk), **Sakura** (blossoms falling), **Windows XP** (Bliss + working Start menu + playable Minesweeper with drawn flags and mines), **Windows 95** (working Start, chunky bevels), **Xbox 360** (boot screen: sphere rings, glow, bubbles). Each has dark & light modes, a liquid wave transition and cursor parallax.

## ⚡ Usage

1. Install Zapusk using one of the methods below
2. Run `zapusk` from your terminal or application menu
3. Drag an `.exe`, `.iso`, `.pkg` or a game folder into the window
4. Press **"Fix & Launch"** — everything else is automatic

## 📦 Install

| Method / System | Command |
|---|---|
| **Prebuilt binary (any Linux x86_64)** | Download `zapusk-linux-x86_64` from [Releases](https://github.com/romanepev2014-stack/zapusk/releases), then:<br>`chmod +x zapusk-linux-x86_64 && ./zapusk-linux-x86_64` |
| **Arch Linux / Manjaro (AUR / PKGBUILD)** | `git clone https://github.com/romanepev2014-stack/zapusk.git && cd zapusk/AUR && makepkg -si` |
| **Build & install to `~/.local/bin`** | `git clone https://github.com/romanepev2014-stack/zapusk.git && cd zapusk && uv sync && make install` |
| **Run from source (for development)** | `git clone https://github.com/romanepev2014-stack/zapusk.git && cd zapusk && uv sync && uv run zapusk gui` |
| **FreeBSD** | `pkg install wine-devel winetricks uv && uv sync && uv run zapusk fbsdgpu` |

To remove a local installation, run `make uninstall` inside the repository directory.

## 💻 CLI

```bash
zapusk gui                 # launch the graphical interface
zapusk doctor              # system diagnostics
zapusk import              # import from Steam/Heroic/Lutris/Bottles/GOG
zapusk consoles            # console emulator status
zapusk run "GTA5" --fix    # launch with auto-heal
zapusk kill "GTA5"         # panic kill
zapusk snapshot "GTA5"     # prefix snapshot
zapusk rollback "GTA5"     # prefix rollback
zapusk fbsdgpu [--kernel]  # FreeBSD: auto GPU drivers (+ kernel tuning)
zapusk update              # self-update
```

## ❓ Honest answers

- **Anti-cheats** (Vanguard, kernel-level EAC/BattlEye) — don't work anywhere outside the official Windows client; Zapusk warns upfront
- **PS5** — no emulator exists; the honest path (streaming from your console via Chiaki) is built in
- **Xbox One / Series** — no emulators
- Written by a 12-year-old developer with an AI assistant. **GPL-3.0**: code always open
