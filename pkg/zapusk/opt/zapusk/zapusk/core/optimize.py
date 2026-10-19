"""EN: System optimization helpers (governor, swappiness, shader caches, gamemode).
RU: Оптимизация системы (губернатор CPU, swappiness, кэши шейдеров, gamemode)."""
# SPDX-License-Identifier: GPL-3.0-or-later
import os, glob, subprocess, shutil


def governor_get():
    """EN: current CPU governor. RU: текущий губернатор CPU."""
    try:
        return open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor").read().strip()
    except OSError:
        return None


def governor_set_performance():
    """EN: set performance governor (needs root via pkexec outside). RU: performance-губернатор."""
    cmd = ("for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; "
           "do echo performance > $c; done")
    return subprocess.run(["pkexec", "sh", "-c", cmd]).returncode == 0


def swappiness_get():
    try:
        return open("/proc/sys/vm/swappiness").read().strip()
    except OSError:
        return None


def swappiness_set(v: int = 10):
    """EN: lower swappiness -> less stutter in games. RU: меньше свопа -> меньше фризов."""
    return subprocess.run(["pkexec", "sysctl", f"vm.swappiness={v}"]).returncode == 0


def gamemode_active():
    """EN: is gamemoded user service running. RU: работает ли gamemoded."""
    if not shutil.which("gamemoded"):
        return False
    r = subprocess.run(["systemctl", "--user", "is-active", "gamemoded"],
                       capture_output=True, text=True)
    return r.stdout.strip() == "active"


def gamemode_enable():
    subprocess.run(["systemctl", "--user", "enable", "--now", "gamemoded"])
    return gamemode_active()


def clear_shader_cache():
    """EN: clear DXVK/Mesa shader caches. RU: чистим кэши шейдеров DXVK/Mesa."""
    removed = 0
    patterns = [
        os.path.expanduser("~/.cache/dxvk*"),
        os.path.expanduser("~/.cache/mesa_shader_cache*"),
        os.path.expanduser("~/.cache/radv_builtin_shaders*"),
        os.path.expanduser("~/.local/share/Steam/steamapps/shadercache/*"),
    ]
    for pat in patterns:
        for p in glob.glob(pat):
            subprocess.run(["rm", "-rf", p])
            removed += 1
    return removed


def vulkan_driver():
    """EN: first GPU device name from vulkaninfo. RU: имя GPU из vulkaninfo."""
    if not shutil.which("vulkaninfo"):
        return None
    r = subprocess.run(["vulkaninfo", "--summary"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if "deviceName" in line:
            return line.split("=")[-1].strip()
    return None
