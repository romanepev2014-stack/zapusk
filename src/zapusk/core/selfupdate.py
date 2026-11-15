# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: self-update — check GitHub releases, download the right package for the
detected distro, install via pkexec. RU: самообновление — проверка релизов,
скачивание пакета под дистрибутив, установка через pkexec."""

import json
import pathlib
import subprocess
import urllib.request

from zapusk import __version__
from zapusk.core import distro as _distro

REPO = "romanepev2014-stack/zapusk"
UA = {"User-Agent": "zapusk-selfupdate"}


def latest():
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode())
        return d["tag_name"], {
            a["name"]: a["browser_download_url"] for a in d.get("assets", [])
        }
    except Exception as e:
        return None, str(e)


def check():
    """EN: -> (newer: bool, info). RU: -> (есть ли новее, инфо)."""
    tag, assets = latest()
    if not tag:
        return False, f"не удалось проверить: {assets}"
    return tag.lstrip("v") > __version__, tag


def download_and_install(progress=print):
    """EN: fetch the right package for this distro and install it. RU: скачать и установить."""
    import shutil as _sh

    tag, assets = latest()
    if not tag:
        return False, assets
    _, pm = _distro.detect()
    if pm == "pacman":
        pref = ".pkg.tar.zst"
    elif pm == "apt":
        pref = "_all.deb"
    elif pm in ("dnf", "zypper"):
        pref = ".noarch.rpm"
    else:
        pref = ".AppImage"
    pick = next((n for n in assets if n.endswith(pref)), None)
    if not pick:
        pick = next((n for n in assets if n.endswith(".AppImage")), None)
    if not pick:
        return False, "подходящий пакет не найден в релизе"
    url = assets[pick]
    dest = pathlib.Path.home() / "Downloads" / pick
    progress(f"⬇ скачиваю {pick} ...")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        _sh.copyfileobj(r, f)
    if pick.endswith(".AppImage"):
        dest.chmod(0o755)
        subprocess.Popen([str(dest)])
        return True, f"AppImage запущен: {dest}"
    if pick.endswith(".pkg.tar.zst"):
        cmd = ["pkexec", "pacman", "-U", "--noconfirm", str(dest)]
    elif pick.endswith(".deb"):
        cmd = ["pkexec", "apt", "install", "-y", str(dest)]
    elif pick.endswith(".rpm"):
        cmd = ["pkexec", "dnf", "install", "-y", str(dest)]
    else:
        return False, "не знаю как установить"
    progress("📦 установка (введи пароль) ...")
    rc = subprocess.run(cmd).returncode
    if rc == 0:
        progress("✅ обновлено! Перезапусти Zapusk.")
        return True, "ok"
    return False, f"установка не удалась (код {rc})"
