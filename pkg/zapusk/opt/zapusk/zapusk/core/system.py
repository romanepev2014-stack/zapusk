# SPDX-License-Identifier: GPL-3.0-or-later
import os, subprocess, shutil
from zapusk.core.util import which, run

CHECKS = []

def check(name, ok, fix, critical=True):
    CHECKS.append((name, ok, fix, critical))
    return ok

def doctor():
    """Полная диагностика. Возвращает текстовый отчёт."""
    global CHECKS
    CHECKS = []
    lines = []

    def add(name, ok, fix):
        mark = "✅" if ok else "❌"
        lines.append(f"{mark} {name}")
        if not ok and fix:
            lines.append(f"    └─ чинить: {fix}")

    # --- Wine ---
    add("wine (staging)", bool(which("wine")), "sudo pacman -S wine-staging")
    if which("wine"):
        rc, out = run(["wine", "--version"])
        lines.append(f"    └─ {out.strip()}")

    # --- Winetricks ---
    add("winetricks", bool(which("winetricks")), "sudo pacman -S winetricks")

    # --- Vulkan ---
    add("vulkaninfo", bool(which("vulkaninfo")), "sudo pacman -S vulkan-tools")
    vk_ok = False
    if which("vulkaninfo"):
        rc, out = run(["vulkaninfo", "--summary"])
        vk_ok = rc == 0
        if vk_ok:
            for l in out.splitlines():
                if "deviceName" in l:
                    lines.append(f"    └─ {l.strip()}"); break
        add("Vulkan работает", vk_ok, "проверь драйвер GPU и перезагрузись")

    # --- 32-bit Vulkan (самая частая причина 'молча не стартует') ---
    lib32 = None
    try:
        if shutil.which("pacman"):
            ld = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True).stdout
            lib32 = ("libvulkan.so" in ld and ("i386" in ld or "lib32" in ld)) or \
                    bool(shutil.which("/usr/lib32/libvulkan.so.1"))
        elif shutil.which("dpkg"):
            out = subprocess.run(["dpkg", "--print-foreign-architectures"],
                                 capture_output=True, text=True).stdout
            lib32 = "i386" in out
        elif shutil.which("pkg"):   # FreeBSD
            lib32 = True
    except Exception:
        pass
    if lib32 is True:
        add("32-bit Vulkan (lib32)", True, "")
    elif lib32 is False:
        add("32-bit Vulkan (lib32)", False,
            "pacman: sudo pacman -S lib32-vulkan-icd-loader (+ lib32 GPU driver) | apt: sudo dpkg --add-architecture i386 && sudo apt install mesa-vulkan-drivers:i386")

    # --- DXVK / VKD3D ---
    add("DXVK (dxvk)", os.path.exists("/usr/share/dxvk"), "sudo pacman -S dxvk (или yay -S dxvk-bin)")
    add("VKD3D-Proton", os.path.exists("/usr/share/vkd3d-proton"), "sudo pacman -S vkd3d-proton")

    # --- Опционально ---
    add("gamemode (опционально)", bool(which("gamemoderun")), "sudo pacman -S gamemode lib32-gamemode", )
    add("mangohud (опционально)", bool(which("mangohud")), "sudo pacman -S mangohud lib32-mangohud")

    # --- Fsync ---
    fsync = False
    try:
        with open("/proc/kallsyms") as f:
            fsync = "futex2" in f.read(2_000_000)
    except Exception:
        pass
    add("ядро с futex2 (fsync)", fsync, "kernel 5.16+ (у Arch по умолчанию — ок)")

    return "\n".join(lines)
