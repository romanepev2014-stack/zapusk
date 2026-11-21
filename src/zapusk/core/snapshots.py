# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: prefix Time Machine — snapshot before risky changes, one-click rollback.
RU: машина времени префикса — снапшот перед рискованными действиями, откат в клик."""

import shutil
import time

from zapusk.core.util import DATA_DIR

SNAPS = DATA_DIR / "snapshots"
KEEP = 3


def _snapdir(slug):
    d = SNAPS / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def snapshot_prefix(game, progress=None):
    """EN: copy the game's prefix into a timestamped snapshot, prune old ones.
    RU: копия префикса игры в снапшот с меткой времени, старые чистятся."""
    from zapusk.core.prefix import prefix_path

    src = prefix_path(game["slug"], game.get("shared_prefix", False))
    if not src.exists():
        return None
    ts = time.strftime("%Y%m%d-%H%M%S")
    dst = _snapdir(game["slug"]) / ts
    if progress:
        progress(f"📸 снапшот префикса -> {dst.name}")
    try:
        shutil.copytree(src, dst)
    except OSError as e:
        if progress:
            progress(f"⚠ снапшот не сделан: {e}")
        return None
    snaps = sorted(p for p in _snapdir(game["slug"]).iterdir() if p.is_dir())
    for old in snaps[:-KEEP]:
        shutil.rmtree(old, ignore_errors=True)
    return dst


def list_snapshots(game):
    d = _snapdir(game["slug"])
    if not d.exists():
        return []
    return sorted((p.name for p in d.iterdir() if p.is_dir()), reverse=True)


def rollback(game, snap_name=None, progress=None):
    """EN: restore prefix from a snapshot (latest by default). RU: откат префикса из снапшота."""
    from zapusk.core.prefix import prefix_path

    snaps = list_snapshots(game)
    if not snaps:
        return False, "снапшотов нет"
    snap_name = snap_name or snaps[0]
    src = _snapdir(game["slug"]) / snap_name
    dst = prefix_path(game["slug"], game.get("shared_prefix", False))
    if progress:
        progress(f"⏪ откат префикса к {snap_name}")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)
    return True, snap_name
