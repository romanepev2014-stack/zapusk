# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: Auto-heal — detect a game crash, read its log, apply a matching fix,
restart, repeat until the game runs. No other launcher does this.
RU: Авто-лечение — поймать вылет, прочитать лог, применить нужный фикс,
перезапустить, повторять, пока игра не заведётся. Больше ни у кого такого нет."""

import os
import pathlib
import re
import time

from zapusk.core import library, runner
from zapusk.core.prefix import prefix_path, winetricks_install

# EN: log signature -> (fix key, human description). Order matters.
# RU: подпись в логе -> (ключ фикса, описание). Порядок важен.
RULES = [
    (r"d3dx9", "d3dx9", "d3dx9 (DirectX 9 библиотеки)"),
    (
        r"VCRUNTIME|MSVCP|vcruntime|msvcp",
        "vcrun2019",
        "Visual C++ 2015-2022 (vcrun2019)",
    ),
    (r"\.NET Framework|mscoree|Microsoft\.NET|CLR", "dotnet48", ".NET Framework 4.8"),
    (r"XAudio|xact|xaudio", "xact", "XAudio/Xact (звук)"),
    (
        r"DXVK.*(fail|error)|failed to create.*[Vv]ulkan|vkCreate.*fail",
        "dxvk",
        "проблема DXVK/Vulkan",
    ),
    (
        r"out of memory|Out Of Memory|не хватает памяти",
        "laa",
        "нехватка памяти (Large Address Aware)",
    ),
]


def pick_fix(log_tail, applied):
    """EN: find first matching not-yet-applied fix. RU: первый подходящий невыполненный фикс."""
    for pat, key, desc in RULES:
        if key in applied:
            continue
        if re.search(pat, log_tail, re.IGNORECASE):
            return key, desc
    # EN: generic fallbacks. RU: запасные универсальные фики
    for key, desc in (
        ("fsync", "fsync (подозрение на падения futex2)"),
        ("wined3d", "откат DXVK на встроенный DirectX Wine (wined3d)"),
    ):
        if key not in applied:
            return key, desc
    return None, None


def apply_fix(key, game, progress=None):
    """EN: apply one fix to the game's prefix/settings. RU: применить один фикс."""

    def say(m):
        if progress:
            progress(m)

    slug = game["slug"]
    prefix = prefix_path(slug, game.get("shared_prefix", False))
    if key in ("d3dx9", "vcrun2019", "dotnet48", "xact"):
        say(f"   ⬇ winetricks {key} ...")
        winetricks_install(prefix, [key])
    elif key == "dxvk":
        from zapusk.core import prefix as P

        say("   🧊 переустановка DXVK ...")
        P.install_dxvk(prefix)
    elif key == "wined3d":
        from zapusk.core import prefix as P

        say("   🍷 откат на wined3d (DXVK выключен для этой игры)")
        P.uninstall_dxvk(prefix)
        library.update(game["name"], {"_dxvk_off": True})
    elif key == "laa":
        say("   🧠 включаю Large Address Aware (2 ГБ -> 4 ГБ для 32-бит)")
        library.update(game["name"], {"large_address": True})
    elif key == "fsync":
        say("   🔀 отключаю fsync для этой игры")
        library.update(game["name"], {"fsync": False})


def _wait_alive(pid, timeout, progress=None):
    """EN: True if the process is still alive after `timeout` seconds.
    RU: True, если процесс жив через timeout секунд."""
    t = 0
    while t < timeout:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        time.sleep(2)
        t += 2
        if progress and t % 10 == 0:
            progress(f"   ... жду {t}/{timeout} сек")
    return True


def run_with_autofix(game, timeout=90, tries=4, progress=None):
    """EN: launch -> monitor -> on crash read log -> fix -> relaunch. Returns (ok, applied fixes).
    RU: запуск -> наблюдение -> при вылете читает лог -> чинит -> перезапускает."""

    def say(m):
        if progress:
            progress(m)

    applied = []
    for attempt in range(1, tries + 1):
        say(f"▶ Попытка {attempt}/{tries}: запускаю '{game['name']}'")
        res = runner.launch(game, want_pid=True)
        lp, pid = res if isinstance(res, tuple) else (res, None)
        if pid is None:
            say("❌ Не удалось запустить процесс")
            return False, applied
        if _wait_alive(pid, timeout, progress=say):
            say(f"✅ Игра '{game['name']}' работает! (попытка {attempt})")
            return True, applied
        say(f"💀 Процесс умер через <{timeout} сек — читаю лог")
        try:
            tail = "\n".join(
                pathlib.Path(lp)
                .read_text(encoding="utf-8", errors="replace")
                .splitlines()[-80:]
            )
        except OSError:
            tail = ""
        key, desc = pick_fix(tail, applied)
        if not key:
            say(
                "❌ В логе не нашёл знакомых ошибок — автолечение остановлено. Скинь лог разработчику."
            )
            return False, applied
        say(f"🔧 Определил проблему: {desc}")
        if not applied:
            from zapusk.core import snapshots

            snapshots.snapshot_prefix(game, progress=say)
        applied.append(key)
        try:
            apply_fix(key, game, progress=say)
        except Exception as e:
            say(f"⚠ Фикс '{key}' не применился: {e}")
    say(f"❌ Исчерпаны попытки ({tries}). Последние строки лога:\n{tail[-600:]}")
    return False, applied
