# SPDX-License-Identifier: GPL-3.0-or-later
import os, shutil, pathlib
from zapusk.core.util import run, which, DEFAULT_PREFIX, PREFIXES_DIR

def prefix_path(slug: str, shared: bool):
    if shared:
        DEFAULT_PREFIX.mkdir(parents=True, exist_ok=True)
        return DEFAULT_PREFIX
    p = PREFIXES_DIR / slug
    p.mkdir(parents=True, exist_ok=True)
    return p

def wine_env(prefix: pathlib.Path, extra=None, debug=False):
    env = os.environ.copy()
    env["WINEPREFIX"] = str(prefix)
    env["WINEDEBUG"] = "" if debug else "-all"
    env["WINEESYNC"] = "1"
    env["WINEFSYNC"] = "1"
    if extra:
        env.update({k: v for k, v in extra.items() if v is not None})
    return env

def wineboot(prefix: pathlib.Path, log=None):
    if not which("wine"):
        raise RuntimeError("wine не установлен. Запусти install_arch.sh")
    run(["wineboot", "-u"], env=wine_env(prefix), log=log)

def set_winver(prefix: pathlib.Path, winver: str, log=None):
    if winver:
        run(["winecfg", "-v", winver], env=wine_env(prefix), log=log)

def reg_add(prefix: pathlib.Path, key: str, value: str, data: str, log=None):
    run(["wine", "reg", "add", key, "/v", value, "/d", data, "/f"],
        env=wine_env(prefix), log=log)

def _local_dxvk():
    """EN: find or download DXVK (for distros without a dxvk package).
       RU: ищем или скачиваем DXVK (для дистрибутивов без пакета dxvk)."""
    d = DATA_DIR / "dxvk"
    if (d / "x64").exists():
        return d
    from zapusk.core import runners
    try:
        tag = runners.latest_dxvk()               # e.g. "v2.4.1"
        ver = tag.lstrip("v")
        tmp = DATA_DIR / "dxvk.tar.gz"
        runners.download_file(f"https://github.com/doitsujin/dxvk/releases/download/{tag}/dxvk-{ver}.tar.gz", tmp, None)
        import tarfile
        with tarfile.open(tmp, "r:gz") as tf:
            try:
                tf.extractall(DATA_DIR, filter="data")
            except TypeError:
                tf.extractall(DATA_DIR)
        tmp.unlink(missing_ok=True)
        hits = sorted(pathlib.Path(DATA_DIR).glob("dxvk-*"), key=lambda p: p.stat().st_mtime)
        for h in hits:
            if (h / "x64").exists() and h.name != "dxvk":
                h.rename(d)
                break
        return d if (d / "x64").exists() else None
    except Exception:
        return None


def install_dxvk(prefix: pathlib.Path, log=None):
    """Ставим DXVK: системный пакет, скачанный билд или ручное копирование dll."""
    setup = "/usr/share/dxvk/setup_dxvk.sh"
    if os.path.exists(setup):
        run(["bash", setup, "install"], env=wine_env(prefix), log=log)
        return True
    # EN: downloaded DXVK fallback / RU: запасной путь — скачанный DXVK
    src = pathlib.Path("/usr/share/dxvk")
    if not src.exists():
        src = _local_dxvk()
    if src is None or not src.exists():
        return False
    pfx = prefix / "drive_c/windows"
    for sub, win_dir in (("x64", "system32"), ("x32", "syswow64")):
        for dll in (src / sub).glob("*.dll"):
            shutil.copy2(dll, pfx / win_dir / dll.name)
    for dll in ("dxgi", "d3d11", "d3d10core", "d3d10", "d3d10_1", "d3d9"):
        reg_add(prefix, "HKCU\\Software\\Wine\\DllOverrides", dll, "native", log)
    return True

def uninstall_dxvk(prefix: pathlib.Path, log=None):
    setup = "/usr/share/dxvk/setup_dxvk.sh"
    if os.path.exists(setup):
        run(["bash", setup, "uninstall"], env=wine_env(prefix), log=log)

def install_vkd3d(prefix: pathlib.Path, log=None):
    setup = "/usr/share/vkd3d-proton/setup_vkd3d_proton.sh"
    if os.path.exists(setup):
        run(["bash", setup, "install"], env=wine_env(prefix), log=log)
        return True
    src = pathlib.Path("/usr/share/vkd3d-proton")
    if not src.exists():
        return False
    pfx = prefix / "drive_c/windows"
    for sub, win_dir in (("x64", "system32"), ("x32", "syswow64")):
        for dll in (src / sub).glob("*.dll"):
            shutil.copy2(dll, pfx / win_dir / dll.name)
    reg_add(prefix, "HKCU\\Software\\Wine\\DllOverrides", "d3d12", "native", log)
    reg_add(prefix, "HKCU\\Software\\Wine\\DllOverrides", "d3d12core", "native", log)
    return True

def open_prefix(prefix: pathlib.Path):
    for fm in ("dolphin", "nautilus", "thunar", "pcmanfm", "xdg-open"):
        if which(fm):
            run([fm, str(prefix)])
            return
