# SPDX-License-Identifier: GPL-3.0-or-later
"""
EN: self-update — check GitHub releases, download the right package for the
    detected distro, install via pkexec.
RU: самообновление — проверка релизов,
    скачивание пакета под дистрибутив, установка через pkexec.
"""

import json
import os
import pathlib
import shutil
import sys
import urllib.request

from zapusk import __version__

REPO = "romanepev2014-stack/zapusk"
ASSET_NAME = "zapusk-linux-x86_64"
UA = {"User-Agent": "zapusk-selfupdate"}

def _parse_version(tag: str) -> tuple[int, ...]:
    clean = tag.lstrip("v").split("-")[0]
    parts = []
    for part in clean.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _target_binary() -> pathlib.Path | None:
    """Return path to the installed binary if running as a compiled executable."""
    if not getattr(sys, "frozen", False) and "__compiled__" not in globals():
        which_bin = shutil.which("zapusk")
        if which_bin:
            return pathlib.Path(which_bin).resolve()
        return None
    return pathlib.Path(sys.executable).resolve()


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


def check() -> tuple[bool, str]:
    """EN: -> (newer: bool, info). RU: -> (есть ли новее, инфо)."""
    tag, assets = latest()
    if not tag or isinstance(assets, str):
        return False, f"не удалось проверить: {assets}"
    return _parse_version(tag) > _parse_version(__version__), tag


def download_and_install(progress=print) -> tuple[bool, str]:
    """EN: download the release binary and atomically replace the current one.
    RU: скачать релизный бинарник и атомарно заменить текущий."""
    tag, assets = latest()
    if not tag or isinstance(assets, str):
        return False, str(assets)

    url = assets.get(ASSET_NAME)
    if not url:
        return False, f"файл {ASSET_NAME} не найден в релизе {tag}"

    target = _target_binary()
    if not target:
        return False, "запуск из исходников: обновите репозиторий через git pull && uv sync"

    if str(target).startswith(("/usr/", "/opt/")):
        return (
            False,
            f"установлено системно ({target}): обновите через пакетный менеджер (AUR / makepkg)",
        )

    if not os.access(target.parent, os.W_OK):
        return False, f"нет прав на запись в {target.parent}"

    tmp_path = target.with_name(f"{target.name}.new")
    progress(f"⬇ скачиваю {ASSET_NAME} ({tag}) ...")

    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=300) as r, open(tmp_path, "wb") as f:
            shutil.copyfileobj(r, f)

        tmp_path.chmod(0o755)
        os.replace(tmp_path, target)
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        return False, f"ошибка обновления: {e}"

    progress(f"✅ обновлено до {tag}! Перезапусти Zapusk.")
    return True, "ok"
