"""Zapusk 2.1 — cyberpunk carbon launcher / киберпанк-лаунчер.

EN: opaque carbon background, animated RGB neon window border, liquid-smooth
    theme transitions, drag&drop, one-click Fix & Launch, GE-Proton/DXVK
    updater, system optimization.
RU: непрозрачный карбоновый фон, анимированная RGB-неоновая рамка окна,
    плавные «жидкие» переходы темы, drag&drop, «Починить и запустить»,
    обновление GE-Proton/DXVK, оптимизация системы.
"""

# SPDX-License-Identifier: GPL-3.0-or-later
import math
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QEvent,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    Qt,
    QThread,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygon,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from zapusk.core import i18n, library
from zapusk.core.prefix import open_prefix, prefix_path
from zapusk.core.presets import PRESETS
from zapusk.core.runner import launch
from zapusk.core.util import (
    DATA_DIR,
    LOGS_DIR,
    PREFIXES_DIR,
    ensure_dirs,
    host_prefix,
)

_ = i18n.tr


def _cfg(key, default=None):
    """EN: read app config. RU: читаем конфиг приложения."""
    try:
        import json as _j

        return _j.loads((DATA_DIR / "config.json").read_text(encoding="utf-8")).get(
            key, default
        )
    except Exception:
        return default


SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent / "scripts"

INSTALL_SCRIPT = SCRIPTS_DIR / "install.sh"
INSTALL_ARCH = SCRIPTS_DIR / "install_arch.sh"


# ============================================================
# EN: 4 worlds x 2 modes (dark/light) — same scenes as the website.
# RU: 4 мира x 2 режима (тёмный/светлый) — те же сцены, что на сайте.
# ============================================================
WORLDS = [
    (
        "Cyber",
        {
            "accent": "#00e5ff",
            "accent2": "#ff2fd6",
            "bg": "#07080c",
            "border": "#1b2135",
            "btn": "rgba(255,255,255,18)",
            "btnhover": "rgba(127,200,255,34)",
            "card": "#12141f",
            "err": "#ff3b5c",
            "input": "#0a0c12",
            "muted": "#5d6a86",
            "ok": "#00ff9d",
            "panel": "#0e1017",
            "scene": {
                "far": "#0a1020",
                "glow": "#00e5ff",
                "mid": "#070c18",
                "near": "#04060f",
                "sky1": "#03040a",
                "sky2": "#0a1226",
                "stars": 1,
                "win1": "#00e5ff",
                "win2": "#ff2fd6",
            },
            "text": "#e6f4ff",
            "warn": "#ffb020",
        },
        {
            "accent": "#0090c8",
            "accent2": "#c81e9e",
            "bg": "#dfe6f2",
            "border": "#c7d2e4",
            "btn": "rgba(0,25,70,12)",
            "btnhover": "rgba(0,140,200,40)",
            "card": "#ffffff",
            "err": "#d21f45",
            "input": "#e8edf5",
            "muted": "#5b6880",
            "ok": "#0a8f5b",
            "panel": "#f4f7fc",
            "scene": {
                "far": "#8fa3c4",
                "glow": "#9fc4ff",
                "mid": "#6e829f",
                "near": "#4d5f78",
                "sky1": "#a8bde0",
                "sky2": "#dfe9f8",
                "stars": 0,
                "win1": "#2a3550",
                "win2": "#7a4a8a",
            },
            "text": "#0c1220",
            "warn": "#b57500",
        },
    ),
    (
        "Matrix",
        {
            "accent": "#00ff88",
            "accent2": "#aaff00",
            "bg": "#040805",
            "border": "#16301f",
            "btn": "rgba(0,255,136,14)",
            "btnhover": "rgba(0,255,136,34)",
            "card": "#0f1d13",
            "err": "#ff3b5c",
            "input": "#08120b",
            "muted": "#5f7a66",
            "ok": "#00ff9d",
            "panel": "#0a140d",
            "scene": {"rbg": "#010502", "rfg": "#00ff88", "rhead": "#d6ffe9"},
            "text": "#e4ffe9",
            "warn": "#ffb020",
        },
        {
            "accent": "#009a56",
            "accent2": "#5f8f00",
            "bg": "#eef5ee",
            "border": "#c9dfd0",
            "btn": "rgba(0,120,60,12)",
            "btnhover": "rgba(0,150,80,30)",
            "card": "#ffffff",
            "err": "#d21f45",
            "input": "#e2efe7",
            "muted": "#57705f",
            "ok": "#0a8f5b",
            "panel": "#f7fbf7",
            "scene": {"rbg": "#f2f7f2", "rfg": "#009a56", "rhead": "#003a1e"},
            "text": "#0c1f13",
            "warn": "#b57500",
        },
    ),
    (
        "Sunset",
        {
            "accent": "#ff6b35",
            "accent2": "#b537f2",
            "bg": "#0d0708",
            "border": "#35202a",
            "btn": "rgba(255,107,53,14)",
            "btnhover": "rgba(255,107,53,34)",
            "card": "#1f1216",
            "err": "#ff4d6b",
            "input": "#140a0c",
            "muted": "#8a6f68",
            "ok": "#7dff8a",
            "panel": "#170d10",
            "scene": {
                "ground": "#2a0d16",
                "m1": "#5c1f2c",
                "m2": "#421522",
                "sky1": "#2a0e2e",
                "sky2": "#8a2b3a",
                "sky3": "#e86a3a",
                "sun1": "#fff3d6",
                "sun2": "#ffb056",
            },
            "text": "#ffece4",
            "warn": "#ffcf5c",
        },
        {
            "accent": "#d84f16",
            "accent2": "#8a2bbf",
            "bg": "#f7ece4",
            "border": "#e4cfc5",
            "btn": "rgba(200,80,20,12)",
            "btnhover": "rgba(220,90,25,30)",
            "card": "#ffffff",
            "err": "#d21f45",
            "input": "#f2e3dc",
            "muted": "#7d6259",
            "ok": "#1d8a4a",
            "panel": "#fdf6f0",
            "scene": {
                "ground": "#5c3226",
                "m1": "#b06a58",
                "m2": "#8a4a3e",
                "sky1": "#f2c4a0",
                "sky2": "#eda06a",
                "sky3": "#ffdba8",
                "sun1": "#fff8e0",
                "sun2": "#ffc478",
            },
            "text": "#241009",
            "warn": "#b57a00",
        },
    ),
    (
        "Sakura",
        {
            "accent": "#ff7ab8",
            "accent2": "#7ad9ff",
            "bg": "#0e070c",
            "border": "#33202c",
            "btn": "rgba(255,122,184,14)",
            "btnhover": "rgba(255,122,184,34)",
            "card": "#1f111b",
            "err": "#ff5c7a",
            "input": "#150a12",
            "muted": "#8a6a80",
            "ok": "#8affc1",
            "panel": "#170d14",
            "scene": {
                "ground": "#2a0f20",
                "m1": "#55203c",
                "m2": "#3f1830",
                "moon": "#ffe9f2",
                "petals": ["#ffc7dd", "#ffabd0", "#ff9ec7", "#ff8dc0"],
                "sky1": "#241019",
                "sky2": "#6e2c4c",
                "sky3": "#c97697",
                "trunk": "#4a2b3a",
            },
            "text": "#ffe9f4",
            "warn": "#ffd25c",
        },
        {
            "accent": "#d63384",
            "accent2": "#2aa8d8",
            "bg": "#fbeef4",
            "border": "#e8ccd9",
            "btn": "rgba(200,50,130,12)",
            "btnhover": "rgba(220,60,140,30)",
            "card": "#ffffff",
            "err": "#d21f45",
            "input": "#f5e4ec",
            "muted": "#7d5f70",
            "ok": "#1d8a5a",
            "panel": "#fdf4f8",
            "scene": {
                "ground": "#7d4462",
                "m1": "#c98aa8",
                "m2": "#a86a8c",
                "moon": "#ffffff",
                "petals": ["#ffb8d4", "#ff9ec7", "#ff8dc0", "#ffd0e2"],
                "sky1": "#ffd9e8",
                "sky2": "#ffb3d1",
                "sky3": "#fff0f6",
                "trunk": "#5c3a4a",
            },
            "text": "#26091a",
            "warn": "#b58200",
        },
    ),
]


WORLDS += [
    (
        "Xbox 360",
        {
            "accent": "#a4d725",
            "accent2": "#5a8a10",
            "bg": "#0c1206",
            "border": "#2a3a14",
            "btn": "rgba(164,215,37,16)",
            "btnhover": "rgba(164,215,37,36)",
            "card": "#1e2c0e",
            "err": "#ff5252",
            "input": "#101a08",
            "muted": "#7d9455",
            "ok": "#9be645",
            "panel": "#16200a",
            "scene": {"scene_type": "x360boot"},
            "text": "#eef7d8",
            "warn": "#ffb020",
        },
        {
            "accent": "#6a9a00",
            "accent2": "#3f6b00",
            "bg": "#eef4da",
            "border": "#d2dfb0",
            "btn": "rgba(90,138,16,12)",
            "btnhover": "rgba(106,154,0,28)",
            "card": "#ffffff",
            "err": "#d21f45",
            "input": "#e6eed0",
            "muted": "#6a7a48",
            "ok": "#4c8a1a",
            "panel": "#f8fbe9",
            "scene": {"scene_type": "x360boot"},
            "text": "#1c2608",
            "warn": "#b57500",
        },
    )
]

# EN: keep only the original 4 + Windows XP + Windows 95.
# RU: оставляем 4 оригинальные + Windows XP + Windows 95.
KEEP_WORLDS = (
    "Cyber",
    "Matrix",
    "Sunset",
    "Sakura",
    "Windows XP",
    "Windows 95",
    "Xbox 360",
)
WORLDS = [w for w in WORLDS if w[0] in KEEP_WORLDS]

# EN: Windows XP and 95 — restored after cleanup. RU: восстановлены после чистки.
WORLDS += [
    (
        "Windows XP",
        {
            "accent": "#3d95ff",
            "accent2": "#7ec850",
            "bg": "#123a6e",
            "border": "#2a5a9a",
            "btn": "rgba(255,255,255,20)",
            "btnhover": "rgba(61,149,255,35)",
            "card": "#2258a0",
            "err": "#ff5252",
            "input": "#0d2f5c",
            "muted": "#9ab8d8",
            "ok": "#7ec850",
            "panel": "#1a4a8a",
            "scene": {
                "cloud": "#ffffff",
                "hill1": "#3d8a3d",
                "hill2": "#2c6e2c",
                "scene_type": "xp",
                "sky1": "#0d2f5c",
                "sky2": "#3d7fd0",
            },
            "text": "#eaf4ff",
            "warn": "#ffb020",
        },
        {
            "accent": "#2c72e0",
            "accent2": "#4caf50",
            "bg": "#eaf4ff",
            "border": "#c8dcf0",
            "btn": "rgba(30,90,180,12)",
            "btnhover": "rgba(44,114,224,25)",
            "card": "#ffffff",
            "err": "#d21f45",
            "input": "#ddeafa",
            "muted": "#5f7a9a",
            "ok": "#2e8f32",
            "panel": "#ffffff",
            "scene": {
                "cloud": "#ffffff",
                "hill1": "#4caf50",
                "hill2": "#388e3c",
                "scene_type": "xp",
                "sky1": "#2f6fc0",
                "sky2": "#7db8f0",
            },
            "text": "#12294a",
            "warn": "#b57500",
        },
    ),
    (
        "Windows 95",
        {
            "accent": "#000080",
            "accent2": "#800080",
            "bg": "#008080",
            "border": "#808080",
            "btn": "#c0c0c0",
            "btnhover": "#d4d4d4",
            "card": "#dfdfdf",
            "err": "#ff0000",
            "input": "#ffffff",
            "muted": "#404040",
            "ok": "#008000",
            "panel": "#c0c0c0",
            "scene": {"color": "#008080", "scene_type": "flat"},
            "text": "#000000",
            "warn": "#ff8000",
        },
        {
            "accent": "#000080",
            "accent2": "#800080",
            "bg": "#008080",
            "border": "#909090",
            "btn": "#c8c8c8",
            "btnhover": "#dcdcdc",
            "card": "#efefef",
            "err": "#ff0000",
            "input": "#ffffff",
            "muted": "#404040",
            "ok": "#008000",
            "panel": "#d0d0d0",
            "scene": {"color": "#008080", "scene_type": "flat"},
            "text": "#000000",
            "warn": "#ff8000",
        },
    ),
]

# EN: per-theme scene tweaks for the 7 active themes.
# RU: доработки сцен для 7 активных тем.
WORLD_TWEAKS = {
    "windows 95": {"scene_type": "flat", "color": "#008080"},
    "gta": {"palms": 1},
}


PALETTES = [(n, d, light) for n, d, light in WORLDS]


def _lc(c1, c2, t):
    a, b = QColor(c1), QColor(c2)

    def f(x, y):
        return int(x + (y - x) * t)

    return QColor(f(a.red(), b.red()), f(a.green(), b.green()), f(a.blue(), b.blue()))


def _lcs(c1, c2, t):  # вернуть строку hex
    return _lc(c1, c2, t).name()


def _theme_extra(th):
    """EN: per-theme stylesheet extras (authentic controls). RU: аутентичные контролы тем."""
    name = th.get("_name", "")
    if name == "Windows 95":
        return """
QPushButton, QCheckBox, QComboBox { background: #c0c0c0; color: #000000; border: 2px outset #dfdfdf; border-radius: 0; }
QPushButton:pressed { border-style: inset; }
QPushButton#primary, QPushButton#good { border: 2px outset #dfdfdf; border-radius: 0; }
QLineEdit, QTextEdit { background: #ffffff; color: #000000; border: 2px inset #808080; border-radius: 0; }
QLabel#big, QLabel#title { color: #000080; }
"""
    if name in ("Windows XP", "Windows 95"):
        return """
QFrame#panel, QFrame#card { background: #ece9d8; border: 2px outset #ffffff; border-radius: 0; }
QPushButton, QCheckBox, QComboBox { background: #ece9d8; color: #000000; border: 2px outset #ffffff; border-radius: 0; }
QPushButton:hover, QCheckBox:hover { background: #dce9f5; }
QPushButton:pressed { border-style: inset; }
QPushButton#primary { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #5cb3ff, stop:1 #2268d8); color: #ffffff; }
QPushButton#good { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #7ec850, stop:1 #3d8a3d); color: #ffffff; }
QLineEdit, QTextEdit { background: #ffffff; color: #000000; border: 2px inset #808080; border-radius: 0; }
QLabel#big, QLabel#title { color: #0a246a; }
#nav { background: #ece9d8; border: 2px outset #ffffff; }
#nav QListWidget::item:selected { background: #316ac5; color: #ffffff; }
"""
    return ""


def build_qss(th):
    """EN: stylesheet from (possibly interpolated) theme. RU: стили из темы."""
    a = th["accent"]

    def hx(k):
        v = th[k]
        return v if v.startswith("#") else "#20242c"

    return f"""
QWidget {{ background: transparent; color: {th["text"]}; font-size: 13px;
         font-family: "Noto Sans", "Inter", sans-serif; }}
#glass {{ background: transparent; border-radius: 16px; }}
#titlebar {{ background: transparent; }}
#titlebar QLabel {{ color: {th["muted"]}; font-weight: bold; letter-spacing: 3px; }}
#nav {{ background: rgba(255,255,255,10); border-radius: 12px; border: 1px solid {hx("border")}; }}
#nav QListWidget {{ background: transparent; border: none; outline: none; }}
#nav QListWidget::item {{ padding: 12px 14px; border-radius: 10px; margin: 3px 6px; color: {th["muted"]}; }}
#nav QListWidget::item:hover {{ background: rgba(127,200,255,26); color: {th["text"]}; }}
#nav QListWidget::item:selected {{ background: {a}; color: #04121a; font-weight: 700; }}
QPushButton {{ background: {th["btn"]}; border: 1px solid {hx("border")};
             border-radius: 10px; padding: 8px 16px; }}
QPushButton:hover {{ background: {th["btnhover"]}; border-color: {a}; }}
QPushButton:pressed {{ background: rgba(127,200,255,60); }}
QPushButton#primary {{ background: {a}; border: none; color: #04121a; font-weight: 700; }}
QPushButton#primary:hover {{ background: {_lcs(a, "#ffffff", 0.25)}; }}
QPushButton#good {{ background: {th["ok"]}; border: none; color: #04140c; font-weight: 800; }}
QPushButton#good:hover {{ background: {_lcs(th["ok"], "#ffffff", 0.2)}; }}
QPushButton#ghost {{ background: transparent; border: none; font-size: 15px; }}
QPushButton#ghost:hover {{ background: rgba(127,200,255,40); border-radius: 8px; }}
QLineEdit, QComboBox, QTextEdit {{ background: {hx("input")}; border: 1px solid {hx("border")};
                                 border-radius: 10px; padding: 6px 10px; selection-background-color: {a}; }}
QComboBox QAbstractItemView {{ background: {hx("panel")}; }}
QFrame#card {{ background: {hx("card")}; border: 1px solid {hx("border")}; border-radius: 16px; }}
QFrame#card:hover {{ border-color: {a}; }}
QFrame#panel {{ background: {hx("panel")}; border: 1px solid {hx("border")}; border-radius: 14px; }}
QLabel#big {{ font-size: 22px; font-weight: 800; }}
QLabel#title {{ font-size: 15px; font-weight: 700; }}
QLabel#muted {{ color: {th["muted"]}; font-size: 12px; }}
QLabel#chip {{ background: {th["accent2"]}; color: white; border-radius: 8px; padding: 2px 8px; font-size: 11px; }}
QLabel#ok {{ color: {th["ok"]}; font-weight: 600; }}
QLabel#warn {{ color: {th["warn"]}; font-weight: 600; }}
QLabel#err {{ color: {th["err"]}; font-weight: 600; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 8px; }}
QScrollBar::handle:vertical {{ background: rgba(127,200,255,70); border-radius: 4px; min-height: 30px; }}
QProgressBar {{ border: 1px solid {hx("border")}; border-radius: 8px; background: rgba(0,0,0,50); text-align: center; height: 14px; }}
QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {a}, stop:1 {th["accent2"]}); border-radius: 8px; }}
""" + _theme_extra(th)


