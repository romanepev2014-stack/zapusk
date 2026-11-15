# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: distro/PM detection — Linux + FreeBSD. RU: определение дистрибутива и пакетного менеджера."""
import platform, shutil


def detect():
    """EN: -> (distro_name, pm) — pm in pacman|apt|dnf|zypper|emerge|apk|xbps|pkg|None.
       RU: -> (дистрибутив, пакетный менеджер) или (name, None) если неизвестен."""
    if platform.system() == "FreeBSD":
        return ("freebsd", "pkg")
    info = {}
    try:
        for line in open("/etc/os-release"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                info[k] = v.strip('"')
    except OSError:
        return ("unknown", None)
    did = (info.get("ID") or "").lower()
    like = (info.get("ID_LIKE") or "").lower()
    name = info.get("NAME") or did or "linux"
    for fam, pm in (("arch", "pacman"), ("debian", "apt"), ("ubuntu", "apt"),
                    ("fedora", "dnf"), ("rhel", "dnf"), ("opensuse", "zypper"),
                    ("gentoo", "emerge"), ("alpine", "apk"), ("void", "xbps")):
        if fam in did or fam in like:
            return (name, pm)
    return (name, None)


def pm_install_cmd(pm, pkgs):
    """EN: -> command list to install packages. RU: -> команда установки пакетов."""
    if pm == "pacman":
        return ["sudo", "pacman", "-S", "--needed", "--noconfirm"] + pkgs
    if pm == "apt":
        return ["sudo", "apt", "install", "-y"] + pkgs
    if pm == "dnf":
        return ["sudo", "dnf", "install", "-y"] + pkgs
    if pm == "zypper":
        return ["sudo", "zypper", "install", "-y"] + pkgs
    if pm == "apk":
        return ["sudo", "apk", "add"] + pkgs
    if pm == "xbps":
        return ["sudo", "xbps-install", "-Sy"] + pkgs
    if pm == "pkg":
        return ["sudo", "pkg", "install", "-y"] + pkgs
    return None


# EN: package names per distro family / RU: имена пакетов по семействам
PKGS = {
    "pacman": ["wine-staging", "winetricks", "vulkan-icd-loader", "lib32-vulkan-icd-loader",
               "vulkan-tools", "gamemode", "lib32-gamemode", "mangohud", "lib32-mangohud",
               "curl", "jq", "cabextract", "unzip", "p7zip"],
    "apt": ["wine64", "wine32:i386", "winetricks", "vulkan-tools", "gamemode",
            "mangohud", "curl", "jq", "cabextract", "unzip", "p7zip-full"],
    "dnf": ["wine", "winetricks", "vulkan-tools", "gamemode", "mangohud",
            "curl", "jq", "cabextract", "unzip", "p7zip"],
    "zypper": ["wine", "winetricks", "vulkan-tools", "gamemode", "mangohud",
               "curl", "jq", "cabextract", "unzip", "p7zip"],
    "apk": ["wine", "winetricks", "vulkan-tools", "curl", "unzip"],
    "xbps": ["wine", "winetricks", "vulkan-tools", "gamemode", "curl", "unzip"],
    "pkg": ["wine-devel", "winetricks", "vulkan-tools", "curl", "jq", "unzip"],
    "emerge": ["app-emulation/wine-staging", "app-emulation/winetricks", "curl", "unzip"],
}


def gpu_packages(pm, gpu):
    """EN: GPU driver packages. RU: пакеты драйверов GPU."""
    m = {
        ("pacman", "nvidia"): ["nvidia-utils", "lib32-nvidia-utils"],
        ("pacman", "amd"): ["lib32-mesa", "vulkan-radeon", "lib32-vulkan-radeon"],
        ("pacman", "intel"): ["lib32-mesa", "vulkan-intel", "lib32-vulkan-intel"],
        ("apt", "nvidia"): ["nvidia-vulkan-icd"],
        ("apt", "amd"): ["mesa-vulkan-drivers", "mesa-vulkan-drivers:i386"],
        ("apt", "intel"): ["mesa-vulkan-drivers", "mesa-vulkan-drivers:i386"],
        ("dnf", "nvidia"): ["nvidia-driver"],
        ("dnf", "amd"): ["mesa-vulkan-drivers"],
        ("dnf", "intel"): ["mesa-vulkan-drivers"],
    }
    return m.get((pm, gpu), [])
