# SPDX-License-Identifier: GPL-3.0-or-later
# Пресеты: зависимости + настройки под тип игры.
# verbs — то, что ставит winetricks (-q, тихо).

PRESETS = {
    "gta5": {
        "label": "GTA V / Rockstar (Social Club)",
        "winver": "win7",
        "verbs": ["vcrun2019", "d3dx9", "d3dcompiler_47", "xact", "corefonts"],
        "vkd3d": False,
        "env": {},
        "note": "Первый запуск ставит Social Club — просто жди. "
                "Не запустится — запусти Social-Club-Setup.exe из папки игры один раз через Zapusk.",
    },
    "dx12": {
        "label": "Современная игра (DirectX 12)",
        "winver": "win10",
        "verbs": ["vcrun2019", "d3dcompiler_47", "xact", "corefonts"],
        "vkd3d": True,
        "env": {"VKD3D_FEATURE_LEVEL": "12_1"},
        "note": "Требуется видеокарта с Vulkan 1.3+ и свежий VKD3D-Proton.",
    },
    "dx11": {
        "label": "Современная игра (DirectX 11)",
        "winver": "win7",
        "verbs": ["vcrun2019", "d3dcompiler_47", "xact", "corefonts"],
        "vkd3d": False,
        "env": {},
        "note": "",
    },
    "dx9": {
        "label": "Игра эпохи DirectX 9",
        "winver": "win7",
        "verbs": ["d3dx9", "vcrun2013", "corefonts"],
        "vkd3d": False,
        "env": {},
        "note": "",
    },
    "unity": {
        "label": "Unity-игра",
        "winver": "win7",
        "verbs": ["vcrun2013", "vcrun2019", "corefonts"],
        "vkd3d": False,
        "env": {},
        "note": "",
    },
    "unreal": {
        "label": "Unreal Engine",
        "winver": "win7",
        "verbs": ["vcrun2019", "xact", "corefonts"],
        "vkd3d": False,
        "env": {},
        "note": "",
    },
    "old": {
        "label": "Старьё (Windows XP-эра)",
        "winver": "winxp",
        "verbs": ["d3dx9", "corefonts"],
        "vkd3d": False,
        "env": {"WINE_LARGE_ADDRESS_AWARE": "1"},
        "virtual_desktop": "1280x720",
        "note": "Включён виртуальный рабочий стол — меняется в настройках игры.",
    },
    "java": {
        "label": "Java-игра (Minecraft и т.д.)",
        "winver": "win7",
        "verbs": ["corefonts"],
        "vkd3d": False,
        "env": {},
        "note": "Запускается через системную Java (java -jar). Шейдеры/моды — настройки самой игры. "
                "Runs via system Java; shaders/mods are the game's own settings.",
    },
    "launcher": {
        "label": "Лаунчер (Epic / Origin / др.)",
        "winver": "win7",
        "verbs": ["dotnet48", "corefonts", "vcrun2019"],
        "vkd3d": False,
        "env": {},
        "note": "dotnet48 ставится ДОЛГО (10–20 мин) — не убивай процесс.",
    },
}

PRESET_NAMES = list(PRESETS.keys())
