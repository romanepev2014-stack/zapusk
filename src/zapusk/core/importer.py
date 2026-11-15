# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: universal game import — scan Steam, Heroic, Lutris, Bottles, GOG, itch
and plain folders; detect presets; skip games already in the library.
RU: универсальный импорт — Steam, Heroic, Lutris, Bottles, GOG, itch и просто
папки; автоопределение пресетов; без дублей."""

import json
import os
import pathlib
import re
import sqlite3

from zapusk.core import library
from zapusk.core.detect import detect_preset


def _exes(folder):
    """EN: best-guess main exe/jar of a game folder. RU: главный exe/jar папки игры."""
    try:
        files = [
            p
            for p in pathlib.Path(folder).iterdir()
            if p.suffix.lower() in (".exe", ".jar") and p.is_file()
        ]
    except OSError:
        return None
    if not files:
        files = [p for p in pathlib.Path(folder).glob("*/*.exe")]
    if not files:
        return None
    return str(max(files, key=lambda p: p.stat().st_size))


def _add(found, name, exe, preset, source):
    if not exe or not os.path.exists(exe):
        return
    if library.get(name):
        return
    found.append(dict(name=name, exe=exe, preset=preset, source=source))


def from_steam(found, home, progress=None):
    roots = [
        home / ".steam/steam",
        home / ".local/share/Steam",
        home / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
    ]
    scanned = 0
    wins = 0
    for root in roots:
        apps = root / "steamapps"
        if not apps.exists():
            continue
        lf = apps / "libraryfolders.vdf"
        paths = [root]
        try:
            for m in re.finditer(r'"path"\s+"([^"]+)"', lf.read_text(errors="replace")):
                paths.append(pathlib.Path(m.group(1).replace("\\\\", "/")))
        except OSError:
            pass
        for base in paths:
            common = base / "steamapps/common"
            if not common.is_dir():
                continue
            for game_dir in sorted(common.iterdir()):
                if not game_dir.is_dir() or "Proton" in game_dir.name:
                    continue
                scanned += 1
                exe = _exes(game_dir)
                if exe:
                    wins += 1
                    _add(
                        found,
                        game_dir.name,
                        exe,
                        detect_preset(exe, game_dir.name)[0],
                        "Steam",
                    )
    if progress:
        progress(f"   папок игр в common: {scanned}, windows-версий (exe): {wins}")
        if scanned and not wins:
            progress(
                "   → у тебя Linux-версии игр, они и так нативные. Zapusk импортирует Windows-игры:"
            )
            progress(
                "     включи в Steam: Свойства игры → Совместимость → Принудительно Proton"
            )


def from_heroic(found, home):
    for cfg in [
        home / ".config/heroic/installed.json",
        home / ".var/app/com.heroicgameslauncher.hgl/config/heroic/installed.json",
    ]:
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for store in ("installed", "legendary", "gog"):
            for app, info in (data.get(store) or {}).items():
                if not isinstance(info, dict):
                    continue
                folder = info.get("install_path") or info.get("installPath")
                if not folder:
                    continue
                exe = info.get("executable") or _exes(folder)
                name = info.get("title") or pathlib.Path(str(folder)).name
                if exe and os.path.exists(str(exe)):
                    _add(
                        found,
                        str(name),
                        str(exe),
                        detect_preset(str(exe), str(name))[0],
                        "Heroic",
                    )


def from_lutris(found, home):
    db = home / ".local/share/lutris/pga.db"
    if not db.exists():
        return
    try:
        con = sqlite3.connect(str(db))
        for name, directory in con.execute(
            "SELECT name, directory FROM games WHERE directory IS NOT NULL"
        ):
            if directory:
                exe = _exes(directory)
                if exe:
                    _add(found, name, exe, detect_preset(exe, name)[0], "Lutris")
        con.close()
    except sqlite3.Error:
        pass


def from_bottles(found, home):
    base = home / ".local/share/bottles/bottles"
    if not base.is_dir():
        return
    for yml in base.glob("*/*.yml"):
        try:
            txt = yml.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in re.finditer(r"name:\s*(.+)\n(?:.*\n)*?\s*path:\s*(.+\.exe)", txt):
            name, exe = m.group(1).strip().strip("'\""), m.group(2).strip().strip("'\"")
            if os.path.exists(exe):
                _add(found, name, exe, detect_preset(exe, name)[0], "Bottles")


def from_gog(found, home):
    for base in [home / "GOG Games", home / "Games/GOG"]:
        if base.is_dir():
            for d in sorted(base.iterdir()):
                if d.is_dir():
                    exe = _exes(d)
                    if exe:
                        _add(found, d.name, exe, detect_preset(exe, d.name)[0], "GOG")


def from_folders(found, folders):
    for f in folders:
        exe = _exes(f)
        if exe:
            name = pathlib.Path(f).name
            _add(found, name, exe, detect_preset(exe, name)[0], "Папка")


SOURCES = [
    ("steam", from_steam),
    ("heroic", from_heroic),
    ("lutris", from_lutris),
    ("bottles", from_bottles),
    ("gog", from_gog),
]


def _wrap(fn):
    def w(found, home, progress=None):
        if fn.__code__.co_argcount >= 3:
            fn(found, home, progress)
        else:
            fn(found, home)

    return w


def scan(only=None, folders=None, progress=None):
    """EN: -> list of found games. RU: -> список найденных игр."""
    home = pathlib.Path.home()
    found = []
    for key, fn in SOURCES:
        if only and key not in only:
            continue
        if progress:
            progress(f"🔍 {key} ...")
        before = len(found)
        try:
            _wrap(fn)(found, home, progress)
        except Exception as e:
            if progress:
                progress(f"⚠ {key}: {e}")
        if progress:
            progress(f"   {key}: +{len(found) - before}")
    if folders:
        if progress:
            progress("🔍 папки ...")
        from_folders(found, folders)
    return found


def import_all(found, progress=None):
    """EN: add found games to the library. RU: добавить найденное в библиотеку."""
    added = 0
    for g in found:
        try:
            library.add(g["name"], g["exe"], g["preset"], shared_prefix=False)
            added += 1
            if progress:
                progress(f"✅ {g['name']}  [{g['source']}]")
        except ValueError:
            pass
        except Exception as e:
            if progress:
                progress(f"⚠ {g['name']}: {e}")
    return added
