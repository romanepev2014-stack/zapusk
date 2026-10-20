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
    cmd = []
    if game.get("gamemode", True) and which("gamemoderun"):
        cmd.append("gamemoderun")
    if game.get("mangohud", False) and which("mangohud"):
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

def launch(game, extra_env=None):
    slug = game.get("slug") or game["name"]
    log = LOGS_DIR / f"{slug}.log"
    cmd = build_command(game)
    if game["exe"].lower().endswith(".jar"):
        # EN: native java — plain env / RU: нативная java — обычное окружение
        env = dict(os.environ)
        if extra_env:
            env.update(extra_env)
        run_detached(cmd, env=env, cwd=game.get("workdir") or None, log=str(log))
        return log
    prefix = prefix_path(slug, game.get("shared_prefix", False))
    env = build_env(game, prefix, extra_env)
    run_detached(cmd, env=env, cwd=game.get("workdir") or None, log=str(log))
    return log
