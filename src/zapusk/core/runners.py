"""EN: Download & version-check runners (GE-Proton, DXVK, VKD3D).
RU: Скачивание и проверка версий раннеров (GE-Proton, DXVK, VKD3D)."""
# SPDX-License-Identifier: GPL-3.0-or-later
import os, re, json, glob, shutil, tarfile, urllib.request, pathlib, subprocess
from zapusk.core.util import DATA_DIR

GE_DIR = DATA_DIR / "runners"
UA = {"User-Agent": "zapusk-launcher"}


def _gh_latest(repo: str):
    """EN: latest release info via curl (fallback: urllib).
       RU: инфо о последнем релизе — через curl (запасной путь: urllib)."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    if shutil.which("curl"):   # EN: curl handles proxies/SSL better / RU: curl лучше дружит с сетью
        r = subprocess.run(["curl", "-fsSL", "--max-time", "25", url],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip().startswith("{"):
            return json.loads(r.stdout)
        raise RuntimeError(f"GitHub API не отвечает / API unreachable (curl code {r.returncode}): {r.stderr.strip()[:200]}")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def latest_ge_proton():
    """EN: -> (tag, tarball_url, size). RU: -> (тег, ссылка, размер)."""
    d = _gh_latest("GloriousEggroll/proton-ge-custom")
    tag = d["tag_name"]
    for a in d.get("assets", []):
        if a["name"].endswith(".tar.xz"):
            return tag, a["browser_download_url"], a.get("size", 0)
    return tag, f"https://github.com/GloriousEggroll/proton-ge-custom/releases/download/{tag}/{tag}.tar.xz", 0


def installed_ge():
    """EN: -> installed GE-Proton tag or None (own dir + Steam dirs).
       RU: -> установленный GE или None (своя папка + папки Steam)."""
    places = [GE_DIR,
              pathlib.Path.home() / ".local/share/Steam/compatibilitytools.d",
              pathlib.Path.home() / ".steam/root/compatibilitytools.d"]
    hits = []
    for pl in places:
        hits += glob.glob(str(pl / "GE-Proton*"))
    return pathlib.Path(sorted(hits)[-1]).name if hits else None


def protonup_install(emit=print):
    """EN: install GE-Proton via protonup CLI if present. RU: ставим GE через protonup, если есть."""
    import shutil as _sh
    if not _sh.which("protonup"):
        return False, "protonup не установлен / not installed (yay -S protonup)"
    emit("Ставлю через protonup / Installing via protonup…")
    pr = subprocess.run(["protonup"], capture_output=True, text=True)
    out = (pr.stdout or "") + (pr.stderr or "")
    if pr.returncode == 0:
        return True, out.strip().splitlines()[-1] if out.strip() else "ok"
    return False, out.strip()[-300:]


def download_file(url: str, dest: pathlib.Path, progress=None):
    """EN: download via curl with live percent (fallback: urllib).
       RU: скачивание через curl с процентами (запасной путь: urllib)."""
    if shutil.which("curl"):
        proc = subprocess.Popen(
            ["curl", "-fSL", "--retry", "2", "--connect-timeout", "15",
             "--progress-bar", "-o", str(dest), url],
            stderr=subprocess.PIPE, text=True, bufsize=1)
        tail = []
        for line in proc.stderr:
            line = line.strip()
            tail.append(line)
            tail = tail[-5:]
            if progress and line.endswith("%"):
                try:
                    pct = float(line.split()[-1].rstrip("%"))
                    progress(int(pct), 100)
                except ValueError:
                    pass
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"скачивание оборвалось / download failed (curl {proc.returncode}): {' | '.join(tail)}")
        if not dest.exists() or dest.stat().st_size < 1_000_000:
            raise RuntimeError("файл скачался битым / file too small, download corrupted")
        if progress:
            progress(100, 100)
        return
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if progress:
                progress(done, total)


def install_ge(tarpath: pathlib.Path, progress=None):
    """EN: extract GE-Proton safely. RU: распаковка GE-Proton с защитой и fallback."""
    GE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        tf = tarfile.open(tarpath, mode="r:xz")
    except Exception as e:
        raise RuntimeError(f"архив битый / broken tarball: {e}")
    with tf:
        members = tf.getmembers()
        n = max(len(members), 1)
        for i, m in enumerate(members):
            # EN: filter="data" needs py3.12+; fall back on older.
            # RU: filter="data" — с Python 3.12; для старше — fallback.
            try:
                tf.extract(m, GE_DIR, filter="data")
            except TypeError:
                tf.extract(m, GE_DIR)
            if progress and i % 50 == 0:
                progress(i, n)
    # EN: sanity check — the folder must contain a "proton" binary.
    # RU: проверка — в папке должен быть бинарник "proton".
    name = tarpath.stem.replace(".tar", "")
    if not (GE_DIR / name / "proton").exists() and not list(GE_DIR.glob("GE-Proton*/proton")):
        raise RuntimeError("в архиве не найден proton / no 'proton' binary in archive")


def pacman_ver(pkg: str):
    """EN: installed pacman package version. RU: версия пакета pacman."""
    try:
        out = subprocess.run(["pacman", "-Q", pkg], capture_output=True, text=True).stdout.strip()
        return out.split()[-1] if out else None
    except Exception:
        return None


def latest_dxvk():
    """EN: -> latest DXVK tag. RU: -> последний тег DXVK."""
    return _gh_latest("doitsujin/dxvk")["tag_name"]


def latest_vkd3d():
    """EN: -> latest VKD3D-Proton tag. RU: -> последний тег VKD3D-Proton."""
    return _gh_latest("HansKristian-Work/vkd3d-proton")["tag_name"]
