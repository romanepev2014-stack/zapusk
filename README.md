# 🎮 ZAPUSK — run any Windows game on Arch Linux with one click

**Download → launch → drag an .exe in → play.** No terminals, no prefix wizardry.

Zapusk is a launcher that **installs the whole stack for you** (Wine, DXVK, VKD3D-Proton,
Vulkan drivers, gamemode) and **configures every game automatically**: Windows dependencies
(vcrun, d3dx9, dotnet, fonts), Windows version, performance tweaks. You only point it at an .exe.

---

## 🌍 Zapusk 2.9 Global

- 🌐 **10 UI languages** — RU, EN, DE, FR, ES, PT, UK, PL, ZH, JA (selector in the title bar)
- 🎨 **4 color palettes** — Cyber, Matrix, Sunset, Sakura, each with light & dark modes
- 🐧 **Any distro** — Arch, Debian/Ubuntu, Fedora, openSUSE, Void, Alpine, Gentoo, **FreeBSD**: universal `install.sh` detects the package manager; DXVK auto-downloads if your repos lack it
- 🗑 **Remove games** right from the card — from the list, with files, with prefix
- ⚡ **Auto-config**: drop an exe in — dependencies install themselves

## 🚀 Usage (dead simple)

```bash
cd zapusk
python -m zapusk gui
```

Then everything happens in the window:

1. **⚙️ Setup → «🔧 Install everything»** — one time, enter your password.
   **Reboot afterwards** (required for Vulkan).
2. **Drag & drop an .exe or a game folder into the window.**
3. Press **«🚀 Fix & Launch»** on the game card.
   First run installs dependencies (10–20 min) — afterwards it's instant.

Done. Play.

## 🎯 Repacks, official copies, DRM-free releases (GOG), old games

All of them work: repacks, licensed installers, GOG builds. For GTA 5 pick the **gta5** preset — it sets up Rockstar Social Club.
If Social Club doesn't hook on first launch, run `Social-Club-Setup.exe` from the game
folder once via the «▶ Launch» button.

## 📦 What «Install everything» sets up

| Component | Purpose |
|---|---|
| `wine-staging` | run .exe (fresh, with fsync/esync) |
| `dxvk` | DirectX 9/10/11 → Vulkan (huge FPS boost) |
| `vkd3d-proton` | DirectX 12 → Vulkan |
| `lib32-*` drivers | **games silently fail without them** — the most common issue |
| `gamemode`, `mangohud` | performance & FPS overlay |

## ⚙️ Presets for any game

`gta5` · `dx12` · `dx11` · `dx9` · `unity` · `unreal` · `old` (XP era) · `launcher` (Epic etc.)

Not sure which one? Use `dx11` — it fits most games since ~2010.

## 🔧 If a game won't start

1. **⚙️ Setup → «🔎 Check system»** — everything must be ✅.
2. **📋 Logs** page — pick the game, read the last lines, look for `err:`.
3. In the game settings (⚙ on the card) try: disable Fsync, enable «Virtual desktop», change preset.
4. Paste the log into a GitHub Issue — we'll figure it out.

## ⚠️ Honest notes

- Anticheat-protected online games (Vanguard, EAC without Linux support) will **not** work
  outside official Steam. Single-player always works.
- Zapusk is not a new translator — it's the standard stack (Wine + DXVK + VKD3D), correctly
  assembled and fully automated. That's exactly why it actually works.

## 💻 For developers

- GUI: `zapusk/gui.py` (PySide6), logic: `zapusk/core/`, CLI: `python -m zapusk --help`.
- All code is commented in English and Russian.
- GPL-3.0 (copyleft: все версии остаются открытыми / all versions stay open source) — fork it, improve it.
## 📦 Install as an app (menu icon)

```bash
./install_app.sh        # ~/.local: icon + menu entry, no root
```
Or a native Arch package: run `makepkg -si` (PKGBUILD included) → `zapusk` in /usr/bin.

Or a single binary: `pip install pyinstaller && pyinstaller zapusk.spec` → `dist/zapusk`.
## ❓ Empty squares instead of icons?

Install symbol fonts:

```bash
sudo pacman -S ttf-nerd-fonts-symbols noto-fonts-emoji ttf-font-awesome
```

Tested on Arch Linux (snapshot 2026.2).
## 🎮 FreeBSD Gaming Mode (bhyve + GPU passthrough)

Run **heavy and online games** on FreeBSD at ~100% GPU speed: a Linux (Zen kernel) VM
gets your real video card via PCIe passthrough, and Looking Glass shows the game
picture in a window on your FreeBSD desktop.

```sh
sudo sh scripts/freebsd_gaming_mode.sh
```

The script checks IOMMU (VT-d/AMD-Vi), finds GPUs, configures `pptdevs` passthrough,
creates a ZFS zvol and generates a ready bhyve start script with an IVSHMEM region
for Looking Glass.

**Requirements:** FreeBSD 14+, CPU with VT-d/AMD-Vi (enabled in BIOS), a GPU for the
VM **plus any output for the host** (iGPU or a cheap card). Almost all anti-cheats
work inside the VM; Vanguard (Valorant) intentionally refuses VMs.

**Status:** untested on real hardware — you are the first tester. Logs → GitHub Issues.

Packages for everyone: Arch (PKGBUILD), Debian/Ubuntu (build_deb.sh), Flatpak (flatpak/) — see [FLATHUB.md](FLATHUB.md).

Publishing everywhere: [RELEASE.md](RELEASE.md) — pacman, deb, rpm, Flatpak, Snap, AppImage, Nix, Gentoo, Void, Alpine, FreeBSD.