class Theme(QObject):
    """EN: animated theme — 4 worlds, each dark<->light; wave drives t.
    RU: анимированная тема — 4 мира, у каждого тёмный<->светлый; волна качает t."""

    changed = Signal()

    def __init__(self):
        super().__init__()
        self._t = 0.0
        self._pal = 0
        try:
            import json as _j

            cfg = _j.loads((DATA_DIR / "config.json").read_text(encoding="utf-8"))
            self._pal = int(cfg.get("theme", 0)) % len(PALETTES)
        except Exception:
            pass

    def getT(self):
        return self._t

    def setT(self, v):
        q = round(v * 12) / 12
        if q != self._t:
            self._t = q
            self.changed.emit()

    t = Property(float, getT, setT)

    def toggle(self):
        pass  # тему качает волна / RU: theme is driven by the wave

    def current(self):
        _, dk, lt = PALETTES[self._pal % len(PALETTES)]
        th = {}
        for k in dk:
            dv, lv = dk[k], lt.get(k, dk[k])
            if isinstance(dv, list):
                th[k] = dv
            elif isinstance(dv, str) and dv.startswith("#"):
                th[k] = _lcs(dv, lv if isinstance(lv, str) else dv, self._t)
            else:
                th[k] = dv
        th["scene_raw"] = dk["scene"] if self._t < 0.5 else lt["scene"]
        th["_name"] = self.palette_name()
        return th

    def palette_name(self):
        return PALETTES[self._pal % len(PALETTES)][0]

    def set_palette(self, idx):
        idx = idx % len(PALETTES)
        if idx != self._pal:
            self._pal = idx
            i18n.save("theme", idx)
            self.changed.emit()
            try:
                from PySide6.QtWidgets import QApplication

                for w in QApplication.topLevelWidgets():
                    if hasattr(w, "xpbar"):
                        nm = w.theme.palette_name()
                        mode = (
                            "xp"
                            if nm == "Windows XP"
                            else ("95" if nm == "Windows 95" else None)
                        )
                        w.xpbar.set_mode(mode)
                        if hasattr(w, "navw"):
                            w.navw.setVisible(mode is None)
            except Exception:
                import traceback

                traceback.print_exc()

    def qss(self):
        """EN: stylesheet for the current interpolated theme. RU: стили текущей темы."""
        return build_qss(self.current())

    def scene(self):
        """EN: current scene colors (dark/light picked by mode). RU: цвета сцены текущего режима."""
        _, dk, lt = PALETTES[self._pal % len(PALETTES)]
        sd, sl = dk["scene"], lt["scene"]
        out = {}
        for k in sd:
            v = sd[k]
            if isinstance(v, list):
                out[k] = v
            elif isinstance(v, str) and v.startswith("#") and k in sl:
                out[k] = _lcs(v, sl[k], self._t)
            else:
                out[k] = v
        nm = self.palette_name().lower()
        out.update(WORLD_TWEAKS.get(nm, {}))
        out["world"] = (
            out.get("scene_type")
            or {"matrix": "matrix", "sunset": "sunset", "sakura": "sakura"}.get(
                nm, "cyber"
            )
        ).lower()
        out["t"] = self._t
        return out


