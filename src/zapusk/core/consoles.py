# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: Console Mode — detect PlayStation / Xbox images, auto-install the right
emulator, configure and launch. Like Wine layer, but for consoles.
RU: Консольный режим — определение образов PlayStation / Xbox, автоустановка
эмулятора, настройка и запуск. Как слой Wine, только для консолей."""

import os
import pathlib
import re
import subprocess
import urllib.request

from zapusk.core import distro as _distro
from zapusk.core.util import DATA_DIR, host_prefix, which

# ============================================================
# EN: platform signatures — magic bytes / strings in the image.
# RU: сигнатуры платформ — магические байты и строки в образе.
# ============================================================
ROM_EXTS = (".iso", ".img", ".chd", ".cso", ".pbp", ".pkg", ".xex", ".xbe", ".rvz")
FW_URLS = [
    "https://dus01.ps3.update.playstation.net/update/ps3/image/us/2024/PS3UPDAT.PUP",
    "https://www.playstation.com/en-us/support/hardware/ps3/system-software/",
]


def _read_chunks(path, sizes=(65536, 4 * 1024 * 1024, 32 * 1024 * 1024)):
    """EN: yield file head with growing size. RU: отдаёт начало файла нарастающими кусками."""
    try:
        sz = os.path.getsize(path)
    except OSError:
        return
    with open(path, "rb") as f:
        for s in sizes:
            if s >= sz:
                f.seek(0)
                yield f.read(sz)
                return
            f.seek(0)
            yield f.read(s)


def _find(data, needle):
    return data.find(needle) != -1


def detect_rom(path):
    """EN: -> (platform_key, serial) or (None, None).
    RU: -> (ключ платформы, серийник) или (None, None)."""
    p = str(path)
    ext = pathlib.Path(p).suffix.lower()
    try:
        head = b""
        for chunk in _read_chunks(p):
            head = chunk
            # PSN pkg: PS5 (PPSAxxxxx), PS4 (CUSAxxxxx) или PS3
            if ext == ".pkg" and head[:4] == b"\x7fPKG":
                m5 = re.search(rb"PPSA[0-9]{5}", head)
                if m5:
                    return "ps5", m5.group(1).decode()
                m4 = re.search(rb"CUSA[0-9]{5}", head)
                if m4:
                    return "ps4", m4.group(1).decode()
                return "ps3", None
            # PSP eboot
            if ext == ".pbp" and head[:4] == b"\x00PBP":
                return "psp", None
            # Xbox executable
            if ext == ".xbe" and head[:4] == b"XBEH":
                return "xbox", None
            # Xbox 360 executable
            if ext == ".xex" and head[:4] == b"XEX2":
                return "x360", None
            # PS3 disc image
            if _find(head, b"PS3_DISC.SFB"):
                return "ps3", None
            # PSP UMD image
            if _find(head, b"PSP_GAME"):
                return "psp", None
            # Xbox 360 disc (XEX on disc somewhere in first 32MB)
            if _find(head, b"XEX2"):
                return "x360", None
            # original Xbox disc (XDVDFS, no ISO9660)
            if not _find(head[32769:32774], b"CD001") and _find(head, b"XBOX"):
                return "xbox", None
            # ISO9660 discs: PS2 before PS1 (PS2 discs also say PLAYSTATION)
            if _find(head[32769:32774], b"CD001") or _find(head, b"CD001"):
                m = re.search(rb"(S[CL][EU][SP][SM]_[0-9]{3}\.[0-9]{2})", head)
                serial = m.group(1).decode() if m else None
                if _find(head, b"PS2") or serial or _find(head, b"BOOT2"):
                    return "ps2", serial
                if _find(head, b"PLAYSTATION"):
                    return "ps1", serial
    except OSError:
        pass
    return None, None


# ============================================================
# EN: emulators registry. pm = packages per package manager,
#     flatpak = ref, dl = (repo, asset suffix) for GitHub download.
# RU: реестр эмуляторов: pm — пакеты, flatpak — реф, dl — скачивание с GitHub.
# ============================================================
PLATFORMS = {
    "ps1": dict(
        name="PlayStation 1",
        emu="DuckStation",
        pm={"pacman": ["duckstation-qt"], "apt": ["duckstation"]},
        flatpak="org.duckstation.DuckStation",
        launch=lambda rom: (
            (
                [
                    which("duckstation-qt") or which("duckstation") or "flatpak",
                    "run",
                    "org.duckstation.DuckStation",
                ]
                if not which("duckstation-qt") and not which("duckstation")
                else [which("duckstation-qt") or which("duckstation")]
            )
            + ["-fullscreen", rom]
        ),
    ),
    "ps2": dict(
        name="PlayStation 2",
        emu="PCSX2",
        pm={"pacman": ["pcsx2"], "apt": ["pcsx2"], "dnf": ["pcsx2"]},
        flatpak="net.pcsx2.PCSX2",
        launch=lambda rom: (
            (
                [
                    which("pcsx2-qt") or which("pcsx2") or "flatpak",
                    "run",
                    "net.pcsx2.PCSX2",
                ]
                if not which("pcsx2-qt") and not which("pcsx2")
                else [which("pcsx2-qt") or which("pcsx2")]
            )
            + ["-batch", "-fullscreen", rom]
        ),
    ),
    "ps3": dict(
        name="PlayStation 3",
        emu="RPCS3",
        needs_fw=True,
        pm={"pacman": ["rpcs3"], "apt": ["rpcs3"]},
        flatpak="net.rpcs3.RPCS3",
        launch=lambda rom: (
            (
                [which("rpcs3") or "flatpak", "run", "net.rpcs3.RPCS3"]
                if not which("rpcs3")
                else [which("rpcs3")]
            )
            + ["--no-gui", rom]
        ),
    ),
    "psp": dict(
        name="PSP",
        emu="PPSSPP",
        pm={"pacman": ["ppsspp"], "apt": ["ppsspp"], "dnf": ["ppsspp"]},
        flatpak="org.ppsspp.PPSSPP",
        launch=lambda rom: (
            (
                [
                    which("ppsspp-qt") or which("PPSSPPSDL") or "flatpak",
                    "run",
                    "org.ppsspp.PPSSPP",
                ]
                if not which("ppsspp-qt") and not which("PPSSPPSDL")
                else [which("ppsspp-qt") or which("PPSSPPSDL")]
            )
            + [rom]
        ),
    ),
    "xbox": dict(
        name="Original Xbox",
        emu="xemu",
        pm={},
        flatpak="app.xemu.xemu",
        dl=("xemu-project/xemu", "-x86_64.AppImage"),
        launch=lambda rom: (
            (
                [which("xemu") or "flatpak", "run", "app.xemu.xemu"]
                if not which("xemu")
                else [which("xemu")]
            )
            + ["-dvd_path", rom]
        ),
    ),
    "ps4": dict(
        name="PlayStation 4",
        emu="shadPS4",
        needs_fw=True,
        pm={"pacman": ["shadps4-git"]},
        flatpak="net.shadps4.shadPS4",
        dl=("shadPS4/shadPS4", ("-linux.zip", "-linux-x86_64.zip", "-linux.AppImage")),
        launch=lambda rom: (
            (
                [which("shadps4") or "flatpak", "run", "net.shadps4.shadPS4"]
                if not which("shadps4")
                else [which("shadps4")]
            )
            + [rom]
        ),
    ),
    "ps5": dict(name="PlayStation 5", emu="Chiaki (стрим)", stream=True, launch=None),
    "x360": dict(
        name="Xbox 360",
        emu="Xenia (via Wine + DXVK)",
        wine=True,
        pm={},
        flatpak=None,
        dl=("xenia-canary/xenia-canary", "-windows.zip"),
        launch=None,
    ),  # особый путь — через wine-префикс
}

XENIA_DIR = DATA_DIR / "xenia"


def emu_binary(platform):
    """EN: -> path to emulator binary or None. RU: -> путь к эмулятору или None."""
    cfg = PLATFORMS[platform]
    if cfg.get("wine"):
        exe = XENIA_DIR / "xenia_canary.exe"
        return str(exe) if exe.exists() else None
    for c in [cfg["launch"](__file__)] if False else []:
        pass
    # проверяем бинарники напрямую
    names = {
        "ps1": ["duckstation-qt", "duckstation"],
        "ps2": ["pcsx2-qt", "pcsx2"],
        "ps3": ["rpcs3"],
        "psp": ["ppsspp-qt", "PPSSPPSDL", "ppsspp"],
        "xbox": ["xemu"],
    }
    for n in names.get(platform, []):
        if which(n):
            return which(n)
    if cfg.get("flatpak") and which("flatpak"):
        r = subprocess.run(["flatpak", "info", cfg["flatpak"]], capture_output=True)
        if r.returncode == 0:
            return "flatpak:" + cfg["flatpak"]
    if platform == "xbox" and cfg.get("dl"):
        ai = list(pathlib.Path.home().glob("Downloads/xemu*.AppImage"))
        if ai:
            return str(ai[-1])
    return None


def install_emulator(platform, progress=print):
    """EN: try package manager, then flatpak, then direct download.
    RU: пакетный менеджер -> flatpak -> прямое скачивание."""
    cfg = PLATFORMS[platform]
    name = _distro.detect()[1]
    pm = cfg.get("pm", {}).get(name)
    if pm:
        progress(f"📦 ставлю {', '.join(pm)} через {name}...")
        cmd = _distro.pm_install_cmd(name, pm)
        if cmd:
            r = subprocess.run(host_prefix() + cmd)
            if r.returncode == 0 and emu_binary(platform):
                return True, "installed via package manager"
    if cfg.get("flatpak") and which("flatpak"):
        progress(f"📦 ставлю через flatpak: {cfg['flatpak']}")
        r = subprocess.run(
            host_prefix() + ["flatpak", "install", "-y", "flathub", cfg["flatpak"]]
        )
        if r.returncode == 0 and emu_binary(platform):
            return True, "installed via flatpak"
    if cfg.get("dl"):
        ok, msg = _download_emulator(platform, progress)
        if ok:
            return True, msg
    return False, (
        f"не удалось автоматически поставить {cfg['emu']}. "
        f"Установи вручную: {cfg.get('flatpak') or cfg.get('pm', {}).get(name) or cfg['dl'][0]}"
    )


def _download_emulator(platform, progress):
    """EN: fetch latest GitHub release asset. RU: качаем последний релиз с GitHub."""
    repo, suffix = PLATFORMS[platform]["dl"]
    suffixes = suffix if isinstance(suffix, (list, tuple)) else (suffix,)
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/releases/latest",
            headers={"User-Agent": "zapusk"},
        )
        import json

        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode())
        asset = next(
            (
                a
                for a in d.get("assets", [])
                if any(a["name"].endswith(sf) for sf in suffixes)
                and "mac" not in a["name"].lower()
                and "windows" not in a["name"].lower()
            ),
            None,
        )
        if not asset:
            return False, "asset не найден в релизе"
        dest_dir = (
            XENIA_DIR
            if PLATFORMS[platform].get("wine")
            else pathlib.Path.home() / "Downloads"
        )
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / asset["name"]
        progress(
            f"⬇ скачиваю {asset['name']} ({asset.get('size', 0) // 1048576} МБ)..."
        )
        urllib.request.urlretrieve(asset["browser_download_url"], dest)
        if dest.suffix == ".zip":
            import zipfile as zf

            with zf.ZipFile(dest) as z:
                z.extractall(dest_dir)
            dest.unlink()
        if dest.name.endswith(".AppImage"):
            dest.chmod(0o755)
        return True, f"скачано в {dest_dir}"
    except Exception as e:
        return False, str(e)


# ============================================================
# EN: Xenia runs through our own Wine prefix with DXVK — DXVK on
#     top of the console layer, exactly like you asked.
# RU: Xenia идёт через наш префикс Wine с DXVK — прослойка на прослойке.
# ============================================================
def setup_xenia(progress=print):
    """EN: prepare wine prefix + xenia for Xbox 360. RU: префикс Wine + Xenia."""
    from zapusk.core.prefix import (
        install_dxvk,
        prefix_path,
        wineboot,
        winetricks_install,
    )

    if emu_binary("x360"):
        return True, "xenia готов"
    progress("🍷 создаю префикс Wine для Xenia...")
    prefix = prefix_path("xenia", True)
    wineboot(prefix, progress and (lambda m: None))
    progress("⬇ качаю Xenia Canary...")
    ok, msg = _download_emulator("x360", progress)
    if not ok:
        return False, msg
    progress("🧊 ставлю DXVK + vcrun в префикс...")
    try:
        winetricks_install(prefix, ["vcrun2019", "d3dcompiler_47"])
        install_dxvk(prefix)
    except Exception as e:
        progress(f"⚠ зависимости wine: {e}")
    return emu_binary("x360") is not None, "xenia готов" if emu_binary(
        "x360"
    ) else "xenia не найдена после установки"


def build_console_command(game, extra_env=None):
    """EN: -> (cmd, env) to launch a console game. RU: -> (команда, окружение)."""
    rom = game["exe"]
    platform, serial = detect_rom(rom)
    env = dict(os.environ)
    env.pop("WINEPREFIX", None)
    if game.get("mangohud") and which("mangohud"):
        env["MANGOHUD"] = "1"
    if extra_env:
        env.update(extra_env)
    if platform == "ps5":
        import json as _j

        host = None
        cfgp = DATA_DIR / "chiaki.json"
        if cfgp.exists():
            try:
                host = _j.loads(cfgp.read_text()).get("host")
            except Exception:
                host = None
        if not host:
            return None, env
        if which("chiaki"):
            cmd = ["chiaki", "--host", host]
        elif which("flatpak"):
            cmd = ["flatpak", "run", "re.chiaki.Chiaki", "--host", host]
        else:
            return None, env
        return cmd, env
    if platform == "x360":
        prefix = prefix_path("xenia", True)
        env["WINEPREFIX"] = str(prefix)
        env["DXVK_STATE_CACHE"] = "1"
        exe = emu_binary("x360")
        cmd = [which("wine") or "wine", exe, rom]
        if game.get("mangohud") and which("mangohud"):
            cmd = ["mangohud"] + cmd
        return cmd, env
    cfg = PLATFORMS[platform]
    return cfg["launch"](rom), env


# ============================================================
# EN: RPCS3 firmware helpers. RU: прошивка RPCS3.
# ============================================================
def rpcs3_firmware_ok():
    """EN: True if PS3 firmware present. RU: True если прошивка PS3 установлена."""
    candidates = [
        pathlib.Path.home() / ".config/rpcs3/dev_flash",
        pathlib.Path.home() / ".var/app/net.rpcs3.RPCS3/config/rpcs3/dev_flash",
    ]
    return any(p.exists() for p in candidates)


def download_ps3_firmware(progress=print):
    """EN: try direct mirrors, else open the official Sony page. RU: зеркала или сайт Sony."""
    dest = pathlib.Path.home() / "Downloads/PS3UPDAT.PUP"
    for url in FW_URLS[:1]:
        try:
            progress(f"⬇ пробую {url}")
            urllib.request.urlretrieve(url, dest)
            if dest.stat().st_size > 100_000_000:
                progress(f"✅ прошивка скачана: {dest}")
                progress(
                    "Теперь: открой RPCS3 → File → Install Firmware → выбери этот файл"
                )
                return True, str(dest)
        except Exception:
            continue
    import webbrowser

    webbrowser.open(FW_URLS[-1])
    return (
        False,
        "открыл официальную страницу Sony — скачай PS3UPDAT.PUP и установи через RPCS3 (File → Install Firmware)",
    )


def stream_ps5(host=None, progress=print):
    """EN: stream from a real PS5 via Chiaki. RU: стрим с реальной PS5 через Chiaki."""
    import json

    cfg = DATA_DIR / "chiaki.json"
    if not host and cfg.exists():
        try:
            host = json.loads(cfg.read_text()).get("host")
        except Exception:
            host = None
    if not host:
        return False, "укажи IP консоли: настройки Zapusk или chiaki.json"
    if which("chiaki"):
        cmd = ["chiaki"]
    elif which("flatpak"):
        cmd = ["flatpak", "run", "re.chiaki.Chiaki"]
    else:
        progress("📦 ставлю Chiaki...")
        r = subprocess.run(
            host_prefix() + ["flatpak", "install", "-y", "flathub", "re.chiaki.Chiaki"]
        )
        if r.returncode != 0:
            return False, "не удалось установить Chiaki (flatpak)"
        cmd = ["flatpak", "run", "re.chiaki.Chiaki"]
    cmd += ["--host", host]
    subprocess.Popen(cmd)
    return True, f"стрим с {host}"


def platform_status():
    """EN: -> {platform: (emu_state, note)}. RU: -> статус по платформам."""
    out = {}
    for key, cfg in PLATFORMS.items():
        if cfg.get("stream"):
            ok = bool(which("chiaki") or which("flatpak"))
            out[key] = (
                cfg["name"],
                "📺 стрим через Chiaki" if ok else "❌ нужен flatpak",
                "играет с твоей реальной PS5 по сети" if ok else "",
            )
            continue
        b = emu_binary(key)
        if b:
            state = f"✅ {b.split('/')[-1]}"
        else:
            state = "❌ не установлен"
        note = ""
        if key == "ps3" and b:
            note = "прошивка ✅" if rpcs3_firmware_ok() else "⚠ нужна прошивка PS3"
        if key == "ps4" and b:
            note = "экспериментально: часть библиотеки работает"
        out[key] = (cfg["name"], state, note)
    return out
