"""EN: Game auto-detection — PE import analysis + engine heuristics + offline DB.
RU: Автоопределение игры — анализ импортов PE-файла + эвристики движка + офлайн-база."""
# SPDX-License-Identifier: GPL-3.0-or-later
import os, struct, pathlib, json, urllib.request, urllib.parse


# ============================================================
# EN: tiny PE parser — read the import table (dll names).
# RU: минимальный парсер PE — читаем таблицу импортов (имена dll).
# ============================================================
def pe_info(exe_path: str):
    """EN: -> (machine, set_of_imported_dlls) or None on parse failure.
       RU: -> (архитектура, множество импортированных dll) или None при ошибке."""
    try:
        data = open(exe_path, "rb").read()
    except OSError:
        return None
    if len(data) < 0x1000 or data[:2] != b"MZ":
        return None
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_off:pe_off + 4] != b"PE\0\0":
        return None
    machine = struct.unpack_from("<H", data, pe_off + 4)[0]   # 0x14C=x86, 0x8664=x64
    opt_size = struct.unpack_from("<H", data, pe_off + 20)[0]
    opt_off = pe_off + 24
    magic = struct.unpack_from("<H", data, opt_off)[0]
    dd_off = opt_off + (96 if magic == 0x20B else 80)          # data directories
    imp_rva, imp_size = struct.unpack_from("<II", data, dd_off + 8)   # dir #1 = import
    nsec = struct.unpack_from("<H", data, pe_off + 6)[0]
    sec_off = opt_off + opt_size
    sections = []
    for i in range(nsec):
        off = sec_off + 40 * i
        name = data[off:off + 8].rstrip(b"\0").decode(errors="replace")
        vsize, vaddr, raw_size, raw_off = struct.unpack_from("<IIII", data, off + 8)
        sections.append((vaddr, max(vsize, raw_size), raw_off))

    def rva2off(rva):
        for vaddr, size, raw in sections:
            if vaddr <= rva < vaddr + size:
                return raw + (rva - vaddr)
        return None

    def read_str(off):
        if off is None or off >= len(data):
            return ""
        end = data.find(b"\0", off)
        return data[off:end].decode(errors="replace").lower()

    dlls = set()
    if imp_rva:
        pos = rva2off(imp_rva)
        while pos and pos + 20 <= len(data):
            desc = data[pos:pos + 20]
            original, _, _, _, name_rva = struct.unpack("<IIIII", desc)
            if original == 0 and name_rva == 0:
                break
            dlls.add(read_str(rva2off(name_rva)))
            pos += 20
    return ("x64" if machine == 0x8664 else "x86", dlls)


# ============================================================
# EN: offline knowledge base — popular games (ru/en name -> preset).
# RU: офлайн-база популярных игр (рус/англ имя -> пресет).
# ============================================================
GAME_DB = {
    "gta5": "gta5", "gta 5": "gta5", "grand theft auto v": "gta5", "гта 5": "gta5",
    "terraria": "dx9", "терария": "dx9",
    "cyberpunk": "dx12", "cyberpunk 2077": "dx12", "киберпанк": "dx12",
    "elden ring": "dx12", "эльден ринг": "dx12",
    "witcher 3": "dx11", "ведьмак 3": "dx11",
    "skyrim": "dx9", "скайрим": "dx9",
    "stardew valley": "old", "стардью валлей": "old",
    "hollow knight": "unity", "холлоу найт": "unity",
    "hades": "dx11", "хейдес": "dx11",
    "celeste": "old", "селеста": "old",
    "undertale": "old", "андертейл": "old",
    "hotline miami": "dx9", "хотлайн майами": "dx9",
    "red dead redemption 2": "dx12", "ред дед 2": "dx12",
    "baldur's gate 3": "dx11", "балдурс гейт 3": "dx11",
    "sekiro": "dx11", "секиро": "dx11",
    "doom eternal": "dx12", "doom 2016": "dx11",
    "metro exodus": "dx12", "метро исход": "dx12",
    "fallout 4": "dx11", "фоллаут 4": "dx11",
    "nvidia": "dx11",
}


