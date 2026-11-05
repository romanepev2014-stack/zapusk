# SPDX-License-Identifier: GPL-3.0-or-later
import os, pathlib
from zapusk.core.util import which, run_detached, LOGS_DIR
from zapusk.core.prefix import prefix_path, wine_env

def build_command(game):
    """Собрать команду запуска: [gamemoderun] [mangohud] wine game.exe args"""
    exe = game["exe"]
    args = game.get("args", "")
    # EN: Java games (Minecraft etc.) run natively — no wine needed.
    # RU: Java-игры (Minecraft и т.д.) идут нативно — wine не нужен.
    if exe.lower().endswith(".jar"):
        return ["java", "-jar", exe] + (args.split() if args else [])
    # EN: console ROMs — through the emulator layer, no wine.
    # RU: консольные образы — через эмуляторный слой, без wine.
    if pathlib.Path(exe).suffix.lower() in (".iso", ".img", ".chd", ".cso", ".pbp", ".pkg", ".xex", ".xbe"):
        return None  # launch() handles consoles separately
    cmd = []
    if game.get("gamemode", True) and which("gamemoderun"):
        cmd.append("gamemoderun")
    mh = game.get("mangohud", "")
    if mh is True:
        mh = "fps"
    if mh and which("mangohud"):
        cmd.append("mangohud")
    if game.get("virtual_desktop"):
        w, h = game["virtual_desktop"].split("x")
        cmd += ["wine", "explorer", f"/desktop=game,{w}x{h}", exe]
    else:
        cmd += ["wine", exe]
    if args:
        cmd += args.split()
    return cmd

def build_env(game, prefix, extra_env=None):
    env = wine_env(prefix, debug=game.get("debug", False))
    if game.get("dxvk_hud"):
        env["DXVK_HUD"] = "compiler,fps"
    env["DXVK_STATE_CACHE"] = "1"
    if game.get("fsync", True):
        env["WINEFSYNC"] = "1"
    if game.get("esync", True):
        env["WINEESYNC"] = "1"
    if game.get("large_address", False):
        env["WINE_LARGE_ADDRESS_AWARE"] = "1"
    if extra_env:
        env.update(extra_env)
    return env

def launch(game, extra_env=None, want_pid=False):
    slug = game.get("slug") or game["name"]
    log = LOGS_DIR / f"{slug}.log"
    cmd = build_command(game)
    if game["exe"].lower().endswith(".jar"):
        # EN: native java — plain env / RU: нативная java — обычное окружение
        env = dict(os.environ)
        if extra_env:
            env.update(extra_env)
        p = run_detached(cmd, env=env, cwd=game.get("workdir") or None, log=str(log))
        return (log, p.pid) if want_pid else log
    if pathlib.Path(game["exe"]).suffix.lower() in (".iso", ".img", ".chd", ".cso", ".pbp", ".pkg", ".xex", ".xbe"):
        from zapusk.core import consoles
        cmd, env = consoles.build_console_command(game, extra_env)
        if game.get("gamemode", True) and which("gamemoderun"):
            cmd = ["gamemoderun"] + cmd
        p = run_detached(cmd, env=env, cwd=game.get("workdir") or None, log=str(log))
        return (log, p.pid) if want_pid else log
    prefix = prefix_path(slug, game.get("shared_prefix", False))
    env = build_env(game, prefix, extra_env)
    p = run_detached(cmd, env=env, cwd=game.get("workdir") or None, log=str(log))
    return (log, p.pid) if want_pid else log