# ============================================================
# EN: NeonFrame — animated themed background (4 worlds x 2 modes),
#     parallax, matrix rain, sakura petals, pre-rendered border.
# RU: NeonFrame — живой фон (4 мира x 2 режима), параллакс,
#     матричный дождь, лепестки сакуры, предрендер рамки.
# ============================================================
class NeonFrame(QFrame):
    FRAMES = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glass")
        self.theme = None
        self._cache = None
        self._scene_key = None
        self._borders = []
        self._bkey = None
        self._bidx = 0
        self._px = 0.0
        self._py = 0.0
        self._ov = 48
        # дождь матрицы / RU: matrix rain state
        self._drops = []
        self._cols = 0
        # лепестки / RU: petals state
        self._petals = []
        self._cars = []  # EN: city traffic / RU: трафик города
        self._phase = 0.0  # EN: wave drift / RU: дрейф волн
        self._timer = QTimer(self)
        self._timer.setInterval(80)  # EN: one 12.5fps timer for everything
        self._timer.timeout.connect(self._tick_all)
        self._timer.start()
        self._paused = False

    def set_anim(self, paused):
        """EN: pause background animation (e.g. while splash is showing).
        RU: пауза анимации фона (например, пока показывается сплэш)."""
        self._paused = paused
        if not paused:
            self.update()

    # ---------- управление ----------
    def _tick_all(self):
        """EN: single timer tick: border pulse + world dynamics.
        RU: один тик на всё: пульс рамки + динамика мира."""
        if self._paused:
            return
        if self._borders:
            self._bidx = (self._bidx + 1) % len(self._borders)
        sc = self._sc()
        if sc:
            w = sc.get("world")
            if w == "matrix":
                self._rain_step()
            elif w == "sakura":
                self._petals_step()
            elif w == "cyber":
                self._cars_step()
        self.update()

    def _sc(self):
        return self.theme.scene() if self.theme else None

    def set_parallax(self, x, y):
        if abs(x - self._px) > 0.02 or abs(y - self._py) > 0.02:
            self._px, self._py = x, y
            self.update()

    def invalidate(self):
        self._cache = None
        self._scene_key = None
        self._borders = []
        self._bkey = None
        self.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.invalidate()

    # ---------- рендер статичной сцены ----------
    def _render_bg(self, sc):
        ov = self._ov
        w, h = self.width() + ov * 2, self.height() + ov * 2
        pm = QPixmap(w, h)
        pm.fill(QColor(sc.get("rbg") or sc.get("sky1") or "#05070c"))
        pt = QPainter(pm)
        pt.setRenderHint(QPainter.Antialiasing)
        world = sc.get("world")
        if world == "cyber":
            self._draw_city(pt, w, h, sc, ov)
        elif world == "sunset":
            self._draw_sunset(pt, w, h, sc, ov)
            if sc.get("palms"):
                self._draw_palms(pt, w, h, sc)
        elif world == "sakura":
            self._draw_sakura(pt, w, h, sc, ov)
        elif world == "wave":
            pass  # волны рисуются живьём в paintEvent
        elif world == "flat":
            if sc.get("color2") and sc.get("radial"):
                fg = QRadialGradient(w / 2, h * 0.42, max(w, h) * 0.75)
                fg.setColorAt(0, QColor(sc["color"]))
                fg.setColorAt(1, QColor(sc["color2"]))
                pt.fillRect(0, 0, w, h, fg)
            elif sc.get("color2"):
                fg = QLinearGradient(0, 0, 0, h)
                fg.setColorAt(0, QColor(sc["color"]))
                fg.setColorAt(1, QColor(sc["color2"]))
                pt.fillRect(0, 0, w, h, fg)
            else:
                pt.fillRect(0, 0, w, h, QColor(sc.get("color", "#008080")))
        elif world == "minecraft":
            self._draw_minecraft(pt, w, h, sc, ov)
        elif world == "forest":
            self._draw_forest(pt, w, h, sc, ov)
        elif world == "road":
            self._draw_road(pt, w, h, sc, ov)
        elif world == "xp":
            self._draw_xp(pt, w, h, sc, ov)
        elif world == "sea":
            self._draw_sea(pt, w, h, sc, ov)
        elif world == "x360boot":
            self._draw_x360boot(pt, w, h, sc, ov)
        if sc.get("logo"):
            self._draw_logo(pt, w, h, sc["logo"], sc.get("win1", "#ffffff"))
        if sc.get("beastie"):
            self._draw_beastie(pt, w, h)
        pt.end()
        self._cache = pm

    def _draw_city(self, p, w, h, sc, ov):
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor(sc["sky1"]))
        g.setColorAt(1, QColor(sc["sky2"]))
        p.fillRect(0, 0, w, h, g)
        rnd = random.Random(42)
        if sc.get("stars"):
            for _ in range(120):
                p.setPen(QPen(QColor(255, 255, 255, rnd.randint(30, 110)), 1))
                p.drawPoint(rnd.randint(0, w), rnd.randint(0, h // 3))
        glow = QColor(sc["glow"])
        rg = QRadialGradient(ov, ov, 380)
        rg.setColorAt(0, QColor(glow.red(), glow.green(), glow.blue(), 34))
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(pm_rect(w, h), rg)
        base = h - 20
        for depth, (kcol, kwin, wd, op) in enumerate(
            (
                ("far", 0.09, 0.12, 0.85),
                ("mid", 0.14, 0.16, 0.95),
                ("near", 0.2, 0.2, 1),
            )
        ):
            p.setOpacity(op)
            x = -40
            while x < w:
                bw = rnd.randint(120, 230)
                bh = rnd.randint(
                    int(h * 0.18), int(h * (0.6 if kcol == "near" else 0.42))
                )
                top = base - bh
                p.fillRect(x, top, bw, bh, QColor(sc[kcol]))
                if rnd.random() < 0.3:
                    ax = x + rnd.randint(6, max(7, bw - 8))
                    p.fillRect(ax, top - rnd.randint(12, 30), 3, 30, QColor(sc[kcol]))
                gy = top + 8
                while gy < base - 8:
                    gx = x + 5
                    while gx < x + bw - 6:
                        if rnd.random() < wd:
                            cname = rnd.choice(["win1", "win1", "win2", "win2", "glow"])
                            c = QColor(sc[cname])
                            c.setAlpha(rnd.randint(50, 150))
                            p.fillRect(gx, gy, 3, 4, c)
                        gx += 9
                    gy += 13
                x += bw + rnd.randint(80, 180)
            p.setOpacity(1)
            base += 12
        p.fillRect(0, h - 40, w, 40, QColor(0, 0, 0, 110))

    def _draw_sunset(self, p, w, h, sc, ov):
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor(sc["sky1"]))
        g.setColorAt(0.5, QColor(sc["sky2"]))
        g.setColorAt(1, QColor(sc["sky3"]))
        p.fillRect(0, 0, w, h, g)
        sx, sy = w // 2, int(h * 0.62)
        rg = QRadialGradient(sx, sy, 150)
        rg.setColorAt(0, QColor(sc["sun1"]))
        rg.setColorAt(0.55, QColor(sc["sun2"]))
        rg.setColorAt(1, QColor(255, 144, 64, 0))
        p.fillRect(pm_rect(w, h), rg)
        p.setPen(QPen(QColor(sc["m1"]).darker(120), 2))
        for bx, by in (
            (w * 0.2, h * 0.32),
            (w * 0.24, h * 0.3),
            (w * 0.72, h * 0.26),
            (w * 0.76, h * 0.28),
        ):
            p.drawArc(int(bx), int(by), 16, 8, 0, 5760)
        for pts, col in (
            (
                [
                    (-40, h * 0.82),
                    (w * 0.18, h * 0.48),
                    (w * 0.33, h * 0.66),
                    (w * 0.52, h * 0.42),
                    (w * 0.75, h * 0.66),
                    (w * 0.9, h * 0.5),
                    (w + 40, h * 0.7),
                ],
                sc["m1"],
            ),
            (
                [
                    (-40, h * 0.92),
                    (w * 0.15, h * 0.68),
                    (w * 0.35, h * 0.85),
                    (w * 0.55, h * 0.6),
                    (w * 0.74, h * 0.85),
                    (w + 40, h * 0.75),
                ],
                sc["m2"],
            ),
        ):
            p.fillRect(0, 0, 0, 0, QColor(0, 0, 0, 0))
            path = QPainterPath()
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.closeSubpath()
            p.fillPath(path, QColor(col))
        p.fillRect(0, int(h * 0.88), w, h, QColor(sc["ground"]))
        p.setPen(QPen(QColor(sc["ground"]).lighter(120), 2))
        rnd = random.Random(7)
        for gx in range(20, w, 30):
            p.drawLine(gx, h, gx + rnd.randint(-4, 4), h - rnd.randint(14, 34))

    def _draw_sakura(self, p, w, h, sc, ov):
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor(sc["sky1"]))
        g.setColorAt(0.55, QColor(sc["sky2"]))
        g.setColorAt(1, QColor(sc["sky3"]))
        p.fillRect(0, 0, w, h, g)
        mx, my = int(w * 0.78), int(h * 0.2)
        rg = QRadialGradient(mx, my, 100)
        rg.setColorAt(0, QColor(sc["moon"]))
        rg.setColorAt(1, QColor(255, 233, 242, 0))
        p.fillRect(mx - 100, my - 100, 200, 200, rg)
        p.setPen(Qt.NoPen)
        for pts, col in (
            (
                [
                    (-60, h * 0.82),
                    (w * 0.19, h * 0.52),
                    (w * 0.39, h * 0.8),
                    (w * 0.61, h * 0.48),
                    (w * 0.81, h * 0.78),
                    (w + 60, h * 0.58),
                ],
                sc["m1"],
            ),
            (
                [
                    (-60, h * 0.95),
                    (w * 0.16, h * 0.72),
                    (w * 0.35, h * 0.92),
                    (w * 0.61, h * 0.7),
                    (w * 0.86, h * 0.9),
                    (w + 60, h * 0.8),
                ],
                sc["m2"],
            ),
        ):
            path = QPainterPath()
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.closeSubpath()
            p.fillPath(path, QColor(col))
        p.fillRect(0, int(h * 0.9), w, h, QColor(sc["ground"]))
        rnd = random.Random(11)
        for tx, ts in (
            (w * 0.13, 1.3),
            (w * 0.38, 1.0),
            (w * 0.6, 1.35),
            (w * 0.85, 1.05),
        ):
            ty = h * 0.92
            p.setPen(QPen(QColor(sc["trunk"]), int(12 * ts), Qt.SolidLine, Qt.RoundCap))
            p.drawLine(int(tx), int(ty), int(tx), int(ty - 130 * ts))
            p.setPen(Qt.NoPen)
            for _ in range(70):
                a = rnd.uniform(0, 6.283)
                r = rnd.uniform(0, 1) ** 0.5
                cx = tx + 100 * ts * r * math.cos(a)
                cy = ty - 70 * ts - 80 * ts * r * math.sin(a)
                c = QColor(rnd.choice(sc["petals"]))
                c.setAlpha(rnd.randint(120, 240))
                p.setBrush(c)
                p.drawEllipse(
                    int(cx),
                    int(cy),
                    int(rnd.uniform(8, 20) * ts),
                    int(rnd.uniform(8, 20) * ts),
                )

    # ---------- динамика: дождь, лепестки ----------
    def _rain_step(self):
        if not hasattr(self, "_drops"):
            self._drops = []
        if not hasattr(self, "_cols"):
            self._cols = 0
        self._sc()
        w, _h = self.width(), self.height()
        fs = 16
        cols = max(1, w // fs)
        if cols != self._cols:
            self._cols = cols
            hh = max(1, self.height() // 16)
            self._drops = [random.randint(-hh, 0) for _ in range(cols)]
        self._rain_img = None

    def _draw_rain(self, p):
        sc = self._sc()
        w, h = self.width(), self.height()
        fs = 16
        p.fillRect(0, 0, w, h, QColor(sc["rbg"]))
        p.setFont(QFont("monospace", 10))
        chars = "アイウエオカキクケコサシスセソ01ZAPUSK"
        for i in range(self._cols):
            x = i * fs
            y = self._drops[i] * fs
            ch = random.choice(chars)
            p.setPen(QColor(sc["rhead"] if random.random() < 0.1 else sc["rfg"]))
            p.drawText(x, y, ch)
            if y > h and random.random() > 0.976:
                self._drops[i] = 0
            self._drops[i] += 1

    def _petals_step(self):
        w, h = self.width(), self.height()
        if not getattr(self, "_petals", None):
            self._petals = [
                {
                    "x": random.uniform(0, w),
                    "y": random.uniform(-h, 0),
                    "vy": random.uniform(0.6, 1.8),
                    "ph": random.uniform(0, 6.28),
                    "r": random.uniform(0, 360),
                    "s": random.uniform(4, 9),
                }
                for _ in range(24)
            ]
        for pt in self._petals:
            pt["y"] += pt["vy"]
            pt["x"] += math.sin(pt["y"] * 0.02 + pt["ph"]) * 0.8
            pt["r"] += 2
            if pt["y"] > h + 20:
                pt["y"] = -20
                pt["x"] = random.uniform(0, w)

    def _draw_petals(self, p):
        sc = self._sc()
        p.setPen(Qt.NoPen)
        for pt in self._petals:
            p.save()
            p.translate(pt["x"], pt["y"])
            p.rotate(pt["r"])
            c = QColor(random.choice(sc["petals"]))
            c.setAlpha(200)
            p.setBrush(c)
            p.drawEllipse(0, 0, int(pt["s"] * 1.4), int(pt["s"]))
            p.restore()

    def _cars_step(self):
        w, _h = self.width(), self.height()
        if not getattr(self, "_cars", None):
            self._cars = [
                {
                    "x": random.uniform(0, w),
                    "d": random.choice([-1, 1]),
                    "v": random.uniform(3.0, 5.5),
                    "lane": random.randint(0, 1),
                }
                for _ in range(7)
            ]
        for c in self._cars:
            c["x"] += c["v"] * c["d"]
            if c["x"] < -30:
                c["x"] = w + 20
            if c["x"] > w + 30:
                c["x"] = -20

    def _draw_palms(self, p, w, h, sc):
        near = QColor(sc["ground"]).lighter(150)
        for x, s in (
            (w * 0.1, 1.0),
            (w * 0.24, 0.75),
            (w * 0.82, 1.1),
            (w * 0.94, 0.8),
        ):
            p.setPen(QPen(near, 7, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(int(x), int(h * 0.88), int(x + 10), int(h * 0.6))
            p.setPen(Qt.NoPen)
            p.setBrush(near)
            for d in (-1, -0.5, 0, 0.5, 1):
                p.drawEllipse(int(x + 10 + d * 26 - 20), int(h * 0.58), 40, 16)

    def _draw_cars(self, p):
        w, h = self.width(), self.height()
        road_y = h - 46
        p.fillRect(0, road_y - 4, w, 34, QColor(0, 0, 0, 140))
        p.setPen(QPen(QColor(255, 220, 140, 60), 1, Qt.DashLine))
        p.drawLine(0, road_y + 13, w, road_y + 13)
        p.setPen(Qt.NoPen)
        for c in self._cars:
            y = road_y + 4 + c["lane"] * 14
            head = (
                QColor(255, 244, 200, 230) if c["d"] > 0 else QColor(255, 90, 80, 230)
            )
            tail = (
                QColor(255, 60, 60, 200) if c["d"] > 0 else QColor(255, 244, 200, 200)
            )
            hx = c["x"] + (6 if c["d"] > 0 else -2)
            tx = c["x"] - (2 if c["d"] > 0 else -6)
            p.setBrush(head)
            p.drawEllipse(int(hx), int(y), 4, 3)
            p.setBrush(tail)
            p.drawEllipse(int(tx), int(y), 3, 3)

    def _draw_wave(self, p, w, h, sc):
        """EN: liquid black&white waves (iPhone/macOS), drifting. RU: жидкие ч/б волны."""
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor(sc["sky1"]))
        g.setColorAt(1, QColor(sc["sky2"]))
        p.fillRect(0, 0, w, h, g)
        layers = 4 if sc.get("detail") else 3
        for i in range(layers):
            base = h * (0.5 + 0.15 * i)
            amp = 34 + 26 * i
            path = QPainterPath()
            crest = QPainterPath()
            x = 0
            first = True
            while x <= w + 24:
                y = (
                    base
                    + math.sin(x * 0.004 + i * 1.7 + self._phase) * amp
                    + math.sin(x * 0.011 + i * 0.9 + self._phase * 1.4) * amp * 0.4
                )
                if first:
                    path.moveTo(x, y)
                    crest.moveTo(x, y)
                    first = False
                else:
                    path.lineTo(x, y)
                    crest.lineTo(x, y)
                x += 24
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.closeSubpath()
            col = QColor(sc["w1"])
            col.setAlpha(70 + i * 45)
            p.fillPath(path, col)
            cp = QColor(sc["w2"])
            cp.setAlpha(60 + i * 40)
            p.setPen(QPen(cp, 2))
            p.drawPath(crest)

    def _draw_minecraft(self, p, w, h, sc, ov):
        """EN: blocky voxel landscape. RU: кубический мир."""
        cell = max(10, w // 80)
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor("#7db3e8"))
        g.setColorAt(1, QColor("#c8e0f5"))
        p.fillRect(0, 0, w, h, g)
        # квадратное солнце
        p.fillRect(int(w * 0.78), int(h * 0.1), cell * 3, cell * 3, QColor("#f8f0a0"))
        rnd = random.Random(5)
        ground = int(h * 0.55)
        grass = QColor("#5f9e3a")
        dirt = QColor("#8a5a32")
        dirt2 = QColor("#7a4e2a")
        for row in range(ground, h + cell, cell):
            depth = (row - ground) // cell
            for x in range(0, w + cell, cell):
                if depth == 0:
                    c = grass
                else:
                    c = dirt if rnd.random() < 0.5 else dirt2
                p.fillRect(x, row, cell - 1, cell - 1, c)
        # кубические деревья
        for tx in range(int(w * 0.08), w, int(w * 0.22)):
            th = int(h * 0.12) + rnd.randint(0, int(h * 0.1))
            ty = ground - th
            p.fillRect(tx, ty, cell, th, QColor("#6b4a2a"))
            for dx, dy, s in (
                (0, -cell * 2, cell * 3),
                (-cell, -cell, cell * 2),
                (cell, -cell, cell * 2),
            ):
                p.fillRect(tx + dx, ty + dy, s, s, QColor("#3f7a24"))

    def _draw_forest(self, p, w, h, sc, ov):
        """EN: lush forest — layered pines, moon glow, mist. RU: густой лес."""
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor("#0c1f2a"))
        g.setColorAt(0.6, QColor("#14342c"))
        g.setColorAt(1, QColor("#1d4a30"))
        p.fillRect(0, 0, w, h, g)
        rg = QRadialGradient(w * 0.72, h * 0.2, 180)
        rg.setColorAt(0, QColor(220, 240, 220, 90))
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(QRectF(0, 0, w, h), rg)
        p.fillEllipse(
            int(w * 0.72 - 26), int(h * 0.2 - 26), 52, 52, QColor(235, 245, 225, 200)
        )
        rnd = random.Random(9)
        for layer, (col, count, size, base) in enumerate(
            (
                ("#1d4530", 12, 2.1, 0.86),
                ("#173a26", 16, 1.5, 0.92),
                ("#102c1a", 22, 1.0, 1.0),
            )
        ):
            p.setBrush(QColor(col))
            p.setPen(Qt.NoPen)
            for i in range(count):
                tx = rnd.randint(-20, w + 20)
                th = int(h * 0.16 * size * (0.7 + rnd.random() * 0.7))
                ty = int(h * base)
                p.drawRect(tx - max(3, th // 14), ty - th // 4, max(6, th // 7), th)
                for k in range(4):
                    ww = int(th * (1.0 - k * 0.22))
                    yy = ty - th // 4 - k * th // 5
                    p.drawPolygon(
                        QPolygon(
                            [
                                QPoint(tx - ww, yy),
                                QPoint(tx + ww, yy),
                                QPoint(tx, yy - th // 3),
                            ]
                        )
                    )
        mist = QLinearGradient(0, int(h * 0.6), 0, h)
        mist.setColorAt(0, QColor(140, 190, 150, 0))
        mist.setColorAt(1, QColor(140, 190, 150, 46))
        p.fillRect(QRectF(0, h * 0.6, w, h * 0.4), mist)

    def _draw_road(self, p, w, h, sc, ov):
        """EN: endless road through a clearing (ETS2). RU: бесконечная дорога в поляне."""
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor("#1a2a4a"))
        g.setColorAt(0.55, QColor("#7a4a6a"))
        g.setColorAt(0.56, QColor("#2c3418"))
        g.setColorAt(1, QColor("#1a2010"))
        p.fillRect(0, 0, w, h, g)
        p.fillEllipse(int(w * 0.62), int(h * 0.36), 70, 70, QColor("#ffd9a0"))  # солнце
        # поляна и лес по краям
        p.setPen(Qt.NoPen)
        rnd = random.Random(3)
        for side in (0, 1):
            for i in range(8):
                tx = (
                    int(w * (0.04 + 0.1 * i))
                    if side == 0
                    else int(w * (0.96 - 0.1 * i))
                )
                th = rnd.randint(int(h * 0.1), int(h * 0.22))
                p.setBrush(QColor("#12200f"))
                p.drawPolygon(
                    QPolygon(
                        [
                            QPoint(tx - th // 2, int(h * 0.56)),
                            QPoint(tx + th // 2, int(h * 0.56)),
                            QPoint(tx, int(h * 0.56) - th),
                        ]
                    )
                )
        # дорога в перспективе
        cx = w // 2
        p.setBrush(QColor("#20242c"))
        p.drawPolygon(
            QPolygon(
                [
                    QPoint(cx - 14, int(h * 0.56)),
                    QPoint(cx + 14, int(h * 0.56)),
                    QPoint(w, h),
                    QPoint(0, h),
                ]
            )
        )
        p.setPen(QPen(QColor("#e8c860"), 4, Qt.DashLine))
        p.drawLine(cx, int(h * 0.58), cx, h)

    def _draw_xp(self, p, w, h, sc, ov):
        """EN: Bliss — one smooth grass slope to the horizon, sky above.
        RU: Блисс — один плавный травяной склон до горизонта, выше небо."""
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor(sc["sky1"]))
        g.setColorAt(0.55, QColor(sc["sky2"]))
        g.setColorAt(0.56, QColor("#2f7a2f"))
        g.setColorAt(1, QColor("#58a83c"))
        p.fillRect(0, 0, w, h, g)
        rg = QRadialGradient(w * 0.76, h * 0.14, 200)
        rg.setColorAt(0, QColor(255, 252, 235, 230))
        rg.setColorAt(1, QColor(255, 252, 235, 0))
        p.fillRect(QRectF(0, 0, w, h), rg)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(sc["cloud"]))
        for cx, cy, cw, ch in (
            (w * 0.22, h * 0.16, 150, 40),
            (w * 0.55, h * 0.09, 190, 48),
            (w * 0.85, h * 0.24, 120, 32),
            (w * 0.38, h * 0.3, 100, 26),
        ):
            for k in range(3):
                p.drawEllipse(
                    int(cx - cw / 2 + k * cw * 0.32), int(cy), int(cw * 0.6), int(ch)
                )
        p.setBrush(QColor("#fffbe8"))
        p.drawEllipse(int(w * 0.76 - 20), int(h * 0.14 - 20), 40, 40)
        # дальний холм (светлее)
        far = QPainterPath()
        far.moveTo(0, h * 0.58)
        far.quadTo(w * 0.35, h * 0.46, w * 0.7, h * 0.56)
        far.quadTo(w * 0.9, h * 0.6, w, h * 0.55)
        far.lineTo(w, h)
        far.lineTo(0, h)
        far.closeSubpath()
        p.fillPath(far, QColor("#69b84c"))
        # главный склон: от нижнего левого к горизонту справа
        hill = QPainterPath()
        hill.moveTo(0, h)
        hill.lineTo(0, h * 0.78)
        hill.quadTo(w * 0.3, h * 0.66, w * 0.62, h * 0.6)
        hill.quadTo(w * 0.85, h * 0.57, w, h * 0.56)
        hill.lineTo(w, h)
        hill.closeSubpath()
        p.fillPath(hill, QColor(sc["hill1"]))
        # травяная текстура — короткие штрихи
        rnd = random.Random(12)
        p.setPen(QPen(QColor("#3d8a2f"), 1))
        for _ in range(260):
            x = rnd.randint(0, w)
            y = rnd.randint(int(h * 0.62), h)
            p.drawLine(x, y, x + rnd.randint(2, 6), y)

    def _draw_sea(self, p, w, h, sc, ov):
        """EN: sea with mountains on the horizon (Ocean). RU: море, за ним горы."""
        hz = int(h * 0.52)
        g = QLinearGradient(0, 0, 0, hz)
        g.setColorAt(0, QColor(sc["sky1"]))
        g.setColorAt(1, QColor(sc["sky2"]))
        p.fillRect(0, 0, w, hz, g)
        rg = QRadialGradient(w * 0.7, hz * 0.7, 160)
        rg.setColorAt(0, QColor(sc["glow"]))
        rg.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(QRectF(0, 0, w, hz), rg)
        for pts, col in (
            (
                [
                    (-40, hz),
                    (w * 0.2, hz - h * 0.2),
                    (w * 0.45, hz),
                    (w * 0.7, hz - h * 0.24),
                    (w + 40, hz - h * 0.06),
                ],
                sc["m1"],
            ),
            (
                [
                    (-40, hz),
                    (w * 0.3, hz - h * 0.12),
                    (w * 0.6, hz),
                    (w * 0.9, hz - h * 0.14),
                ],
                sc["m2"],
            ),
        ):
            path = QPainterPath()
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.lineTo(w, hz + 4)
            path.lineTo(0, hz + 4)
            path.closeSubpath()
            p.fillPath(path, QColor(col))
        wg = QLinearGradient(0, hz, 0, h)
        wg.setColorAt(0, QColor(sc["sky2"]).lighter(110))
        wg.setColorAt(1, QColor(sc["water"]))
        p.fillRect(0, hz, w, h - hz, wg)
        rnd = random.Random(4)
        p.setPen(QPen(QColor(sc["glow"]), 1))
        for _ in range(40):
            y = rnd.randint(hz + 8, h - 8)
            x = rnd.randint(0, w - 80)
            ln = rnd.randint(20, 80)
            c = QColor(sc["glow"])
            c.setAlpha(rnd.randint(30, 90))
            p.setPen(QPen(c, 1))
            p.drawLine(x, y, x + ln, y)

    def _draw_logo(self, p, w, h, text, color="#ffffff"):
        p.save()
        p.setFont(QFont("Noto Sans", 220, QFont.Bold))
        c = QColor(color)
        c.setAlpha(24)
        p.setPen(c)
        p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, text)
        p.restore()

    def _draw_beastie(self, p, w, h):
        """EN: Beastie logo exactly: a red ball with two horns, nothing else.
        RU: логотип Beastie в точности: красный круг и два рога, без лица."""
        cx, cy, r = w * 0.5, h * 0.46, h * 0.28
        red = QColor("#d6202f")
        red.setAlpha(82)
        p.setPen(Qt.NoPen)
        p.setBrush(red)
        # левый рог (как на фото: от верхнего левого края круга, наружу-вверх)
        horn = QPainterPath()
        horn.moveTo(cx - r * 0.72, cy - r * 0.62)
        horn.quadTo(cx - r * 1.55, cy - r * 1.35, cx - r * 1.15, cy - r * 1.85)
        horn.quadTo(cx - r * 1.05, cy - r * 1.0, cx - r * 0.28, cy - r * 0.85)
        horn.closeSubpath()
        p.fillPath(horn, red)
        # правый рог
        horn2 = QPainterPath()
        horn2.moveTo(cx + r * 0.72, cy - r * 0.62)
        horn2.quadTo(cx + r * 1.55, cy - r * 1.35, cx + r * 1.15, cy - r * 1.85)
        horn2.quadTo(cx + r * 1.05, cy - r * 1.0, cx + r * 0.28, cy - r * 0.85)
        horn2.closeSubpath()
        p.fillPath(horn2, red)
        # сам круг
        p.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))

    def _draw_logo(self, p, w, h, text, color="#ffffff"):
        p.save()
        p.setFont(QFont("Noto Sans", 220, QFont.Bold))
        c = QColor(color)
        c.setAlpha(24)
        p.setPen(c)
        p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, text)
        p.restore()

    def _draw_beastie(self, p, w, h):
        """EN: the real Beastie logo — red ball with two horns (as on the photo).
        RU: настоящий логотип Beastie — красный шар с двумя рожками."""
        cx, cy, r = w * 0.5, h * 0.44, h * 0.26
        red = QColor("#d6202f")
        red.setAlpha(78)
        p.setPen(Qt.NoPen)
        for sgn in (-1, 1):
            path = QPainterPath()
            bx = cx + sgn * r * 0.6
            path.moveTo(bx, cy - r * 0.45)
            path.quadTo(
                bx + sgn * r * 0.95, cy - r * 1.55, bx + sgn * r * 0.1, cy - r * 1.75
            )
            path.quadTo(
                bx + sgn * r * 0.5, cy - r * 1.0, bx - sgn * r * 0.3, cy - r * 0.7
            )
            path.closeSubpath()
            p.fillPath(path, red)
        p.setBrush(red)
        p.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))

    def _draw_logo(self, p, w, h, text, color="#ffffff"):
        p.save()
        p.setFont(QFont("Noto Sans", 220, QFont.Bold))
        c = QColor(color)
        c.setAlpha(24)
        p.setPen(c)
        p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, text)
        p.restore()

    def _draw_beastie(self, p, w, h):
        """EN: the BSD daemon — red ball with horns. RU: демон BSD — красный шар с рожками."""
        cx, cy, r = w * 0.5, h * 0.4, h * 0.24
        red = QColor("#e03c31")
        red.setAlpha(64)
        p.setPen(Qt.NoPen)
        p.setBrush(red)
        p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
        p.setPen(QPen(red, int(r * 0.22), Qt.SolidLine, Qt.RoundCap))
        # рожки
        p.drawArc(
            int(cx - r * 1.2),
            int(cy - r * 1.9),
            int(r * 1.1),
            int(r * 1.6),
            0,
            130 * 16,
        )
        p.drawArc(
            int(cx + r * 0.1),
            int(cy - r * 1.9),
            int(r * 1.1),
            int(r * 1.6),
            50 * 16,
            130 * 16,
        )
        # глаза и улыбка
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(
            int(cx - r * 0.42), int(cy - r * 0.25), int(r * 0.3), int(r * 0.42)
        )
        p.drawEllipse(
            int(cx + r * 0.12), int(cy - r * 0.25), int(r * 0.3), int(r * 0.42)
        )
        p.setBrush(QColor("#101820"))
        p.drawEllipse(
            int(cx - r * 0.33), int(cy - r * 0.05), int(r * 0.12), int(r * 0.2)
        )
        p.drawEllipse(
            int(cx + r * 0.21), int(cy - r * 0.05), int(r * 0.12), int(r * 0.2)
        )
        p.setPen(QPen(red, int(r * 0.1), Qt.SolidLine, Qt.RoundCap))
        p.drawArc(
            int(cx - r * 0.35),
            int(cy + r * 0.05),
            int(r * 0.7),
            int(r * 0.6),
            200 * 16,
            140 * 16,
        )

    def _draw_x360boot(self, p, w, h, sc, ov):
        """EN: Xbox 360 boot screen — lime gradient, sphere rings with a gap,
        glow orb, bubbles, dark corner. RU: стартовый экран Xbox 360."""
        g = QLinearGradient(0, 0, int(w * 0.4), h)
        g.setColorAt(0.0, QColor("#86c40a"))
        g.setColorAt(0.45, QColor("#aade18"))
        g.setColorAt(1.0, QColor("#8fce10"))
        p.fillRect(0, 0, w, h, g)
        # тёмный угол справа сверху
        corner = QPainterPath()
        corner.moveTo(w, 0)
        corner.lineTo(w * 0.55, 0)
        corner.quadTo(w * 0.98, h * 0.02, w, h * 0.5)
        corner.closeSubpath()
        p.fillPath(corner, QColor(74, 122, 0, 110))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(44, 76, 0, 90))
        p.drawEllipse(int(w * 0.86), int(-h * 0.12), int(w * 0.30), int(h * 0.34))
        # скобки по краям (как на фото)
        p.setPen(QPen(QColor(232, 247, 192, 200), int(h * 0.045)))
        p.drawArc(
            int(-w * 0.06), int(-h * 0.10), int(w * 0.20), int(h * 0.42), 0, 120 * 16
        )
        p.drawArc(
            int(-w * 0.05),
            int(h * 0.72),
            int(w * 0.18),
            int(h * 0.40),
            300 * 16,
            90 * 16,
        )
        # сфера: три кольца с разрывом слева-сверху
        cx, cy = w * 0.60, h * 0.60
        p.setPen(QPen(QColor(255, 255, 255, 215), int(h * 0.020)))
        for r, gap in (
            (h * 0.46, (150, 55)),
            (h * 0.355, (150, 50)),
            (h * 0.26, (148, 48)),
        ):
            rr = int(r)
            start = (gap[0] + gap[1]) * 16
            span = (360 - gap[1]) * 16
            p.drawArc(int(cx - rr), int(cy - rr), rr * 2, rr * 2, start, span)
        # блик-точка на внешнем кольце
        ang = -30
        bx = cx + math.cos(math.radians(ang)) * h * 0.46
        by = cy + math.sin(math.radians(ang)) * h * 0.46
        p.setBrush(QColor(255, 255, 255, 230))
        p.drawEllipse(int(bx - 6), int(by - 6), 12, 12)
        # свечение-орб справа от сферы
        ox, oy = w * 0.76, h * 0.56
        rg = QRadialGradient(ox, oy, h * 0.20)
        rg.setColorAt(0, QColor(255, 255, 235, 200))
        rg.setColorAt(1, QColor(255, 255, 235, 0))
        p.fillRect(QRectF(ox - h * 0.22, oy - h * 0.22, h * 0.44, h * 0.44), rg)
        p.setBrush(QColor(253, 255, 240, 220))
        p.drawEllipse(
            int(ox - h * 0.075), int(oy - h * 0.075), int(h * 0.15), int(h * 0.15)
        )
        # пузыри
        rnd = random.Random(21)
        for _ in range(26):
            bx2, by2 = rnd.uniform(0, w), rnd.uniform(0, h)
            r2 = rnd.uniform(3, h * 0.045)
            c = QColor(255, 255, 255, rnd.randint(28, 90))
            if rnd.random() < 0.4:
                p.setBrush(c)
                p.setPen(Qt.NoPen)
                p.drawEllipse(int(bx2), int(by2), int(r2 * 2), int(r2 * 2))
            else:
                p.setBrush(Qt.NoBrush)
                p.setPen(QPen(c, 2))
                p.drawEllipse(int(bx2), int(by2), int(r2 * 2), int(r2 * 2))

    # ---------- рамка ----------
    def _render_borders(self, th):
        self._borders = []
        w, h = self.width(), self.height()
        if w < 10 or h < 10:
            return
        path = QPainterPath()
        path.addRoundedRect(1, 1, w - 2, h - 2, 15, 15)
        c1, c2 = QColor(th["accent"]), QColor(th["accent2"])
        for i in range(self.FRAMES):
            tt = i / self.FRAMES
            col = _lc(c1.name(), c2.name(), (math.sin(tt * 6.283) + 1) / 2)
            grad = QLinearGradient(0, 0, w, h)
            grad.setColorAt(0, c1)
            grad.setColorAt(1, col)
            pm = QPixmap(w, h)
            pm.fill(Qt.transparent)
            pp = QPainter(pm)
            pp.setRenderHint(QPainter.Antialiasing)
            pp.setPen(QPen(QBrush(grad), 2))
            pp.drawPath(path)
            pp.end()
            self._borders.append(pm)
        self._bkey = (
            self.theme.palette_name(),
            round(self.theme.t * 12) if self.theme else 0,
            self.size(),
        )

    # ---------- paint ----------
    def paintEvent(self, event):
        try:
            self._paint_scene(event)
        except Exception:
            import traceback

            try:
                log = pathlib.Path.home() / ".local/share/zapusk/bg.log"
                log.parent.mkdir(parents=True, exist_ok=True)
                if not log.exists() or log.stat().st_size < 4000:
                    with open(log, "a") as f:
                        f.write(traceback.format_exc() + "\n")
            except Exception:
                pass
            qp = QPainter(self)
            qp.fillRect(self.rect(), QColor("#0d1322"))
            qp.end()

    def _paint_scene(self, event):
        sc = self._sc()
        if not sc:
            return
        key = (sc.get("world"), round(sc.get("t", 0) * 12), self.size())
        if (
            self._cache is None
            or self._cache.width() != self.width() + self._ov * 2
            or key != self._scene_key
        ):
            self._render_bg(sc)
            self._scene_key = key
        bkey = (sc.get("world"), round(sc.get("t", 0) * 12), self.size())
        if not self._borders or self._bkey != bkey:
            th = self.theme.current()
            self._render_borders(th)
        p = QPainter(self)
        world = sc.get("world")
        if world == "matrix":
            self._draw_rain(p)
        else:
            p.drawPixmap(
                int(-self._ov + self._px * -16),
                int(-self._ov + self._py * -12),
                self._cache,
            )
        if world == "wave":
            self._draw_wave(p, self.width(), self.height(), sc)
        if world == "sakura":
            self._draw_petals(p)
        if world == "cyber":
            self._draw_cars(p)
        if self._borders:
            p.drawPixmap(0, 0, self._borders[self._bidx])
        p.end()


