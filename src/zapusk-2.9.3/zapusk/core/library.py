# SPDX-License-Identifier: GPL-3.0-or-later
import json, os, pathlib
from zapusk.core.util import LIBRARY_FILE, ensure_dirs, slugify

def load():
    ensure_dirs()
    if LIBRARY_FILE.exists():
        try:
            return json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"games": []}
    return {"games": []}

def save(data):
    ensure_dirs()
    LIBRARY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def games():
    return load().get("games", [])

def get(name):
    for g in games():
        if g["name"] == name:
            return g
    return None

def add(name, exe, preset, shared_prefix=True, args="", workdir=""):
    data = load()
    if any(g["name"] == name for g in data["games"]):
        raise ValueError(f"Игра '{name}' уже есть в библиотеке")
    g = {
        "name": name, "slug": slugify(name), "exe": exe,
        "preset": preset, "shared_prefix": shared_prefix,
        "args": args, "workdir": workdir or str(pathlib.Path(exe).parent),
        "gamemode": True, "mangohud": False, "fsync": True, "esync": True,
        "dxvk_hud": False, "large_address": False, "debug": False,
        "virtual_desktop": "",
    }
    data["games"].append(g)
    save(data)
    return g

def update(name, fields):
    data = load()
    for g in data["games"]:
        if g["name"] == name:
            g.update(fields)
            save(data)
            return g
    raise KeyError(name)

def remove(name):
    data = load()
    data["games"] = [g for g in data["games"] if g["name"] != name]
    save(data)

def scan_folder(folder):
    """Найти подозрительно игровые .exe в папке (рекурсивно, без system32)."""
    found = []
    skip = ("unins", "setup", "installer", "redist", "vcredist", "directx", "dotnet",
            "socialclub", "activate", "crash", "report", "updater", "patch")
    for p in list(pathlib.Path(folder).rglob("*.exe")) + list(pathlib.Path(folder).rglob("*.jar")):
        pl = str(p).lower()
        if any(s in pl for s in ("windows/", "system32", "syswow64", "_commonredist", "__installer")):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        name_l = p.name.lower()
        score = size  # большой exe = вероятнее всего игра
        if any(s in name_l for s in skip):
            score = -1
        if score > 0:
            found.append((score, str(p)))
    found.sort(reverse=True)
    return [p for _, p in found[:20]]