def db_lookup(name: str):
    """EN: match game name against local DB. RU: ищем игру в локальной базе."""
    n = name.strip().lower()
    for key, preset in GAME_DB.items():
        if key in n:
            return preset
    return None


# ============================================================
# EN: online lookup via PCGamingWiki semantic API (best effort).
# RU: онлайн-поиск через API PCGamingWiki (если есть сеть).
# ============================================================
def web_lookup(name: str):
    """EN: -> (preset, info) or None. RU: -> (пресет, инфо) или None."""
    q = urllib.parse.quote(f"[[{name}]]|?Direct3D versions|?Engine")
    url = f"https://www.pcgamingwiki.com/w/api.php?action=ask&format=json&query={q}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "zapusk"})
        with urllib.request.urlopen(req, timeout=12) as r:
            res = json.loads(r.read().decode())
        results = res.get("query", {}).get("results", {})
        if not results:
            return None
        page = next(iter(results.values()))
        props = page.get("printouts", {})
        dx = str(props.get("Direct3D versions", ""))
        engine = str(props.get("Engine", ""))
        if "12" in dx:
            preset = "dx12"
        elif "11" in dx:
            preset = "dx11"
        elif "9" in dx:
            preset = "dx9"
        elif "8" in dx or "7" in dx:
            preset = "old"
        else:
            preset = None
        if "Unity" in engine and preset in (None, "dx11"):
            preset = "unity"
        if "Unreal" in engine and preset in (None, "dx11"):
            preset = "unreal"
        info = f"PCGamingWiki: Direct3D {dx or '?'} · {engine or 'engine ?'}"
        return preset, info
    except Exception:
        return None


# ============================================================
# EN: full detection — PE imports + folder heuristics.
# RU: полное определение — импорты exe + эвристики папки.
# ============================================================
def detect_preset(exe_path: str, game_name: str = ""):
    """EN: -> (preset, reason) — best guess for a game.
       RU: -> (пресет, причина) — лучшее предположение по игре."""
    exe_path = str(exe_path)
    if exe_path.lower().endswith(".jar"):
        return "java", "Java-архив — нативный запуск / native Java launch"
    folder = pathlib.Path(exe_path).parent
    info = pe_info(exe_path)
    arch, dlls = info if info else (None, set())
    dlls = dlls or set()

    # EN: engine hints from folder / RU: признаки движка по папке
    is_unity = (folder / "UnityPlayer.dll").exists() or (folder / "GameAssembly.dll").exists() \
               or any(folder.glob("*_Data/"))
    is_unreal = "-win64-shipping" in exe_path.lower() or (folder / "Engine").is_dir()

    # EN: DirectX from imports / RU: DirectX по импортам
    if any("d3d12" in d for d in dlls):
        return "dx12", f"exe импортирует d3d12.dll ({arch or '?'})"
    if any(d in ("dxgi.dll", "d3d11.dll") for d in dlls):
        if is_unity:
            return "unity", "DX11-импорты + Unity-признаки"
        if is_unreal:
            return "unreal", "DX11-импорты + Unreal-признаки"
        return "dx11", f"exe импортирует d3d11/dxgi ({arch or '?'})"
    if any("d3dx9" in d or d == "d3d9.dll" for d in dlls):
        return "dx9", f"exe импортирует d3d9 ({arch or '?'})"
    if any("d3d8" in d for d in dlls):
        return "old", "exe импортирует d3d8 (эпоха XP)"

    # EN: no dx imports — try local DB, then folder heuristics / RU: импортов DX нет
    if game_name:
        hit = db_lookup(game_name)
        if hit:
            return hit, f"известная игра / known game: {game_name}"
    if is_unity:
        return "unity", "признаки Unity (папка *_Data / UnityPlayer.dll)"
    if is_unreal:
        return "unreal", "признаки Unreal Engine"
    return "dx11", "DirectX не определён — безопасный дефолт dx11"