def pm_rect(w, h):
    return QRectF(0, 0, w, h)


# ============================================================
# EN: generic workers with a global registry — the app never aborts
# with "QThread destroyed while running" anymore.
# RU: фоновые потоки с глобальным реестром — приложение больше не
# падает с "QThread destroyed while running".
# ============================================================
_ACTIVE_WORKERS = []


class Worker(QThread):
    line = Signal(str)
    done = Signal()

    def __init__(self, fn):
        super().__init__()
        self.fn = fn
        _ACTIVE_WORKERS.append(self)

    def run(self):
        try:
            self.fn()
        except Exception as e:
            import traceback

            print("Worker error:", e)
            traceback.print_exc()
        finally:
            if self in _ACTIVE_WORKERS:
                _ACTIVE_WORKERS.remove(self)
            self.done.emit()


class ShellThread(QThread):
    line = Signal(str)
    done = Signal(int)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        code = self.fn(lambda s: self.line.emit(s))
        self.done.emit(code if isinstance(code, int) else 0)


class _Signal(QObject):
    sig = Signal(str)


class ParallaxFilter(QObject):
    """EN: app-level mouse tracker — parallax works over ANY widget, no button needed.
    RU: фильтр на всё приложение — параллакс работает над любыми кнопками."""

    def __init__(self, win):
        super().__init__()
        self.win = win

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.MouseMove and self.win.isVisible():
            pos = self.win.mapFromGlobal(QCursor.pos())
            nx = pos.x() / max(self.win.width(), 1) * 2 - 1
            ny = pos.y() / max(self.win.height(), 1) * 2 - 1
            self.win.glass.set_parallax(nx, ny)
        return False


class AutoInstallThread(QThread):
    line = Signal(str)
    done = Signal(int)

    def run(self):
        script = INSTALL_SCRIPT if INSTALL_SCRIPT.exists() else INSTALL_ARCH
        if shutil.which("flatpak-spawn"):
            cmd = (
                host_prefix()
                + ["pkexec", "bash", str(script)]
                + (["--auto"] if script == INSTALL_ARCH else [])
            )
        elif shutil.which("pkexec"):
            cmd = ["pkexec", "bash", str(script)] + (
                ["--auto"] if script == INSTALL_ARCH else []
            )
        else:
            term = None
            for t in (
                ["konsole", "-e"],
                ["gnome-terminal", "--"],
                ["alacritty", "-e"],
                ["kitty", "-e"],
                ["xterm", "-e"],
            ):
                if shutil.which(t[0]):
                    term = t
                    break
            if not term:
                self.line.emit(
                    "❌ Нет pkexec/терминала — вручную: sudo bash install_arch.sh"
                )
                self.done.emit(1)
                return
            cmd = term + ["sudo", "bash", str(INSTALL_SCRIPT), "--auto"]
        self.line.emit("$ " + " ".join(cmd))
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            bufsize=1,
        )
        for ln in p.stdout:
            self.line.emit(ln.rstrip())
        p.wait()
        self.done.emit(p.returncode)


# ============================================================
# EN: Add game dialog. RU: Диалог добавления игры.
# ============================================================
class AddGameDialog(QDialog):
    def __init__(self, parent=None, initial_exe=""):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setWindowTitle(_("Add game"))
        self.resize(600, 380)
        self.result_game = None
        lay = QVBoxLayout(self)
        t = QLabel(_("New game"))
        t.setObjectName("big")
        lay.addWidget(t)
        self.name = QLineEdit()
        self.name.setPlaceholderText(_("Name"))
        lay.addWidget(self.name)
        row = QHBoxLayout()
        self.exe = QLineEdit(initial_exe)
        self.exe.setPlaceholderText("Путь к .exe / Path to .exe")
        b = QPushButton("Обзор…")
        b.clicked.connect(self.browse_exe)
        scan = QPushButton("📂 Сканировать папку")
        scan.clicked.connect(self.scan)
        row.addWidget(self.exe, 1)
        row.addWidget(b)
        row.addWidget(scan)
        lay.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel(_("Preset") + ":"))
        self.preset = QComboBox()
        for k, v in PRESETS.items():
            self.preset.addItem(f"{v['label']}  ({k})", k)
        self.preset.setCurrentIndex(list(PRESETS.keys()).index("dx11"))
        row2.addWidget(self.preset, 1)
        btn_auto = QPushButton("🔍 Авто")
        btn_auto.setToolTip("Определить по .exe")
        btn_auto.clicked.connect(self.auto_preset)
        btn_web = QPushButton("🌐 База")
        btn_web.setToolTip("Спросить PCGamingWiki")
        btn_web.clicked.connect(self.web_preset)
        row2.addWidget(btn_auto)
        row2.addWidget(btn_web)
        lay.addLayout(row2)
        self.detect_label = QLabel("")
        self.detect_label.setObjectName("muted")
        lay.addWidget(self.detect_label)
        self.own = QCheckBox(_("Own prefix"))
        self.own.setChecked(bool(_cfg("own_prefix", True)))
        lay.addWidget(self.own)
        self.args = QLineEdit()
        self.args.setPlaceholderText(_("Arguments"))
        lay.addWidget(self.args)
        lay.addWidget(QLabel("💡 Потом жми «🚀 Починить и запустить»."))
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText(_("Add"))
        bb.button(QDialogButtonBox.Ok).setObjectName("primary")
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)
        if initial_exe:
            self.name.setText(pathlib.Path(initial_exe).stem)

    def auto_preset(self):
        """EN: detect preset from the exe itself. RU: определить пресет по exe."""
        from zapusk.core import detect

        exe = self.exe.text().strip()
        if not exe or not pathlib.Path(exe).exists():
            QMessageBox.information(self, "Zapusk", "Сначала укажи .exe")
            return
        preset, reason = detect.detect_preset(exe, self.name.text())
        if preset in PRESETS:
            self.preset.setCurrentIndex(list(PRESETS.keys()).index(preset))
        self.detect_label.setText(f"🔍 {reason}")

    def web_preset(self):
        """EN: online lookup by game name. RU: онлайн-поиск по названию."""
        from zapusk.core import detect

        name = self.name.text().strip()
        if not name:
            QMessageBox.information(self, "Zapusk", "Сначала введи название игры")
            return
        hit = detect.web_lookup(name)
        self.detect_label.setText("🌐 спрашиваю PCGamingWiki…")
        QApplication.processEvents()
        hit = detect.web_lookup(name)
        if hit:
            preset, info = hit
            self.detect_label.setText(f"🌐 {info}")
            if preset and preset in PRESETS:
                self.preset.setCurrentIndex(list(PRESETS.keys()).index(preset))
        else:
            self.detect_label.setText("🌐 не нашёл в сети — жми «🔍 Авто»")

    def browse_exe(self):
        f, _ = QFileDialog.getOpenFileName(
            self, "Выбери .exe", str(pathlib.Path.home()), "Exe (*.exe)"
        )
        if f:
            self.exe.setText(f)
            if not self.name.text():
                self.name.setText(pathlib.Path(f).stem)

    def scan(self):
        d = QFileDialog.getExistingDirectory(self, "Папка с игрой / Game folder")
        if not d:
            return
        found = library.scan_folder(d)
        if not found:
            QMessageBox.information(
                self, "Zapusk", "Подходящих .exe не нашлось / No game .exe found"
            )
            return
        pick, ok = QInputDialog.getItem(
            self,
            "Найденные exe / Found",
            "Похоже на игру / Looks like the game:",
            found,
            0,
            False,
        )
        if ok and pick:
            self.exe.setText(pick)
            if not self.name.text():
                self.name.setText(pathlib.Path(pick).stem)
            self.auto_preset()

    def accept(self):
        if not self.exe.text() or not pathlib.Path(self.exe.text()).exists():
            QMessageBox.warning(
                self, "Zapusk", "Укажи существующий .exe / Choose a valid .exe"
            )
            return
        if not self.name.text():
            self.name.setText(pathlib.Path(self.exe.text()).stem)
        try:
            g = library.add(
                self.name.text(),
                self.exe.text(),
                self.preset.currentData(),
                shared_prefix=not self.own.isChecked(),
                args=self.args.text(),
            )
        except ValueError as e:
            QMessageBox.warning(self, "Zapusk", str(e))
            return
        from zapusk.core import oracle

        warn = oracle.check(
            self.name.text(), self.exe.text(), str(pathlib.Path(self.exe.text()).parent)
        )
        self.result_game = g
        super().accept()
        if warn:
            QMessageBox.warning(self, "🔮 Оракул совместимости", warn)


