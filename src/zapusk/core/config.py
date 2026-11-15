"""EN: app config (language, auto mode) in ~/.local/share/zapusk/config.json.
   RU: конфиг приложения (язык, авто-режим) в ~/.local/share/zapusk/config.json."""
import json
from zapusk.core.util import DATA_DIR, ensure_dirs

CFG_FILE = DATA_DIR / "config.json"
DEFAULTS = {"lang": "ru", "auto_mode": True}


def load():
    ensure_dirs()
    try:
        data = json.loads(CFG_FILE.read_text(encoding="utf-8"))
        return {**DEFAULTS, **data}
    except Exception:
        return dict(DEFAULTS)


def save(cfg):
    ensure_dirs()
    CFG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def get(key):
    return load().get(key, DEFAULTS.get(key))


def set_key(key, value):
    cfg = load()
    cfg[key] = value
    save(cfg)
