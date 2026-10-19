# SPDX-License-Identifier: GPL-3.0-or-later
import argparse, sys, os, pathlib
from zapusk.core import library, system
from zapusk.core.presets import PRESETS
from zapusk.core.util import LOGS_DIR, ensure_dirs
from zapusk.core.prefix import prefix_path

def log_path(g):
    return LOGS_DIR / f"{g['slug']}.log"

def cmd_doctor(a):
    print(system.doctor())

def cmd_add(a):
    exe = os.path.abspath(a.exe)
    if not os.path.exists(exe):
        print(f"❌ Файл не найден: {exe}"); return 1
    try:
        g = library.add(a.name or pathlib.Path(exe).stem, exe, a.preset,
                        shared_prefix=not a.own_prefix, args=a.args or "")
    except ValueError as e:
        print(f"❌ {e}"); return 1
    print(f"✅ Добавлено: {g['name']} (пресет {a.preset})")
    print(f"   Теперь: python -m zapusk fix \"{g['name']}\"  (поставит зависимости)")
    return 0

def cmd_list(a):
    gs = library.games()
    if not gs:
        print("Библиотека пуста. Добавь игру: python -m zapusk add /путь/к/game.exe --preset dx11")
        return
    for g in gs:
        print(f"• {g['name']}  [{g['preset']}]  {g['exe']}")

def cmd_fix(a):
    g = library.get(a.name)
    if not g:
        print(f"❌ Игра '{a.name}' не найдена. Список: python -m zapusk list"); return 1
    preset = PRESETS.get(g["preset"], PRESETS["dx11"])
    prefix = prefix_path(g["slug"], g.get("shared_prefix", False))
    lp = log_path(g)
    print(f"Чиним '{g['name']}' в префиксе {prefix} … (лог: {lp})")
    from zapusk.core.deps import fix_game
    def progress(m): print(f"  → {m}")
    fix_game(prefix, preset, log=str(lp), progress=progress)
    if preset.get("note"):
        print(f"\n💡 {preset['note']}")
    print(f"\nЗапуск: python -m zapusk run \"{g['name']}\"")
    return 0

def cmd_run(a):
    g = library.get(a.name)
    if not g:
        print(f"❌ Игра '{a.name}' не найдена."); return 1
    if a.exe:  # запуск конкретного exe (напр. установщик Social Club)
        g = dict(g); g["exe"] = os.path.abspath(a.exe)
    from zapusk.core.runner import launch
    lp = launch(g)
    print(f"🚀 Запущено: {g['name']}")
    print(f"   Лог: {lp}")
    print("   Если чёрный экран/вылет — смотри: python -m zapusk logs \"%s\"" % g['name'])
    return 0

def cmd_logs(a):
    lp = LOGS_DIR / f"{library.get(a.name)['slug']}.log" if library.get(a.name) else None
    if not lp or not lp.exists():
        print("Лог не найден."); return 1
    lines = lp.read_text(encoding='utf-8', errors='replace').splitlines()
    for l in lines[-(a.lines or 60):]:
        print(l)
    return 0

def cmd_remove(a):
    library.remove(a.name)
    print(f"Удалено: {a.name}")

def cmd_detect(a):
    from zapusk.core import detect
    preset, reason = detect.detect_preset(a.exe, a.name)
    print(f"Пресет / preset: {preset}\nПричина / reason: {reason}")
    web = detect.web_lookup(a.name) if a.name else None
    if web:
        print(f"Сеть / web: {web[1]} -> {web[0]}")
    return 0

def cmd_gui(a):
    from zapusk.gui import run_gui
    return run_gui()

def main():
    ensure_dirs()
    p = argparse.ArgumentParser(prog="zapusk", description="Лаунчер Windows-игр на Arch Linux")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="диагностика системы").set_defaults(fn=cmd_doctor)
    sp = sub.add_parser("add", help="добавить игру")
    sp.add_argument("exe"); sp.add_argument("--name", default=None)
    sp.add_argument("--preset", default="dx11", choices=list(PRESETS.keys()))
    sp.add_argument("--args", default="")
    sp.add_argument("--own-prefix", action="store_true", help="отдельный префикс для игры")
    sp.set_defaults(fn=cmd_add)

    sub.add_parser("list", help="список игр").set_defaults(fn=cmd_list)

    sp = sub.add_parser("fix", help="установить зависимости и настроить префикс")
    sp.add_argument("name"); sp.set_defaults(fn=cmd_fix)

    sp = sub.add_parser("run", help="запустить игру")
    sp.add_argument("name"); sp.add_argument("--exe", default=None, help="запустить другой exe (установщик и т.п.)")
    sp.set_defaults(fn=cmd_run)

    sp = sub.add_parser("logs", help="показать лог игры")
    sp.add_argument("name"); sp.add_argument("--lines", type=int, default=60)
    sp.set_defaults(fn=cmd_logs)

    sp = sub.add_parser("remove", help="убрать из библиотеки")
    sp.add_argument("name"); sp.set_defaults(fn=cmd_remove)

    sp = sub.add_parser("detect", help="определить пресет по exe")
    sp.add_argument("exe"); sp.add_argument("--name", default="")
    sp.set_defaults(fn=cmd_detect)

    sub.add_parser("gui", help="графический интерфейс").set_defaults(fn=cmd_gui)

    a = p.parse_args()
    return a.fn(a) or 0

if __name__ == "__main__":
    sys.exit(main())
