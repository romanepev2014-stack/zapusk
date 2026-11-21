# SPDX-License-Identifier: GPL-3.0-or-later
"""EN: compat oracle — warn BEFORE launch about games known to be unfixable.
RU: оракул совместимости — предупреждение ДО запуска об играх, которые не заведутся."""

import pathlib

KNOWN_BAD = [
    (
        "valorant",
        "Vanguard (ядерный античит Riot) — не работает нигде вне официального клиента Windows. Одиночного режима нет.",
    ),
    ("faceit", "Faceit Anti-Cheat (ядерный) — не запустится под Wine/VM."),
    (
        "fortnite",
        "Fortnite: EAC без Linux-поддержки — матчмейкинг не пустит. Не трать время.",
    ),
    ("pubg", "PUBG: ядерный античит — не работает."),
    (
        "gta v online",
        "GTA Online: BattlEye без Linux-флага Rockstar — онлайн не пустит. Одиночная часть — да.",
    ),
    (
        "easyanticheat",
        "Игра с EAC: работает только если разработчик включил Linux-флаг. Проверь protondb.com.",
    ),
    (
        "games for windows live",
        "Games for Windows Live — мёртвый DRM. Нужна версия без GFWL.",
    ),
    (
        "securom",
        "SecuROM — старый DRM ломается на современных системах; ищи версию без него.",
    ),
]

MARKERS = ["games for windows live"]


def check(name, exe=None, folder=None):
    """EN: -> warning text or None. RU: -> текст предупреждения или None."""
    n = (name or "").lower()
    for frag, why in KNOWN_BAD:
        if frag in n:
            return why
    if folder:
        try:
            for f in pathlib.Path(folder).iterdir():
                if any(m in f.name.lower() for m in MARKERS):
                    return KNOWN_BAD[6][1]
        except OSError:
            pass
    return None