# ============================================================
# EN: Game settings dialog. RU: Настройки игры.
# ============================================================
class GameDialog(QDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setObjectName("panel")
        self.setWindowTitle(f"{_('Settings')} — {game['name']}")
        self.resize(560, 600)
        lay = QVBoxLayout(self)
        g = game
        lay.addWidget(QLabel("Exe:"))
        self.exe = QLineEdit(g.get("exe", ""))
        lay.addWidget(self.exe)
        lay.addWidget(QLabel(_("Work dir") + ":"))
        self.workdir = QLineEdit(g.get("workdir", ""))
        lay.addWidget(self.workdir)
        lay.addWidget(QLabel(_("Arguments") + ":"))
        self.args = QLineEdit(g.get("args", ""))
        lay.addWidget(self.args)
        lay.addWidget(QLabel(_("Preset") + ":"))
        self.preset = QComboBox()
        for k, v in PRESETS.items():
            self.preset.addItem(f"{v['label']} ({k})", k)
        cur = g.get("preset", "dx11")
        self.preset.setCurrentIndex(
            list(PRESETS.keys()).index(cur) if cur in PRESETS else 1
        )
        lay.addWidget(self.preset)

        def chk(title, key, default=False):
            c = QCheckBox(title)
            c.setChecked(g.get(key, default))
            setattr(self, key, c)
            lay.addWidget(c)
            return c

        chk(_("GameMode"), "gamemode", True)
        chk(_("MangoHUD"), "mangohud")
        chk("Fsync", "fsync", True)
        chk("Esync", "esync", True)
        chk("DXVK HUD", "dxvk_hud")
        chk("🔧 " + _("Auto-heal"), "autofix", True)
        chk("Wine debug-лог", "debug")
        chk("Large Address Aware", "large_address")

        lay.addWidget(QLabel(_("Virtual desktop") + ":"))
        self.vdesk = QLineEdit(g.get("virtual_desktop", ""))
        lay.addWidget(self.vdesk)

        row = QHBoxLayout()
        row3 = QHBoxLayout()
        for text, fn in (("📸 Снапшот", self.mk_snap), ("⏪ Откат", self.do_rollback)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row3.addWidget(b)
        lay.addLayout(row3)
        for text, fn in (
            ("🚀 " + _("Fix & Launch"), self.fix_run),
            ("📁 " + _("Game folder"), self.opengame),
            ("📂 " + _("Prefix"), self.openpfx),
            ("🗑 " + _("Remove"), self.remove),
        ):
            b = QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        lay.addLayout(row)

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Save).setText(_("Save"))
        bb.button(QDialogButtonBox.Save).setObjectName("primary")
        bb.accepted.connect(self.save)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def collect(self):
        return {
            "exe": self.exe.text().strip() or self.game["exe"],
            "workdir": self.workdir.text().strip()
            or str(pathlib.Path(self.exe.text()).parent),
            "args": self.args.text(),
            "preset": self.preset.currentData(),
            "gamemode": self.gamemode.isChecked(),
            "mangohud": self.mhud.currentData(),
            "fsync": self.fsync.isChecked(),
            "esync": self.esync.isChecked(),
            "dxvk_hud": self.dxvk_hud.isChecked(),
            "debug": self.debug.isChecked(),
            "large_address": self.large_address.isChecked(),
            "virtual_desktop": self.vdesk.text().strip(),
        }

    def save(self):
        library.update(self.game["name"], self.collect())
        self.accept()

    def mk_snap(self):
        from zapusk.core import snapshots

        g = library.get(self.game["name"]) or self.game
        snapshots.snapshot_prefix(g, progress=lambda m: print(m))
        QMessageBox.information(
            self, "Zapusk", "📸 Снапшот сохранён (хранятся последние 3)"
        )

    def do_rollback(self):
        from zapusk.core import snapshots

        g = library.get(self.game["name"]) or self.game
        snaps = snapshots.list_snapshots(g)
        if not snaps:
            QMessageBox.information(self, "Zapusk", "Снапшотов нет")
            return
        pick, ok = QInputDialog.getItem(
            self, "⏪ Откат префикса", "К какому снапшоту откатить?", snaps, 0, False
        )
        if ok and pick:
            ok2, info = snapshots.rollback(g, pick, progress=lambda m: print(m))
            QMessageBox.information(
                self, "Zapusk", f"⏪ Откат к {info}" if ok2 else "Не удалось откатить"
            )

    def fix_run(self):
        library.update(self.game["name"], self.collect())
        self.accept()
        w = self.parent()
        while w and not isinstance(w, MainWindow):
            w = w.parent()
        if w:
            w.fix_and_launch(library.get(self.game["name"]))

    def openpfx(self):
        g = library.get(self.game["name"])
        open_prefix(prefix_path(g["slug"], g.get("shared_prefix", False)))

    def opengame(self):
        """EN: open the game's folder in the file manager. RU: открыть папку игры."""
        g = library.get(self.game["name"]) or self.game
        w = self.parent()
        while w and not isinstance(w, MainWindow):
            w = w.parent()
        if w:
            w.opengamefolder(g)

    def remove(self):
        self.accept()
        w = self.parent()
        while w and not isinstance(w, MainWindow):
            w = w.parent()
        if w:
            w.remove_game(self.game)


# ============================================================
# EN: Remove game dialog — with optional file/prefix deletion.
# RU: Диалог удаления игры — с опцией удаления файлов и префикса.
# ============================================================
class RemoveGameDialog(QDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setWindowTitle(_("Remove"))
        lay = QVBoxLayout(self)
        t = QLabel(f"🗑 {game['name']}")
        t.setObjectName("big")
        lay.addWidget(t)
        self.cb_files = QCheckBox(
            f"Удалить файлы игры / Delete game files\n{game.get('workdir', '')}"
        )
        self.cb_prefix = QCheckBox("Удалить префикс Wine / Delete Wine prefix")
        lay.addWidget(self.cb_files)
        lay.addWidget(self.cb_prefix)
        lay.addWidget(
            QLabel("Из списка игра удаляется всегда. / Always removed from the list.")
        )
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText(_("Remove"))
        bb.button(QDialogButtonBox.Ok).setObjectName("danger")
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)


# ============================================================
# EN: game card. RU: карточка игры.
# ============================================================
class Card(QFrame):
    def __init__(self, game, win):
        super().__init__()
        self.setObjectName("card")
        self.setFixedSize(260, 175)
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        chip = QLabel(game.get("preset", ""))
        chip.setObjectName("chip")
        top.addWidget(chip)
        top.addStretch(1)
        lay.addLayout(top)
        t = QLabel(game["name"])
        t.setObjectName("title")
        t.setWordWrap(True)
        lay.addWidget(t)
        m = QLabel(pathlib.Path(game["exe"]).name)
        m.setObjectName("muted")
        m.setWordWrap(True)
        lay.addWidget(m)
        lay.addStretch(1)
        row = QHBoxLayout()
        run = QPushButton("🚀 " + _("Fix & Launch"))
        run.setObjectName("good")
        run.clicked.connect(
            lambda: win.fix_and_launch(library.get(game["name"]) or game)
        )
        row.addWidget(run)
        lay.addLayout(row)
        row2 = QHBoxLayout()
        quick = QPushButton("▶ " + _("Launch"))
        quick.clicked.connect(lambda: win.launch(game))
        cfg = QPushButton("⚙")
        cfg.setFixedWidth(42)
        cfg.clicked.connect(lambda: win.settings(game))
        folder = QPushButton("📂")
        folder.setFixedWidth(42)
        folder.setToolTip(_("Game folder"))
        folder.clicked.connect(lambda: win.opengamefolder(game))
        logs = QPushButton("📋")
        logs.setFixedWidth(42)
        logs.clicked.connect(lambda: win.show_logs(game))
        rm = QPushButton("🗑")
        rm.setFixedWidth(42)
        rm.setToolTip(_("Remove"))
        rm.setObjectName("danger")
        rm.clicked.connect(lambda: win.remove_game(game))
        panic = QPushButton("💀")
        panic.setFixedWidth(42)
        panic.setToolTip(_("Panic kill"))
        panic.setObjectName("danger")
        panic.clicked.connect(lambda: win.panic_kill(game))
        row2.addWidget(quick)
        row2.addWidget(cfg)
        row2.addWidget(folder)
        row2.addWidget(logs)
        row2.addWidget(panic)
        row2.addWidget(rm)
        lay.addLayout(row2)


# ============================================================
# EN: Splash — liquid-glass boot animation: RGB blobs merge into
#     the ZAPUSK wordmark, lightning strikes under it, then fades.
# RU: Сплэш — жидко-стеклянная загрузка: RGB-пятна сливаются в
#     слово ZAPUSK, под ним бьёт молния, затем всё растворяется.
# ============================================================
class Splash(QWidget):
    """EN: interactive particle splash — a swarm of rainbow stars assembles the
    ZAPUSK wordmark; poke the letters and they burst apart and re-assemble.
    RU: интерактивный сплэш — рой радужных звёзд собирает слово ZAPUSK;
    тыкай буквы — они разлетаются и собираются заново."""

    done = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # EN: get moves WITHOUT pressed buttons
        # RU: движения БЕЗ зажатой кнопки
        self._parts = []
        self._t = 0.0
        self._mouse = None
        self._timer = QTimer(self)
        self._timer.setInterval(40)  # ~25 fps, только на старте / EN: only during boot
        self._timer.timeout.connect(self._tick)
        self._fade = None

    # ---------- particle setup ----------
    def _build(self):
        """EN: sample the wordmark pixels -> particle targets. RU: точки букв -> цели частиц."""
        w, h = self.width(), self.height()
        img = QImage(w, h, QImage.Format_ARGB32)
        img.fill(0)
        pt = QPainter(img)
        f = QFont("Noto Sans", 46)  # EN: smaller wordmark / RU: слово компактнее
        f.setBold(True)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 6)
        pt.setFont(f)
        pt.setPen(QColor(255, 255, 255))
        target = QRect(int(w * 0.19), int(h * 0.36), int(w * 0.62), int(h * 0.28))
        pt.drawText(target, Qt.AlignHCenter | Qt.AlignVCenter, "ZAPUSK")
        pt.end()

        step = 6
        targets = []
        for y in range(0, h, step):
            for x in range(0, w, step):
                if QColor.fromRgba(img.pixel(x, y)).alpha() > 120:
                    targets.append((x, y))
        if len(targets) > 450:  # EN: cap particle count / RU: ограничиваем число частиц
            k = len(targets) // 450 + 1
            targets = targets[::k]

        self._parts = []
        n = len(targets)
        for i, (tx, ty) in enumerate(targets):
            side = i % 4  # EN: fly in from 4 sides / RU: влетают с 4 сторон
            if side == 0:
                sx, sy = -60, (i * 37) % h
            elif side == 1:
                sx, sy = w + 60, (i * 53) % h
            elif side == 2:
                sx, sy = (i * 71) % w, -60
            else:
                sx, sy = (i * 91) % w, h + 60
            # EN: left-to-right typing stagger / RU: набор слова слева направо
            frac = tx / max(w, 1)
            delay = 0.15 + frac * 1.0 + (i % 7) * 0.02
            hue = i / max(n - 1, 1)  # EN: full rainbow / RU: вся радуга
            self._parts.append(
                {
                    "sx": sx,
                    "sy": sy,
                    "tx": tx,
                    "ty": ty,
                    "delay": delay,
                    "bx": 0.0,
                    "by": 0.0,
                    "px": sx,
                    "py": sy,
                    "hue": hue,
                }
            )

    # ---------- lifecycle ----------
    def _build_stars(self):
        """EN: static starfield backdrop, rendered once. RU: звёздный фон, рисуем один раз."""
        w, h = self.width(), self.height()
        pm = QPixmap(w, h)
        pm.fill(QColor(5, 6, 10))
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        for cx, cy, col in (
            (w * 0.2, h * 0.25, QColor(0, 229, 255, 14)),
            (w * 0.85, h * 0.8, QColor(255, 47, 214, 12)),
        ):
            g = QRadialGradient(cx, cy, 320)
            g.setColorAt(0, col)
            g.setColorAt(1, QColor(0, 0, 0, 0))
            p.fillRect(pm.rect(), g)
        for i in range(240):
            x = (i * 137.508 + (i * i) % 53) % w
            y = (i * 61.803 + (i * 7) % 97) % h
            a = 40 + (i * 29) % 180
            r = 1 if i % 9 else 2
            tint = QColor.fromHsvF(((i * 0.618) % 1.0), 0.4, 1.0)
            tint.setAlpha(a)
            p.setPen(QPen(tint, 1))
            p.drawEllipse(int(x), int(y), r, r)
        p.end()
        self._bgpix = pm

    def start(self):
        self._build_stars()
        self._build()
        self.show()
        self.raise_()
        self._timer.start()

    def _tick(self):
        self._t += 0.033
        if self._t > 6.0:  # EN: boot show max ~6s / RU: показ максимум ~6 сек
            self._finish()
            return
        self.update()

    def _finish(self):
        self._timer.stop()
        eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(eff)
        self._fade = QPropertyAnimation(eff, b"opacity", self)
        self._fade.setDuration(450)
        self._fade.setStartValue(1.0)
        self._fade.setEndValue(0.0)
        self._fade.finished.connect(self._hide)
        self._fade.start()

    def _hide(self):
        self.hide()
        self.setGraphicsEffect(None)
        self.done.emit()

    # ---------- interaction / взаимодействие ----------
    def mouseMoveEvent(self, e):
        self._mouse = e.position()

    def leaveEvent(self, e):
        self._mouse = None

    def mousePressEvent(self, e):
        """EN: poke — burst nearby particles. RU: тык — разлетаются ближайшие."""
        pos = e.position()
        for p in self._parts:
            dx = p["tx"] - pos.x()
            dy = p["ty"] - pos.y()
            d = (dx * dx + dy * dy) ** 0.5
            if d < 110:
                f = (110 - d) / 110
                ang = (p["hue"] * 6.283) + self._t * 3
                p["bx"] += (dx / (d + 1)) * 90 * f + math.cos(ang) * 30 * f
                p["by"] += (dy / (d + 1)) * 90 * f + math.sin(ang) * 30 * f

    # ---------- drawing ----------
    def paintEvent(self, e):
        t = self._t
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        # EN: starfield backdrop / RU: звёздный фон
        qp.drawPixmap(0, 0, self._bgpix)

        # --- EN: ambient liquid rainbow blobs drifting behind / RU: жидкие радужные пятна сзади ---
        blob_a = max(0.0, 1.0 - t / 3.5)
        if blob_a > 0:
            for i in range(6):
                ang = t * 0.7 + i * 1.047
                bx = cx + math.cos(ang) * (w * 0.28 + math.sin(t + i) * 40)
                by = cy + math.sin(ang * 1.3) * (h * 0.22 + math.cos(t * 0.8 + i) * 30)
                col = QColor.fromHsvF(((i / 6 + t * 0.05) % 1.0), 0.85, 1.0)
                col.setAlpha(int(34 * blob_a))
                rg = QRadialGradient(bx, by, 190)
                rg.setColorAt(0, col)
                rg.setColorAt(1, QColor(0, 0, 0, 0))
                qp.fillRect(self.rect(), rg)

        # --- EN: particles — fly in, assemble, wobble, 3D depth / RU: частицы ---
        assembled = t > 2.6
        for p in self._parts:
            lt = max(0.0, min(1.0, (t - p["delay"]) / 0.85))
            ease = 1 - (1 - lt) ** 3  # easeOutCubic
            wx = p["tx"] + math.sin(t * 2 + p["hue"] * 9) * 1.6
            wy = p["ty"] + math.cos(t * 1.7 + p["hue"] * 7) * 1.6
            x = p["sx"] + (wx - p["sx"]) * ease + p["bx"]
            y = p["sy"] + (wy - p["sy"]) * ease + p["by"]
            # EN: mouse repulsion / RU: отталкивание от курсора
            if self._mouse is not None and assembled:
                # EN: word scatters just by moving the cursor — no clicks needed
                # RU: слово рассыпается от ДВИЖЕНИЯ мыши, без кликов
                dx = x - self._mouse.x()
                dy = y - self._mouse.y()
                d = (dx * dx + dy * dy) ** 0.5
                if d < 95 and d > 0.01:
                    f = (95 - d) / 95
                    x += dx / d * f * 22
                    y += dy / d * f * 22
            # EN: burst decay / RU: затухание разлёта
            p["bx"] *= 0.90
            p["by"] *= 0.90

            hue = p["hue"]
            # EN: strictly black & white — gray shades only / RU: строго ч/б — оттенки серого
            v = 0.72 + 0.28 * hue
            col = QColor.fromRgbF(v, v, v)
            dark = QColor.fromRgbF(v * 0.22, v * 0.22, v * 0.25)
            qp.setPen(Qt.NoPen)
            # EN: 3D volume — dark extruded copy behind / RU: объём — тёмная копия снизу-сзади
            qp.setBrush(dark)
            qp.drawEllipse(int(x) + 3, int(y) + 4, 5, 5)
            qp.setBrush(col)
            qp.drawEllipse(int(x), int(y), 4, 4)
            # EN: trail while flying / RU: шлейф в полёте
            if lt < 1.0:
                qp.setPen(QPen(col, 1))
                qp.drawLine(int(p["px"]), int(p["py"]), int(x), int(y))
            p["px"], p["py"] = x, y

        qp.end()


# ============================================================
# EN: WaveOverlay — theme switching as a liquid wave sweeping
#     across the screen (right side brings light, left brings dark).
# RU: WaveOverlay — смена темы жидкой волной: справа прибивает
#     светлую, слева увозит её и прибивает тёмную.
# ============================================================
class WaveOverlay(QWidget):
    finished = Signal()

    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self.hide()
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._p = 0.0
        self._f = 0.0
        self._to = 1.0
        self.anim = QPropertyAnimation(self, b"progress", self)
        self.anim.setDuration(1150)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

    def getP(self):
        return self._p

    def setP(self, v):
        self._p = v
        # EN: theme follows the wave / RU: тема едет вместе с волной
        self.theme.setT(self._f + (self._to - self._f) * v)
        self.update()

    progress = Property(float, getP, setP)

    def sweep(self, t_from, t_to):
        """EN: t_from -> t_to. dark->light wave rolls right-to-left, light->dark left-to-right.
        RU: тёмная→светлая: волна справа налево; светлая→тёмная: слева направо."""
        self._f, self._to = t_from, t_to
        self.show()
        self.raise_()
        self.anim.stop()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.finished.connect(self._end, type=Qt.UniqueConnection)
        self.anim.start()

    def _end(self):
        self.hide()
        self.finished.emit()

    def paintEvent(self, e):
        p = self._p
        if p <= 0.0 or p >= 1.0:
            return
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        light_side = self._to > self._f  # EN: dark->light / RU: тёмная→светлая
        front = w * (1 - p) if light_side else w * p

        # EN: wave body — translucent liquid band behind the crest
        # RU: тело волны — полупрозрачная жидкая полоса за гребнем
        path = QPainterPath()
        pts = []
        for i in range(33):
            y = h * i / 32
            fx = (
                front
                + math.sin(y * 0.045 + p * 7) * 26
                + math.sin(y * 0.013 + p * 3) * 14
            )
            pts.append((fx, y))
        path.moveTo(pts[0][0], -40)
        for fx, y in pts:
            path.lineTo(fx, y)
        path.lineTo(pts[-1][0], h + 40)
        if light_side:
            path.lineTo(w + 40, h + 40)
            path.lineTo(w + 40, -40)
        else:
            path.lineTo(-40, h + 40)
            path.lineTo(-40, -40)
        path.closeSubpath()
        grad = QLinearGradient(
            front - 160 if not light_side else front,
            0,
            front if not light_side else front + 160,
            0,
        )
        c1 = QColor(0, 229, 255, 70)
        c2 = QColor(255, 47, 214, 70)
        grad.setColorAt(0, c2 if light_side else c1)
        grad.setColorAt(1, c1 if light_side else c2)
        qp.fillPath(path, QBrush(grad))

        # EN: glowing crest / RU: светящийся гребень
        crest = QPainterPath()
        crest.moveTo(pts[0][0], pts[0][1])
        for fx, y in pts[1:]:
            crest.lineTo(fx, y)
        qp.setPen(QPen(QColor(235, 250, 255, 160), 3))
        qp.drawPath(crest)
        qp.setPen(QPen(QColor(0, 229, 255, 90), 7))
        qp.drawPath(crest)

        # EN: foam bubbles on the crest / RU: пузыри пены на гребне
        qp.setPen(Qt.NoPen)
        for i in range(12):
            y = (i * 97 + int(p * 500)) % h
            fx = (
                front
                + math.sin(y * 0.045 + p * 7) * 26
                + math.sin(y * 0.013 + p * 3) * 14
            )
            r = 2 + (i % 4)
            qp.setBrush(QColor(255, 255, 255, 70))
            qp.drawEllipse(int(fx + (14 if light_side else -14)), int(y), r * 2, r * 2)
        qp.end()


