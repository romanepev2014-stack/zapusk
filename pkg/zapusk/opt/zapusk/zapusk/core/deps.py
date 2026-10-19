# SPDX-License-Identifier: GPL-3.0-or-later
import os
from zapusk.core.util import run, which
from zapusk.core.prefix import wine_env

def winetricks_install(prefix, verbs, log=None):
    """Тихая установка winetricks-вербов в префикс."""
    if not which("winetricks"):
        raise RuntimeError("winetricks не найден. sudo pacman -S winetricks")
    verbs = [v for v in verbs if v]
    if not verbs:
        return 0, ""
    env = wine_env(prefix)
    # winetricks любит X, но -q всё равно лезет в GUI для некоторых вербов — глушим отладку
    return run(["winetricks", "-q"] + verbs, env=env, log=log)

def fix_game(prefix, preset_cfg, log=None, progress=None):
    """Полный 'замочи и запусти': dxvk (+vkd3d) + winver + verbs + твики реестра."""
    from zapusk.core.prefix import (wineboot, set_winver, install_dxvk,
                                    install_vkd3d, reg_add)
    def say(msg):
        if progress: progress(msg)
        if log:
            with open(log, 'a') as f: f.write(f"\n=== {msg} ===\n")

    say("Инициализация префикса (wineboot)")
    wineboot(prefix, log)

    say(f"Версия Windows: {preset_cfg.get('winver', 'win7')}")
    set_winver(prefix, preset_cfg.get("winver"), log)

    say("Установка DXVK (DX9/10/11 -> Vulkan)")
    install_dxvk(prefix, log)

    if preset_cfg.get("vkd3d"):
        say("Установка VKD3D-Proton (DX12 -> Vulkan)")
        install_vkd3d(prefix, log)

    verbs = preset_cfg.get("verbs", [])
    if verbs:
        say(f"Установка зависимостей: {', '.join(verbs)}  (это может занять время)")
        rc, out = winetricks_install(prefix, verbs, log)
        if rc != 0:
            say(f"⚠ winetricks завершился с кодом {rc} — смотри лог")

    # Полезные твики реестра
    reg_add(prefix, "HKCU\\Software\\Wine\\Direct3D", "UseGLSL", "disabled", log)  # dxvk сам ок, но для wined3d-фолбэка
    reg_add(prefix, "HKCU\\Control Panel\\Desktop", "LogPixels", "96", log)
    say("Готово. Играй: zapusk run <имя>")
    return True
