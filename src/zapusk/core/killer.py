# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: panic kill — terminate every process of a running game (wine/proton/exe).
RU: паник-килл — убить все процессы запущенной игры (wine/proton/exe)."""

import os
import pathlib
import signal


def kill_game(game, prefix=None):
    """EN: kill all processes belonging to the game. RU: убивает все процессы игры."""
    exe_name = pathlib.Path(game["exe"]).name.lower()
    target_prefix = str(prefix) if prefix else None
    killed = []
    for pid_s in os.listdir("/proc"):
        if not pid_s.isdigit():
            continue
        try:
            with open(f"/proc/{pid_s}/cmdline", "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode("utf-8", "replace").lower()
            with open(f"/proc/{pid_s}/environ", "rb") as f:
                env = f.read().decode("utf-8", "replace")
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        is_wine = ("wine" in cmd) or ("proton" in cmd) or ("WINEPREFIX" in env)
        if not is_wine:
            continue
        hit = (target_prefix and target_prefix in env) or (exe_name and exe_name in cmd)
        if hit:
            try:
                os.kill(int(pid_s), signal.SIGKILL)
                killed.append(int(pid_s))
            except (ProcessLookupError, PermissionError):
                pass
    return killed