# ============================================================
# EN: Saper (Minesweeper) — a real, working game. XP desktop icon.
# RU: Сапёр — настоящая рабочая игра. Ярлык на рабочем столе XP.
# ============================================================
class CellButton(QPushButton):
    """EN: minesweeper cell with a hand-drawn icon (flag / mine).
    RU: клетка сапёра с нарисованной иконкой (флаг / мина)."""

    def __init__(self):
        super().__init__()
        self._icon = ""

    def set_icon(self, name):
        self._icon = name
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        if not self._icon:
            return
        p = QPainter(self)
        s = min(self.width(), self.height())
        if self._icon == "flag":
            p.setPen(QPen(Qt.black, max(2, s // 12)))
            p.drawLine(int(s * 0.38), int(s * 0.12), int(s * 0.38), int(s * 0.85))
            p.setBrush(QColor("#e00000"))
            p.setPen(Qt.NoPen)
            p.drawPolygon(
                QPolygon(
                    [
                        QPoint(int(s * 0.44), int(s * 0.1)),
                        QPoint(int(s * 0.88), int(s * 0.26)),
                        QPoint(int(s * 0.44), int(s * 0.44)),
                    ]
                )
            )
            p.setBrush(Qt.black)
            p.drawRect(int(s * 0.24), int(s * 0.82), int(s * 0.34), max(2, s // 10))
        elif self._icon == "mine":
            cx = cy = s / 2
            r = s * 0.26
            p.setPen(QPen(Qt.black, max(2, s // 14)))
            for a in range(8):
                ang = math.radians(a * 45)
                p.drawLine(
                    int(cx),
                    int(cy),
                    int(cx + math.cos(ang) * s * 0.44),
                    int(cy + math.sin(ang) * s * 0.44),
                )
            p.setBrush(Qt.black)
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))
            p.setBrush(QColor("#c0c0c0"))
            p.drawEllipse(
                int(cx - r * 0.35),
                int(cy - r * 0.55),
                max(2, int(r * 0.42)),
                max(2, int(r * 0.42)),
            )
        elif self._icon == "mine_red":
            p.fillRect(self.rect(), QColor("#e00000"))
            p.end()
            self._icon = "mine"
            self.paintEvent(e)
            return
        p.end()


class FaceButton(QPushButton):
    """EN: the smiley — normal / dead / cool(win). RU: смайлик — обычный / мёртвый / в очках."""

    def __init__(self):
        super().__init__()
        self._state = "normal"

    def set_state(self, st):
        self._state = st
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        s = min(self.width(), self.height())
        cx = cy = s / 2
        r = s * 0.36
        p.setBrush(QColor("#f8e000"))
        p.setPen(QPen(QColor("#000000"), 1))
        p.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))
        p.setPen(QPen(Qt.black, max(2, s // 14)))
        if self._state == "dead":
            for sx in (-1, 1):
                ex, ey = cx + sx * r * 0.42, cy - r * 0.25
                p.drawLine(int(ex - 3), int(ey - 3), int(ex + 3), int(ey + 3))
                p.drawLine(int(ex - 3), int(ey + 3), int(ex + 3), int(ey - 3))
            p.drawArc(
                int(cx - r * 0.5), int(cy + r * 0.15), int(r), int(r * 0.7), 0, 180 * 16
            )
        elif self._state == "win":
            p.setBrush(Qt.black)
            p.setPen(Qt.NoPen)
            p.drawRect(
                int(cx - r * 0.75), int(cy - r * 0.45), int(r * 1.5), int(r * 0.38)
            )
            p.setPen(QPen(Qt.black, max(2, s // 14)))
            p.drawArc(
                int(cx - r * 0.5),
                int(cy - r * 0.1),
                int(r),
                int(r * 0.8),
                180 * 16,
                180 * 16,
            )
        else:
            p.setBrush(Qt.black)
            p.setPen(Qt.NoPen)
            p.drawEllipse(
                int(cx - r * 0.5), int(cy - r * 0.4), max(2, s // 10), max(2, s // 10)
            )
            p.drawEllipse(
                int(cx + r * 0.3), int(cy - r * 0.4), max(2, s // 10), max(2, s // 10)
            )
            p.setPen(QPen(Qt.black, max(2, s // 14)))
            p.drawArc(
                int(cx - r * 0.5),
                int(cy - r * 0.35),
                int(r),
                int(r),
                200 * 16,
                140 * 16,
            )
        p.end()


class SaperGame(QDialog):
    """EN: classic Minesweeper — drawn icons, LCD counters, colored numbers.
    RU: классический Сапёр — нарисованные иконки, LCD-счётчики, цветные цифры."""

    NUM_COLORS = {
        1: "#0000ff",
        2: "#007b00",
        3: "#ff0000",
        4: "#00007b",
        5: "#7b0000",
        6: "#007b7b",
        7: "#000000",
        8: "#7b7b7b",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сапёр")
        self.setFixedSize(330, 420)
        self.setStyleSheet("""
QDialog { background: #c0c0c0; border-radius: 0; }
QLabel { color: #000000; font-weight: bold; }
QPushButton { border-radius: 0; }
""")
        self.N, self.MINES = 9, 10
        self.reset(first=True)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        top = QHBoxLayout()
        lcd = (
            "background: #000000; color: #ff0000; font-family: monospace;"
            " font-size: 20px; font-weight: bold; border: 2px inset #808080; padding: 2px 6px;"
        )
        self.mine_lbl = QLabel(f"{self.MINES:03d}")
        self.mine_lbl.setStyleSheet(lcd)
        face = FaceButton()
        face.setFixedSize(38, 38)
        face.setStyleSheet(
            "background: #c0c0c0; border: 2px outset #ffffff; border-radius: 0;"
        )
        face.clicked.connect(lambda: self.reset())
        self.face = face
        self.time_lbl = QLabel("000")
        self.time_lbl.setStyleSheet(lcd)
        top.addWidget(self.mine_lbl)
        top.addStretch(1)
        top.addWidget(face)
        top.addStretch(1)
        top.addWidget(self.time_lbl)
        lay.addLayout(top)
        field = QFrame()
        field.setStyleSheet("border: 3px inset #808080; background: #c0c0c0;")
        fl = QVBoxLayout(field)
        fl.setContentsMargins(6, 6, 6, 6)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        fl.addLayout(self.grid)
        lay.addWidget(field)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._build()

    def reset(self, first=False):
        self.t = 0
        self.over = False
        self.first = True
        self.mines = set(random.sample(range(self.N * self.N), self.MINES))
        self.opened = set()
        self.flags = set()
        if hasattr(self, "timer"):
            self.timer.stop()
            self.time_lbl.setText("000")
            self.mine_lbl.setText(f"{self.MINES:03d}")
            self.face.set_state("normal")
        if hasattr(self, "grid"):
            while self.grid.count():
                it = self.grid.takeAt(0)
                if it.widget():
                    it.widget().deleteLater()
            self._build()

    def _build(self):
        self.btns = []
        closed = "background: #c0c0c0; border: 2px outset #ffffff; border-radius: 0;"
        open_ = "background: #c0c0c0; border: 1px solid #808080; border-radius: 0;"
        self._st_closed = closed
        self._st_open = open_
        for i in range(self.N * self.N):
            b = CellButton()
            b.setFixedSize(30, 30)
            b.setStyleSheet(closed)
            b.setContextMenuPolicy(Qt.CustomContextMenu)
            b.clicked.connect(lambda _, i=i: self.open(i))
            b.customContextMenuRequested.connect(lambda _, i=i: self.flag(i))
            self.grid.addWidget(b, i // self.N, i % self.N)
            self.btns.append(b)

    def _tick(self):
        self.t = min(999, self.t + 1)
        self.time_lbl.setText(f"{self.t:03d}")

    def neighbors(self, i):
        r, c = divmod(i, self.N)
        return [
            nr * self.N + nc
            for nr in (r - 1, r, r + 1)
            for nc in (c - 1, c, c + 1)
            if (nr != r or nc != c) and 0 <= nr < self.N and 0 <= nc < self.N
        ]

    def _counts(self):
        self.cnt = {
            i: (
                0
                if i in self.mines
                else sum(n in self.mines for n in self.neighbors(i))
            )
            for i in range(self.N * self.N)
        }

    def open(self, i):
        if self.over or i in self.flags or i in self.opened:
            return
        if self.first:
            while i in self.mines:
                self.mines.remove(i)
                self.mines.add(
                    random.choice(
                        [
                            x
                            for x in range(self.N * self.N)
                            if x not in self.mines and x != i
                        ]
                    )
                )
            self._counts()
            self.first = False
            self.timer.start(1000)
        if i in self.mines:
            self.lose(i)
            return
        stack = [i]
        while stack:
            j = stack.pop()
            if j in self.opened:
                continue
            self.opened.add(j)
            b = self.btns[j]
            b.setEnabled(False)
            b.setStyleSheet(self._st_open)
            n = self.cnt[j]
            if n > 0:
                b.setText(str(n))
                b.setStyleSheet(
                    self._st_open + f" color: {self.NUM_COLORS.get(n, '#000')};"
                )
            else:
                for k in self.neighbors(j):
                    if k not in self.opened and k not in self.flags:
                        stack.append(k)
        if len(self.opened) == self.N * self.N - self.MINES:
            self.win()

    def flag(self, i):
        if self.over or i in self.opened:
            return
        b = self.btns[i]
        if i in self.flags:
            self.flags.discard(i)
            b.setText("")
            b.set_icon("")
        else:
            self.flags.add(i)
            b.set_icon("flag")
        self.mine_lbl.setText(f"{self.MINES - len(self.flags):03d}")

    def lose(self, hit):
        self.over = True
        self.timer.stop()
        self.face.set_state("dead")
        for i in self.mines:
            b = self.btns[i]
            b.setEnabled(False)
            b.setStyleSheet(
                self._st_open + (" background: #e00000;" if i == hit else "")
            )
            b.set_icon("mine")
        QMessageBox.information(
            self, "Сапёр", "Бум! Нажми на смайлик, чтобы сыграть ещё."
        )

    def win(self):
        self.over = True
        self.timer.stop()
        self.face.set_state("win")
        for i in self.mines:
            self.btns[i].set_icon("flag")
        QMessageBox.information(self, "Сапёр", f"Победа за {self.t} секунд!")


class XPBar(QFrame):
    """EN: XP taskbar — the whole navigation lives in the Start menu.
    RU: панель задач XP — вся навигация живёт в меню «Пуск»."""

    PAGES = [
        "Библиотека",
        "Обновления",
        "Оптимизация",
        "Установка",
        "Настройки",
        "Логи",
    ]

    def __init__(self, win):
        super().__init__(win.glass)
        self.win = win
        self.setFixedHeight(42)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 4, 10, 4)
        self.start_btn = QPushButton("start")
        self.start_btn.setFixedSize(92, 32)
        self.start_btn.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #7ec850, stop:1 #2e8f32);"
            "color: white; font-weight: bold; border-radius: 8px 16px 16px 8px;"
        )
        self.start_btn.clicked.connect(self.toggle_menu)
        lay.addWidget(self.start_btn)
        self.page_lbl = QLabel("")
        self.page_lbl.setStyleSheet("color: white; font-weight: bold;")
        lay.addWidget(self.page_lbl, 1)
        self.clock = QLabel("")
        self.clock.setStyleSheet("color: white; font-weight: bold;")
        lay.addWidget(self.clock)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._clock)
        self.timer.start(1000)
        self._clock()
        # меню Пуск — настоящий popup (клик вне = закрытие, как в Windows)
        self.menu = QFrame()
        self.menu.setWindowFlags(Qt.Popup)
        self.menu.setStyleSheet("background: #f4f1e8; border: 2px outset #ffffff;")
        ml = QVBoxLayout(self.menu)
        for idx, name in enumerate(self.PAGES):
            b = QPushButton(name)
            b.setStyleSheet(
                "text-align: left; padding: 8px 14px; background: #ece9d8;"
                "color: #000; border: 2px outset #ffffff;"
            )
            b.clicked.connect(lambda _, i=idx: self._go(i))
            ml.addWidget(b)
        sep = QLabel("─" * 12)
        sep.setStyleSheet("color: #808080")
        ml.addWidget(sep)
        for text, fn in (("Сапёр", self.saper), ("Выключить", self.win.close)):
            b = QPushButton(text)
            b.setStyleSheet(
                "text-align: left; padding: 8px 14px; background: #ece9d8;"
                "color: #000; border: 2px outset #ffffff;"
            )
            b.clicked.connect(fn)
            ml.addWidget(b)
        self.menu.setFixedWidth(210)
        self.menu.adjustSize()
        self.menu.hide()
        # ярлык Сапёра — сверху по центру
        self.saper_icon = QPushButton("(*)\nСапёр", win.glass)
        self.saper_icon.setFixedSize(76, 66)
        self.saper_icon.setStyleSheet(
            "background: transparent; border: none; color: white; font-weight: bold;"
        )
        self.saper_icon.clicked.connect(self.saper)
        self.raise_()

    def set_mode(self, mode):
        """EN: 'xp' | '95' | None — taskbar style and visibility per theme.
        RU: 'xp' | '95' | None — панель и стиль под тему."""
        self._mode = mode
        self.menu.hide()
        if mode is None:
            self.hide()
            self.saper_icon.hide()
            return
        if mode == "xp":
            self.start_btn.setText("start")
            self.start_btn.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #7ec850, stop:1 #2e8f32);"
                "color: white; font-weight: bold; border-radius: 8px 16px 16px 8px;"
            )
            self.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #316ac5, stop:1 #245edb);"
            )
        else:
            self.start_btn.setText("Пуск")
            self.start_btn.setStyleSheet(
                "background: #c0c0c0; color: #000; font-weight: bold; border: 2px outset #dfdfdf;"
            )
            self.setStyleSheet("background: #c0c0c0; border-top: 2px outset #ffffff;")
        self._rebuild_menu(mode)
        self.saper_icon.setVisible(mode == "xp")
        self.show()
        self.apply_geometry()
        self.raise_()

    def _rebuild_menu(self, mode):
        while self.menu.layout().count():
            it = self.menu.layout().takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        border = "2px outset #ffffff" if mode == "xp" else "2px outset #dfdfdf"
        for idx, name in enumerate(self.PAGES):
            b = QPushButton(name)
            b.setStyleSheet(
                f"text-align: left; padding: 8px 14px; background: #ece9d8;"
                f" color: #000; border: {border};"
            )
            b.clicked.connect(lambda _, i=idx: self._go(i))
            self.menu.layout().addWidget(b)
        if mode == "xp":
            b = QPushButton("Сапёр")
            b.setStyleSheet(
                f"text-align: left; padding: 8px 14px; background: #ece9d8;"
                f" color: #000; border: {border};"
            )
            b.clicked.connect(self.saper)
            self.menu.layout().addWidget(b)
        b = QPushButton("Выключить")
        b.setStyleSheet(
            f"text-align: left; padding: 8px 14px; background: #ece9d8;"
            f" color: #000; border: {border};"
        )
        b.clicked.connect(self.win.close)
        self.menu.layout().addWidget(b)
        self.menu.adjustSize()

    def apply_geometry(self):
        gw, gh = self.win.glass.width(), self.win.glass.height()
        self.setGeometry(0, gh - 42, gw, 42)
        self.saper_icon.move(int(gw * 0.5 - 38), 56)

    def toggle_menu(self):
        if self.menu.isVisible():
            self.menu.hide()
            return
        g = self.start_btn.mapToGlobal(QPoint(0, 0))
        self.menu.adjustSize()
        self.menu.move(int(g.x()), int(g.y()) - self.menu.height())
        self.menu.show()

    def _go(self, idx):
        self.win.nav.setCurrentRow(idx)
        self.page_lbl.setText("▸ " + self.PAGES[idx])
        self.menu.hide()

    def saper(self):
        self.menu.hide()
        if self.win.theme.palette_name() != "Windows XP":
            return
        SaperGame(self.win).exec()

    def _clock(self):
        import time as _t

        self.clock.setText(_t.strftime("%H:%M"))


# ============================================================
# EN: frameless title bar. RU: кастомный заголовок.
# ============================================================
class TitleBar(QFrame):
    def __init__(self, win):
        super().__init__()
        self.win = win
        self.setObjectName("titlebar")
        self.setFixedHeight(44)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 4, 8, 4)
        logo = QLabel("◆ ZAPUSK")
        logo.setStyleSheet(
            "font-weight:800; font-size:14px; letter-spacing:3px; color:#00e5ff;"
        )
        lay.addWidget(logo)
        lay.addStretch(1)
        # EN: language selector / RU: выбор языка
        self.combo_lang = QComboBox()
        for code, (n, fl) in i18n.LANGS.items():
            self.combo_lang.addItem(f"{fl} {n}", code)
        self.combo_lang.setCurrentIndex(
            max(list(i18n.LANGS.keys()).index(i18n.current()), 0)
        )
        self.combo_lang.setFixedWidth(150)
        self.combo_lang.setToolTip(_("Language"))
        self.combo_lang.currentIndexChanged.connect(
            lambda i: win.set_language(self.combo_lang.itemData(i))
        )
        lay.addWidget(self.combo_lang)
        # EN: palette selector / RU: выбор палитры
        self.combo_theme = QComboBox()
        for pi, (nm, _dk, _lt) in enumerate(PALETTES):
            self.combo_theme.addItem(f"🎨 {nm}", pi)
        self.combo_theme.setCurrentIndex(win.theme._pal)
        self.combo_theme.setFixedWidth(150)
        self.combo_theme.setToolTip(_("Theme"))
        self.combo_theme.currentIndexChanged.connect(
            lambda i: win.theme.set_palette(self.combo_theme.itemData(i))
        )
        lay.addWidget(self.combo_theme)
        self.btn_theme = QPushButton("🌙")
        self.btn_theme.setObjectName("ghost")
        self.btn_theme.setToolTip("Dark / Light")
        self.btn_theme.clicked.connect(win.toggle_theme)
        lay.addWidget(self.btn_theme)
        for sym, fn, tip in (
            ("—", win.showMinimized, "Свернуть / Minimize"),
            ("▢", win.toggle_max, "Развернуть / Maximize"),
            ("✕", win.close, "Закрыть / Close"),
        ):
            b = QPushButton(sym)
            b.setObjectName("ghost")
            b.setToolTip(tip)
            b.setFixedSize(38, 32)
            b.clicked.connect(fn)
            lay.addWidget(b)
        self._drag = None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = (
                e.globalPosition().toPoint() - self.win.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, e):
        if self._drag is not None and e.buttons() & Qt.LeftButton:
            self.win.move(e.globalPosition().toPoint() - self._drag)

    def mouseDoubleClickEvent(self, e):
        self.win.toggle_max()


# ============================================================
# EN: main window. RU: главное окно.
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1100, 700)
        self.setMinimumSize(QSize(940, 600))
        self._max = False

        self.theme = (
            Theme()
        )  # EN: theme must exist before TitleBar / RU: тема нужна до TitleBar
        # EN: neon carbon frame (paints its own background+border)
        # RU: неоновая карбоновая рамка (рисует фон и подсветку сама)
        self.glass = NeonFrame()
        root = QVBoxLayout(self.glass)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.titlebar = TitleBar(self)
        root.addWidget(self.titlebar)

        body = QHBoxLayout()
        body.setContentsMargins(14, 2, 14, 14)
        root.addLayout(body, 1)

        navw = QFrame()
        navw.setObjectName("nav")
        navw.setFixedWidth(210)
        self.navw = navw
        nl = QVBoxLayout(navw)
        self.nav = QListWidget()
        self.nav.addItems(
            [
                "🎮  " + _("Library"),
                "🔄  " + _("Updates"),
                "🚀  " + _("Optimization"),
                "⚙️  " + _("Setup"),
                "🔧  " + _("Settings"),
                "📋  " + _("Logs"),
            ]
        )
        self.nav.currentRowChanged.connect(self.switch_page)
        nl.addWidget(self.nav)
        body.addWidget(navw)

        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)

        self._build_library()
        self._build_updates()
        self._build_optimize()
        self._build_setup()
        self._build_settings_tab()
        self._build_logs()

        self.setCentralWidget(self.glass)

        # EN: no splash — start straight to the app. RU: без заставки — сразу в приложение
        self._splashed = True
        self.wave = WaveOverlay(self.glass, None)  # theme проставим в run_gui
        self.xpbar = XPBar(self)  # панель задач Windows XP
        self.stack.setGraphicsEffect(None)
        self.nav.setCurrentRow(0)
        _nm = self.theme.palette_name()
        _mode = "xp" if _nm == "Windows XP" else ("95" if _nm == "Windows 95" else None)
        self.xpbar.set_mode(_mode)
        self.navw.setVisible(_mode is None)
        self.refresh()
        self.refresh_updates()
        self.refresh_optimize()

    def showEvent(self, e):
        super().showEvent(e)
        self.stack.show()  # EN: no splash — content immediately / RU: без заставки
        if hasattr(self, "xpbar") and self.xpbar._mode is not None:
            self.xpbar.apply_geometry()
            self.xpbar.raise_()

    def _reveal(self):
        """EN: after splash — fade the main content in. RU: после сплэша плавно показываем окно."""
        self.glass.set_anim(False)
        self.stack.show()
        eff = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(eff)
        self._anim3 = QPropertyAnimation(eff, b"opacity", self)
        self._anim3.setDuration(500)
        self._anim3.setStartValue(0.0)
        self._anim3.setEndValue(1.0)
        self._anim3.finished.connect(lambda: self.stack.setGraphicsEffect(None))
        self._anim3.start()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, "wave"):
            self.wave.setGeometry(self.glass.rect())
        if hasattr(self, "xpbar"):
            self.xpbar.apply_geometry()

    def closeEvent(self, e):
        try:
            hx = bytes(self.saveGeometry().toHex()).decode()
            i18n.save("geometry", hx)
        except Exception:
            pass
        super().closeEvent(e)

    def toggle_max(self):
        self._max = not self._max
        self.showMaximized() if self._max else self.showNormal()

    def set_language(self, code):
        """EN: switch UI language (restart to fully apply). RU: смена языка (нужен перезапуск)."""
        if code and code != i18n.current():
            i18n.set_lang(code)
            QMessageBox.information(
                self,
                "Zapusk",
                "Язык сохранён. Перезапусти приложение.\nLanguage saved. Restart the app.",
            )

    def toggle_theme(self):
        """EN: switch theme with a liquid side wave. RU: смена темы жидкой боковой волной."""
        if self.wave.anim.state() == QPropertyAnimation.Running:
            return
        cur = self.theme.t
        target = 0.0 if cur > 0.5 else 1.0
        self.wave.setGeometry(self.glass.rect())
        self.wave.sweep(cur, target)
        self.titlebar.btn_theme.setText("☀️" if target == 1.0 else "🌙")

    def mouseMoveEvent(self, e):
        """EN: cursor parallax — background slides under the mouse.
        RU: параллакс от курсора — фон плывёт за мышью."""
        nx = e.position().x() / max(self.width(), 1) * 2 - 1
        ny = e.position().y() / max(self.height(), 1) * 2 - 1
        self.glass.set_parallax(nx, ny)
        super().mouseMoveEvent(e)

    # ---------- animated page switch / плавный переход ----------
    def switch_page(self, i):
        if i == self.stack.currentIndex():
            return
        eff = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(eff)
        self._anim = QPropertyAnimation(eff, b"opacity", self)
        self._anim.setDuration(100)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(lambda: self._page_in(i))
        self._anim.start()

    def _page_in(self, i):
        self.stack.setCurrentIndex(i)
        if i == 1:
            self.refresh_updates()
        if i == 2:
            self.refresh_optimize()
        eff = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(eff)
        self._anim2 = QPropertyAnimation(eff, b"opacity", self)
        self._anim2.setDuration(150)
        self._anim2.setStartValue(0.0)
        self._anim2.setEndValue(1.0)
        self._anim2.finished.connect(lambda: self.stack.setGraphicsEffect(None))
        self._anim2.start()

    # ================= БИБЛИОТЕКА / LIBRARY =================
    def _build_library(self):
        p = QWidget()
        lay = QVBoxLayout(p)
        top = QHBoxLayout()
        title = QLabel(_("My games"))
        title.setObjectName("big")
        add = QPushButton("＋ " + _("Add game"))
        add.setObjectName("primary")
        add.clicked.connect(lambda: self.add_game(""))
        ref = QPushButton(_("Refresh"))
        ref.clicked.connect(self.refresh)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 поиск по играм...")
        self.search.setFixedWidth(200)
        self.search.textChanged.connect(self.refresh)
        imp = QPushButton("📥 " + _("Import games"))
        imp.clicked.connect(self.import_games)
        top.addWidget(self.search)
        top.addStretch(1)
        top.addWidget(ref)
        top.addWidget(imp)
        top.addWidget(add)
        lay.addLayout(top)
        hint = QLabel(_("Drop hint"))
        hint.setObjectName("muted")
        lay.addWidget(hint)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.grid_host)
        lay.addWidget(scroll, 1)
        self.stack.addWidget(p)

    def refresh(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        gs = library.games()
        q = getattr(self, "search", None)
        if q and q.text().strip():
            needle = q.text().strip().lower()
            gs = [g for g in gs if needle in g["name"].lower()]
        if not gs:
            hint = QLabel(_("Empty"))
            hint.setObjectName("muted")
            self.grid.addWidget(hint, 0, 0)
        for i, g in enumerate(gs):
            self.grid.addWidget(Card(g, self), i // 3, i % 3)
        self.refresh_log_combo()

    def import_games(self):
        """EN: scan all stores and import games. RU: скан всех магазинов + импорт."""
        from zapusk.core import importer

        self.setup_out.setPlainText(
            "🔍 Сканирую Steam, Heroic, Lutris, Bottles, GOG..."
        )
        self.nav.setCurrentRow(3)

        def job():
            found = importer.scan(progress=lambda m: self._imp_line.sig.emit(m))
            n = importer.import_all(
                found, progress=lambda m: self._imp_line.sig.emit(m)
            )
            self._imp_line.sig.emit(
                f"\n✅ Готово: найдено {len(found)}, добавлено {n}. Обнови библиотеку."
            )

        self._imp_line = _Signal()
        self._imp_line.sig.connect(
            lambda m: (self.setup_out.append(m), QApplication.processEvents())
        )
        self._imp_worker = Worker(job)
        self._imp_worker.start()

    def add_game(self, initial_exe=""):
        d = AddGameDialog(self, initial_exe)
        if d.exec():
            self.refresh()
            if d.result_game and bool(_cfg("auto_fix", True)):
                self.fix_and_launch(
                    d.result_game, launch=False
                )  # EN: auto-config, no start

    def remove_game(self, game):
        """EN: remove game from library, optionally delete files/prefix.
        RU: удалить игру из списка, опционально с файлами и префиксом."""
        g = library.get(game["name"]) if isinstance(game, dict) else None
        g = g or game
        if not g:
            return
        dlg = RemoveGameDialog(g, self)
        if not dlg.exec():
            return
        if dlg.cb_files.isChecked():
            d = g.get("workdir") or str(pathlib.Path(g["exe"]).parent)
            if (
                QMessageBox.question(
                    self,
                    "Zapusk",
                    f"Точно удалить ФАЙЛЫ игры?\n{d}\n\nThis will delete the game folder!",
                )
                != QMessageBox.Yes
            ):
                return
            shutil.rmtree(d, ignore_errors=True)
        if dlg.cb_prefix.isChecked():
            if not g.get("shared_prefix"):
                shutil.rmtree(PREFIXES_DIR / g["slug"], ignore_errors=True)
            else:
                QMessageBox.information(
                    self, "Zapusk", "Префикс общий — оставил его. / Shared prefix kept."
                )
        library.remove(g["name"])
        self.refresh()

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):
        for url in e.mimeData().urls():
            p = pathlib.Path(url.toLocalFile())
            if not p.exists():
                continue
            if p.is_file() and p.suffix.lower() == ".exe":
                self.add_game(str(p))
                # автоопределение сработает внутри диалога
            elif p.is_dir():
                found = library.scan_folder(str(p))
                if found:
                    self.add_game(found[0])
                else:
                    QMessageBox.information(
                        self, "Zapusk", f"Нет подходящего .exe / No game .exe:\n{p}"
                    )

    # ================= ОБНОВЛЕНИЯ / UPDATES =================
    def _build_updates(self):
        p = QWidget()
        lay = QVBoxLayout(p)
        t = QLabel(_("Updates"))
        t.setObjectName("big")
        lay.addWidget(t)
        d = QLabel(
            "Раннеры и трансляторы — Zapusk качает сам и следит за версиями.\nRunners & translation layers — auto-download with version tracking."
        )
        d.setObjectName("muted")
        lay.addWidget(d)

        ge = QFrame()
        ge.setObjectName("panel")
        gl = QVBoxLayout(ge)
        gl.addWidget(QLabel("🎮 " + _("GEProton")))
        self.ge_status = QLabel("…")
        self.ge_status.setObjectName("muted")
        self.ge_status.setWordWrap(True)
        gl.addWidget(self.ge_status)
        self.ge_progress = QProgressBar()
        self.ge_progress.hide()
        gl.addWidget(self.ge_progress)
        row = QHBoxLayout()
        self.btn_ge = QPushButton("⬇ " + _("Download latest"))
        self.btn_ge.setObjectName("primary")
        self.btn_ge.clicked.connect(self.update_ge)
        row.addWidget(self.btn_ge)
        row.addStretch(1)
        gl.addLayout(row)
        lay.addWidget(ge)

        dx = QFrame()
        dx.setObjectName("panel")
        dl2 = QVBoxLayout(dx)
        dl2.addWidget(QLabel("🧊 " + _("DXVK card")))
        self.dx_status = QLabel("…")
        self.dx_status.setObjectName("muted")
        self.dx_status.setWordWrap(True)
        dl2.addWidget(self.dx_status)
        row2 = QHBoxLayout()
        btn_check = QPushButton("🔎 " + _("Check"))
        btn_check.clicked.connect(self.refresh_updates)
        btn_up = QPushButton("⬆ " + _("Update pm"))
        btn_up.setObjectName("primary")
        btn_up.clicked.connect(self.update_pacman)
        row2.addWidget(btn_check)
        row2.addWidget(btn_up)
        row2.addStretch(1)
        dl2.addLayout(row2)
        lay.addWidget(dx)

        lay.addStretch(1)
        self.stack.addWidget(p)

    def _restyle(self, lbl, objname):
        """EN: force Qt to re-apply the #ok/#warn/#err color. RU: принудительно перекрасить."""
        lbl.setObjectName(objname)
        lbl.style().unpolish(lbl)
        lbl.style().polish(lbl)

    def refresh_updates(self):
        from zapusk.core import runners

        inst = runners.installed_ge()
        try:
            tag, _, _ = runners.latest_ge_proton()
            if inst:
                self.ge_status.setText(
                    f"Установлен / Installed: {inst}   •   Последний / Latest: {tag}"
                )
                self._restyle(self.ge_status, "ok" if inst == tag else "warn")
            else:
                self.ge_status.setText(
                    f"Не установлен / Not installed   •   Последний / Latest: {tag}"
                )
                self._restyle(self.ge_status, "err")
        except Exception as e:
            self.ge_status.setText(
                f"⚠ Нет связи с GitHub / Cannot reach GitHub: {e}\n"
                "Проверь интернет / Check your connection."
            )
            self._restyle(self.ge_status, "warn")
        try:
            dv = runners.pacman_ver("dxvk")
            vp = runners.pacman_ver("vkd3d-proton")
            ld = runners.latest_dxvk()
            lv = runners.latest_vkd3d()

            def stat(cur, latest, name):
                if not cur:
                    return f"{name}: ❌ не установлен / not installed"
                return f"{name}: {cur} (latest: {latest})"

            self.dx_status.setText(
                stat(dv, ld, "DXVK") + "\n" + stat(vp, lv, "VKD3D-Proton")
            )
            self._restyle(self.dx_status, "ok" if dv and vp else "warn")
        except Exception as e:
            self.dx_status.setText(f"Проверка не удалась / Check failed: {e}")
            self._restyle(self.dx_status, "warn")

    def update_ge(self):
        """EN: download & install GE-Proton with progress and clear errors.
        RU: качаем GE-Proton с прогрессом и понятными ошибками."""
        from zapusk.core import runners

        def job(emit):
            try:
                emit("Запрос версии / Querying version…")
                tag, url, size = runners.latest_ge_proton()
                emit(f"Последний релиз / Latest: {tag}  ({size // 1048576} MB)")
                tmp = pathlib.Path(tempfile.gettempdir()) / f"{tag}.tar.xz"

                def prog(done, total):
                    self._ge_signal(int(done * 100 / total) if total else 0)

                emit("Скачивание / Downloading…")
                runners.download_file(url, tmp, prog)
                self._ge_signal(100)
                emit(f"Распаковка / Extracting {tag}…")
                runners.install_ge(
                    tmp, lambda i, n: self._ge_signal(int(i * 100 / max(n, 1)))
                )
                tmp.unlink(missing_ok=True)
                emit(f"✅ Установлен / Installed: {tag}")
                return 0
            except Exception as e:
                emit(f"❌ Ошибка / Error: {e}")
                ok2, msg = runners.protonup_install(emit)
                if ok2:
                    emit(f"✅ Через protonup / Via protonup: {msg}")
                    return 0
                emit("Поставь вручную / Install manually: yay -S protonup && protonup")
                return 1

        self.btn_ge.setEnabled(False)
        self.ge_progress.show()
        self._ge_signal(0)
        self._ge_thread = ShellThread(job)
        self._ge_thread.line.connect(self._ge_line)
        self._ge_thread.done.connect(self._ge_done)
        self._ge_thread.start()

    def _ge_signal(self, pct):
        self.ge_progress.setValue(pct)

    def _ge_line(self, s):
        self.ge_status.setText(s)
        self._restyle(self.ge_status, "muted")

    def _ge_done(self, code):
        self.btn_ge.setEnabled(True)
        self.ge_progress.hide()
        if code == 0:
            self.refresh_updates()
        # EN: on error keep the error text visible / RU: при ошибке текст ошибки остаётся

    def update_pacman(self):
        """EN: update dxvk/vkd3d via pacman with -Sy and fallbacks.
        RU: обновление dxvk/vkd3d через pacman: -Sy + запасные варианты."""
        self.dx_status.setText(
            "Обновление: pacman -Sy dxvk vkd3d-proton… (введи пароль)"
        )
        cmd = host_prefix() + [
            "pkexec",
            "sh",
            "-c",
            (
                "pacman -Sy --needed --noconfirm dxvk; "
                "pacman -S --needed --noconfirm vkd3d-proton || "
                "pacman -S --needed --noconfirm vkd3d || true"
            ),
        ]
        p = subprocess.Popen(cmd)
        p.wait()
        self.refresh_updates()
        from zapusk.core import runners

        if not runners.pacman_ver("vkd3d-proton") and not runners.pacman_ver("vkd3d"):
            self.dx_status.setText(
                self.dx_status.text()
                + "\n⚠ vkd3d-proton нет в твоих репозиториях — вручную: yay -S vkd3d-proton"
            )

    # ================= ОПТИМИЗАЦИЯ / OPTIMIZE =================
    def _build_optimize(self):
        p = QWidget()
        lay = QVBoxLayout(p)
        t = QLabel(_("Optimization title"))
        t.setObjectName("big")
        lay.addWidget(t)

        def panel(title, status_attr):
            f = QFrame()
            f.setObjectName("panel")
            box = QVBoxLayout(f)
            box.addWidget(QLabel(title))
            lbl = QLabel("…")
            lbl.setWordWrap(True)
            setattr(self, status_attr, lbl)
            box.addWidget(lbl)
            return f, box

        gov, gl = panel("🔥 " + _("Governor"), "gov_status")
        b = QPushButton("⚡ " + _("Enable Perf"))
        b.setObjectName("primary")
        b.clicked.connect(self.opt_governor)
        gl.addWidget(b)
        lay.addWidget(gov)

        sw, sl = panel("💾 " + _("Swappiness"), "sw_status")
        b2 = QPushButton("⚡ " + _("Set 10"))
        b2.setObjectName("primary")
        b2.clicked.connect(self.opt_swappiness)
        sl.addWidget(b2)
        lay.addWidget(sw)

        gm, ml = panel("🎯 " + _("GameMode daemon"), "gm_status")
        b3 = QPushButton("⚡ " + _("Enable"))
        b3.setObjectName("primary")
        b3.clicked.connect(self.opt_gamemode)
        ml.addWidget(b3)
        lay.addWidget(gm)

        fbsd, fl2 = panel("🐧 FreeBSD GPU Layer", "fbsd_gpu_status")
        bf = QPushButton("⚡ " + "Настроить драйверы GPU / Setup GPU drivers")
        bf.setObjectName("primary")
        bf.clicked.connect(self.fbsd_gpu)
        fl2.addWidget(bf)
        lay.addWidget(fbsd)

        sc, cl = panel("🧹 " + _("Shader cache"), "sc_status")
        b4 = QPushButton("🗑 " + _("Clear"))
        b4.clicked.connect(self.opt_clear_cache)
        cl.addWidget(b4)
        lay.addWidget(sc)

        lay.addStretch(1)
        self.stack.addWidget(p)

    def fbsd_gpu(self):
        """EN: run the FreeBSD GPU layer. RU: прослойка авто-драйверов FreeBSD."""
        import pathlib
        import subprocess

        script = (
            pathlib.Path(__file__).resolve().parent / "scripts" / "fbsd_gaming_gpu.sh"
        )
        QMessageBox.information(
            self,
            "Zapusk",
            "Запускаю FreeBSD GPU Layer в терминале (нужен root).\n"
            "Скрипт: определит карту, поставит её драйвер, удалит лишнее, проверит Vulkan.",
        )
        subprocess.Popen(
            ["x-terminal-emulator", "-e", f"sudo sh {script}"]
            if shutil.which("x-terminal-emulator")
            else ["sudo", "sh", str(script)]
        )

    def refresh_optimize(self):
        from zapusk.core import optimize

        gov = optimize.governor_get()
        if gov:
            self.gov_status.setText(f"Текущий / Current: {gov}")
            self._restyle(self.gov_status, "ok" if gov == "performance" else "warn")
        else:
            self.gov_status.setText("Не поддерживается / Not available")
            self._restyle(self.gov_status, "muted")
        sw = optimize.swappiness_get()
        self.sw_status.setText(f"Текущий / Current: {sw}")
        self._restyle(self.sw_status, "ok" if sw == "10" else "warn")
        gm = optimize.gamemode_active()
        self.gm_status.setText(
            "Активен / Active ✅" if gm else "Не активен / Inactive ❌"
        )
        self._restyle(self.gm_status, "ok" if gm else "err")
        gpu = optimize.vulkan_driver()
        if gpu:
            self.sc_status.setText(f"GPU: {gpu}")
            self._restyle(self.sc_status, "muted")
        import platform as _pf

        if not hasattr(self, "fbsd_gpu_status"):
            return
        if _pf.system() == "FreeBSD":
            self.fbsd_gpu_status.setText(
                "Система: FreeBSD ✅ — жми «⚡ Настроить драйверы GPU»"
            )
        else:
            self.fbsd_gpu_status.setText(
                "Слой для FreeBSD: детект карты, авто-драйверы, чистка лишних, тюнинг ядра (--kernel)"
            )
        self._restyle(self.fbsd_gpu_status, "muted")

    def opt_governor(self):
        from zapusk.core import optimize

        optimize.governor_set_performance()
        self.refresh_optimize()

    def opt_swappiness(self):
        from zapusk.core import optimize

        optimize.swappiness_set(10)
        self.refresh_optimize()

    def opt_gamemode(self):
        from zapusk.core import optimize

        optimize.gamemode_enable()
        self.refresh_optimize()

    def opt_clear_cache(self):
        from zapusk.core import optimize

        n = optimize.clear_shader_cache()
        self.sc_status.setText(f"Очищено / Cleared {n} ✅")
        self._restyle(self.sc_status, "ok")

    # ================= УСТАНОВКА / SETUP =================
    def _build_setup(self):
        p = QWidget()
        sl = QVBoxLayout(p)
        t = QLabel(_("Setup"))
        t.setObjectName("big")
        sl.addWidget(t)
        sd = QLabel(
            "Один раз: системный стек (Wine, DXVK, драйверы Vulkan). / One-time system setup."
        )
        sd.setObjectName("muted")
        sl.addWidget(sd)
        row = QHBoxLayout()
        self.btn_install = QPushButton("🔧 " + _("Install all"))
        self.btn_install.setObjectName("good")
        self.btn_install.clicked.connect(self.auto_install)
        btn_check = QPushButton("🔎 " + _("Check system"))
        btn_check.clicked.connect(lambda: self.run_doctor(silent=False))
        row.addWidget(self.btn_install)
        row.addWidget(btn_check)
        row.addStretch(1)
        sl.addLayout(row)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        sl.addWidget(self.progress)
        self.setup_out = QTextEdit()
        self.setup_out.setReadOnly(True)
        sl.addWidget(self.setup_out, 1)
        self.stack.addWidget(p)

    def auto_install(self):
        if not INSTALL_SCRIPT.exists():
            QMessageBox.warning(
                self, "Zapusk", f"Не найден / Not found:\n{INSTALL_SCRIPT}"
            )
            return
        self.setup_out.setPlainText(
            "Устанавливаю системный стек / Installing…\nВведи пароль / Enter password when asked.\n"
        )
        self.progress.show()
        self.btn_install.setEnabled(False)
        self._inst = AutoInstallThread()
        self._inst.line.connect(lambda s: self.setup_out.append(s))
        self._inst.done.connect(self._after_install)
        self._inst.start()

    def _after_install(self, code):
        self.progress.hide()
        self.btn_install.setEnabled(True)
        self.setup_out.append(
            f"\n{'✅' if code == 0 else '⚠'} Готово / Done (code {code}). Перезагрузись / Reboot, затем «Проверить систему»."
        )
        self.run_doctor(silent=True)

    def run_doctor(self, silent=False):
        from zapusk.core.system import doctor

        if not silent:
            self.setup_out.setPlainText("Проверяю / Checking…")
        QApplication.processEvents()
        self.setup_out.setPlainText(doctor())

    def self_update(self):
        """EN: check and self-update Zapusk. RU: проверить и установить обновление."""
        from zapusk.core import selfupdate

        reason = selfupdate.unsupported_reason()
        if reason:
            QMessageBox.information(self, "Zapusk", reason)
            return
        new, info = selfupdate.check()
        if not new:
            QMessageBox.information(
                self, "Zapusk", f"У вас актуальная версия. ({info})"
            )
            return
        if (
            QMessageBox.question(self, "Zapusk", f"Доступна {info}. Обновиться?")
            != QMessageBox.Yes
        ):
            return
        _ok, msg = selfupdate.download_and_install(progress=lambda m: print(m))
        QMessageBox.information(self, "Zapusk", msg)

    def _lib_backup(self, export):
        from zapusk.core.util import LIBRARY_FILE

        if export:
            path, _ = QFileDialog.getSaveFileName(
                self, "Экспорт библиотеки", "zapusk-library.json", "JSON (*.json)"
            )
            if path:
                import shutil

                shutil.copy(str(LIBRARY_FILE), path)
                QMessageBox.information(self, "Zapusk", "💾 Экспортировано: " + path)
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "Восстановить библиотеку", "", "JSON (*.json)"
            )
            if path:
                import shutil

                shutil.copy(path, str(LIBRARY_FILE))
                self.refresh()
                QMessageBox.information(self, "Zapusk", "📥 Библиотека восстановлена")

    # ================= ЛОГИ / LOGS =================
    def _build_logs(self):
        p = QWidget()
        lg = QVBoxLayout(p)
        lg.addWidget(QLabel(_("Logs")))
        self.log_combo = QComboBox()
        self.log_combo.currentTextChanged.connect(self.load_log)
        lg.addWidget(self.log_combo)
        self.log_out = QTextEdit()
        self.log_out.setReadOnly(True)
        lg.addWidget(self.log_out, 1)
        self.stack.addWidget(p)

    def refresh_log_combo(self):
        cur = self.log_combo.currentText()
        self.log_combo.blockSignals(True)
        self.log_combo.clear()
        self.log_combo.addItems([g["name"] for g in library.games()])
        if cur:
            self.log_combo.setCurrentText(cur)
        self.log_combo.blockSignals(False)

    def load_log(self, name):
        g = library.get(name)
        if not g:
            return
        lp = LOGS_DIR / f"{g['slug']}.log"
        if lp.exists():
            txt = lp.read_text(encoding="utf-8", errors="replace")
            self.log_out.setPlainText("\n".join(txt.splitlines()[-400:]))
        else:
            self.log_out.setPlainText(_("No log"))

    def panic_kill(self, game):
        """EN: panic kill — SIGKILL every process of the game. RU: паник-килл."""
        from zapusk.core.killer import kill_game
        from zapusk.core.prefix import prefix_path

        g = library.get(game["name"]) or game
        if (
            QMessageBox.question(
                self, "Zapusk", f"{_('Kill all game processes?')}\n{g['name']}"
            )
            != QMessageBox.Yes
        ):
            return
        killed = kill_game(g, prefix_path(g["slug"], g.get("shared_prefix", False)))
        QMessageBox.information(
            self,
            "Zapusk",
            f"💀 {_('Killed processes')}: {len(killed)}"
            if killed
            else _("Nothing to kill"),
        )

    def opengamefolder(self, game):
        """EN: open game's workdir in the default file manager. RU: папка игры в файловом менеджере."""
        g = library.get(game["name"]) or game
        d = g.get("workdir") or str(pathlib.Path(g["exe"]).parent)
        for fm in ("dolphin", "nautilus", "thunar", "pcmanfm", "xdg-open"):
            if shutil.which(fm):
                subprocess.Popen([fm, d])
                return

    def show_logs(self, game):
        self.nav.setCurrentRow(5)
        self.log_combo.setCurrentText(game["name"])

    # ================= НАСТРОЙКИ / APP SETTINGS =================
    def _build_settings_tab(self):
        """EN: app settings tab — language, theme, behaviour. RU: вкладка настроек приложения."""
        p = QWidget()
        lay = QVBoxLayout(p)
        t = QLabel(_("Settings"))
        t.setObjectName("big")
        lay.addWidget(t)

        # --- language ---
        lang = QFrame()
        lang.setObjectName("panel")
        ll = QVBoxLayout(lang)
        ll.addWidget(QLabel("🌐 " + _("Language")))
        self.set_lang_combo = QComboBox()
        for code, (n, fl) in i18n.LANGS.items():
            self.set_lang_combo.addItem(f"{fl} {n}", code)
        self.set_lang_combo.setCurrentIndex(
            max(list(i18n.LANGS.keys()).index(i18n.current()), 0)
        )
        self.set_lang_combo.currentIndexChanged.connect(
            lambda i: self.set_language(self.set_lang_combo.itemData(i))
        )
        ll.addWidget(self.set_lang_combo)
        lay.addWidget(lang)

        # --- theme ---
        th = QFrame()
        th.setObjectName("panel")
        tl = QVBoxLayout(th)
        tl.addWidget(QLabel("🎨 " + _("Theme")))
        self.set_theme_combo = QComboBox()
        for pi, (nm, _dk, _lt) in enumerate(PALETTES):
            self.set_theme_combo.addItem(f"🎨 {nm}", pi)
        self.set_theme_combo.setCurrentIndex(self.theme._pal)
        self.set_theme_combo.currentIndexChanged.connect(
            lambda i: self.theme.set_palette(self.set_theme_combo.itemData(i))
        )
        tl.addWidget(self.set_theme_combo)
        row = QHBoxLayout()
        dl = QPushButton("🌙 / ☀️")
        dl.clicked.connect(self.toggle_theme)
        row.addWidget(dl)
        row.addStretch(1)
        tl.addLayout(row)
        lay.addWidget(th)

        # --- behaviour ---
        beh = QFrame()
        beh.setObjectName("panel")
        bl = QVBoxLayout(beh)
        bl.addWidget(QLabel("⚙️"))
        self.cb_autofix = QCheckBox(
            "Авто-установка зависимостей при добавлении игры / Auto-fix on add"
        )
        self.cb_autofix.setChecked(bool(_cfg("auto_fix", True)))
        self.cb_autofix.toggled.connect(lambda v: i18n.save("auto_fix", bool(v)))
        bl.addWidget(self.cb_autofix)
        self.cb_ownprefix = QCheckBox(
            "По умолчанию отдельный префикс / Own prefix by default"
        )
        self.cb_ownprefix.setChecked(bool(_cfg("own_prefix", True)))
        self.cb_ownprefix.toggled.connect(lambda v: i18n.save("own_prefix", bool(v)))
        bl.addWidget(self.cb_ownprefix)
        btn_data = QPushButton("📁 Папка данных / Open data folder")
        btn_data.clicked.connect(lambda: subprocess.Popen(["xdg-open", str(DATA_DIR)]))
        bl.addWidget(btn_data)
        lay.addWidget(beh)

        lay.addStretch(1)
        self.stack.addWidget(p)

    # ================= запуск / launch =================
    def launch(self, game):
        g = library.get(game["name"]) or game
        if not g:
            return
        from zapusk.core.runner import launch

        lp = launch(g)
        QMessageBox.information(
            self,
            "Zapusk",
            f"{_('Launched')}: {g['name']}\n{_('Log')}: {lp}\n\n{_('Not starting')}",
        )

    def fix_and_launch(self, game):
        if not game:
            return
        g = library.get(game["name"]) or game
        preset = PRESETS.get(g.get("preset", "dx11"), PRESETS["dx11"])
        prefix = prefix_path(g["slug"], g.get("shared_prefix", False))
        lp = LOGS_DIR / f"{g['slug']}.log"
        self.nav.setCurrentRow(3)
        self.setup_out.setPlainText(f"Чиним / Fixing '{g['name']}'… лог / log: {lp}\n")
        self.progress.show()
        self.btn_install.setEnabled(False)
        from zapusk.core.deps import fix_game

        def job():
            fix_game(
                prefix,
                preset,
                log=str(lp),
                progress=lambda m: self._fix_line.sig.emit(m),
            )

        self._fix_line = _Signal()
        self._fix_line.sig.connect(lambda m: self.setup_out.append(f"  → {m}"))
        self._worker = Worker(job)
        self._launch_after = launch
        self._worker.done.connect(lambda: self._after_fix(g, lp))
        self._worker.start()

    def _start_autofix(self, g):
        """EN: launch with auto-heal loop. RU: запуск с циклом авто-лечения."""
        from zapusk.core import autofix

        self.setup_out.append(
            "\n🔧 Авто-лечение: если игра вылетит — Zapusk сам поймёт, починит и перезапустит (до 4 попыток)"
        )

        def job():
            autofix.run_with_autofix(
                g, timeout=90, tries=4, progress=lambda m: self._fix_line.sig.emit(m)
            )

        self._fix_line = _Signal()
        self._fix_line.sig.connect(
            lambda m: (self.setup_out.append(m), QApplication.processEvents())
        )
        self._worker2 = Worker(job)
        self._worker2.start()

    def _after_fix(self, g, lp):
        self.progress.hide()
        self.btn_install.setEnabled(True)
        preset = PRESETS.get(g.get("preset", "dx11"), {})
        if preset.get("note"):
            self.setup_out.append(f"\n💡 {preset['note']}")
        if getattr(self, "_launch_after", True):
            if g.get("autofix", True):
                self._start_autofix(g)
            else:
                self.setup_out.append(f"\n✅ Запускаю / Launching {g['name']}…")
                self.launch(g)
        else:
            self.setup_out.append(f"\n✅ Готово! Жми ▶ {g['name']}")


def run_gui():
    """EN: app entry — animated theme + neon window. RU: вход — тема и неоновое окно."""
    ensure_dirs()
    app = QApplication(sys.argv)
    # EN: required for the window icon on Wayland/X11.
    # RU: нужно для иконки окна в Wayland/X11.
    app.setApplicationName("zapusk")
    app.setDesktopFileName("zapusk")
    app.setFont(QFont("Noto Sans", 10))
    win = MainWindow()
    theme = win.theme
    win.wave.theme = theme
    win.glass.theme = theme

    def _apply_theme():
        app.setStyleSheet(theme.qss())
        win.glass.invalidate()  # EN: frame bg follows theme / RU: фон едет за темой

    theme.changed.connect(_apply_theme)
    app.setStyleSheet(theme.qss())
    app.installEventFilter(ParallaxFilter(win))
    app.aboutToQuit.connect(lambda: [w.wait(4000) for w in list(_ACTIVE_WORKERS)])
    win.show()
    return app.exec()
