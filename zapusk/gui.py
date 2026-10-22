"""Zapusk 2.1 — cyberpunk carbon launcher / киберпанк-лаунчер.

EN: opaque carbon background, animated RGB neon window border, liquid-smooth
    theme transitions, drag&drop, one-click Fix & Launch, GE-Proton/DXVK
    updater, system optimization.
RU: непрозрачный карбоновый фон, анимированная RGB-неоновая рамка окна,
    плавные «жидкие» переходы темы, drag&drop, «Починить и запустить»,
    обновление GE-Proton/DXVK, оптимизация системы.
"""
# SPDX-License-Identifier: GPL-3.0-or-later
import sys, math, random, subprocess, shutil, pathlib, tempfile

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QFileDialog,
    QDialog, QDialogButtonBox, QMessageBox, QListWidget, QStackedWidget,
    QScrollArea, QFrame, QTextEdit, QInputDialog, QProgressBar,
    QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, QThread, Signal, QObject, Property, QTimer, QRect, QRectF, QPoint, QPoint,
                            QPropertyAnimation, QEasingCurve, QSize, QEvent)
from PySide6.QtGui import (QFont, QColor, QCursor, QDragEnterEvent, QDropEvent, QPainter,
                           QLinearGradient, QRadialGradient, QPen, QBrush,
                           QPainterPath, QPixmap, QImage)

from zapusk.core import library, i18n
_ = i18n.tr
from zapusk.core.presets import PRESETS
from zapusk.core.util import LOGS_DIR, PREFIXES_DIR, DATA_DIR, ensure_dirs


def _cfg(key, default=None):
    """EN: read app config. RU: читаем конфиг приложения."""
    try:
        import json as _j
        return _j.loads((DATA_DIR / "config.json").read_text(encoding="utf-8")).get(key, default)
    except Exception:
        return default
from zapusk.core.prefix import prefix_path, open_prefix
from zapusk.core.util import host_prefix

INSTALL_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "install.sh"           # универсальный
INSTALL_ARCH = pathlib.Path(__file__).resolve().parent.parent / "install_arch.sh"        # arch-only fallback

# ============================================================
# EN: 4 worlds x 2 modes (dark/light) — same scenes as the website.
# RU: 4 мира x 2 режима (тёмный/светлый) — те же сцены, что на сайте.
# ============================================================
WORLDS = [('Cyber',
  {'accent': '#00e5ff',
   'accent2': '#ff2fd6',
   'bg': '#07080c',
   'border': '#1b2135',
   'btn': 'rgba(255,255,255,18)',
   'btnhover': 'rgba(127,200,255,34)',
   'card': '#12141f',
   'err': '#ff3b5c',
   'input': '#0a0c12',
   'muted': '#5d6a86',
   'ok': '#00ff9d',
   'panel': '#0e1017',
   'scene': {'far': '#0a1020',
             'glow': '#00e5ff',
             'mid': '#070c18',
             'near': '#04060f',
             'sky1': '#03040a',
             'sky2': '#0a1226',
             'stars': 1,
             'win1': '#00e5ff',
             'win2': '#ff2fd6'},
   'text': '#e6f4ff',
   'warn': '#ffb020'},
  {'accent': '#0090c8',
   'accent2': '#c81e9e',
   'bg': '#dfe6f2',
   'border': '#c7d2e4',
   'btn': 'rgba(0,25,70,12)',
   'btnhover': 'rgba(0,140,200,40)',
   'card': '#ffffff',
   'err': '#d21f45',
   'input': '#e8edf5',
   'muted': '#5b6880',
   'ok': '#0a8f5b',
   'panel': '#f4f7fc',
   'scene': {'far': '#8fa3c4',
             'glow': '#9fc4ff',
             'mid': '#6e829f',
             'near': '#4d5f78',
             'sky1': '#a8bde0',
             'sky2': '#dfe9f8',
             'stars': 0,
             'win1': '#2a3550',
             'win2': '#7a4a8a'},
   'text': '#0c1220',
   'warn': '#b57500'}),
 ('Matrix',
  {'accent': '#00ff88',
   'accent2': '#aaff00',
   'bg': '#040805',
   'border': '#16301f',
   'btn': 'rgba(0,255,136,14)',
   'btnhover': 'rgba(0,255,136,34)',
   'card': '#0f1d13',
   'err': '#ff3b5c',
   'input': '#08120b',
   'muted': '#5f7a66',
   'ok': '#00ff9d',
   'panel': '#0a140d',
   'scene': {'rbg': '#010502', 'rfg': '#00ff88', 'rhead': '#d6ffe9'},
   'text': '#e4ffe9',
   'warn': '#ffb020'},
  {'accent': '#009a56',
   'accent2': '#5f8f00',
   'bg': '#eef5ee',
   'border': '#c9dfd0',
   'btn': 'rgba(0,120,60,12)',
   'btnhover': 'rgba(0,150,80,30)',
   'card': '#ffffff',
   'err': '#d21f45',
   'input': '#e2efe7',
   'muted': '#57705f',
   'ok': '#0a8f5b',
   'panel': '#f7fbf7',
   'scene': {'rbg': '#f2f7f2', 'rfg': '#009a56', 'rhead': '#003a1e'},
   'text': '#0c1f13',
   'warn': '#b57500'}),
 ('Sunset',
  {'accent': '#ff6b35',
   'accent2': '#b537f2',
   'bg': '#0d0708',
   'border': '#35202a',
   'btn': 'rgba(255,107,53,14)',
   'btnhover': 'rgba(255,107,53,34)',
   'card': '#1f1216',
   'err': '#ff4d6b',
   'input': '#140a0c',
   'muted': '#8a6f68',
   'ok': '#7dff8a',
   'panel': '#170d10',
   'scene': {'ground': '#2a0d16',
             'm1': '#5c1f2c',
             'm2': '#421522',
             'sky1': '#2a0e2e',
             'sky2': '#8a2b3a',
             'sky3': '#e86a3a',
             'sun1': '#fff3d6',
             'sun2': '#ffb056'},
   'text': '#ffece4',
   'warn': '#ffcf5c'},
  {'accent': '#d84f16',
   'accent2': '#8a2bbf',
   'bg': '#f7ece4',
   'border': '#e4cfc5',
   'btn': 'rgba(200,80,20,12)',
   'btnhover': 'rgba(220,90,25,30)',
   'card': '#ffffff',
   'err': '#d21f45',
   'input': '#f2e3dc',
   'muted': '#7d6259',
   'ok': '#1d8a4a',
   'panel': '#fdf6f0',
   'scene': {'ground': '#5c3226',
             'm1': '#b06a58',
             'm2': '#8a4a3e',
             'sky1': '#f2c4a0',
             'sky2': '#eda06a',
             'sky3': '#ffdba8',
             'sun1': '#fff8e0',
             'sun2': '#ffc478'},
   'text': '#241009',
   'warn': '#b57a00'}),
 ('Sakura',
  {'accent': '#ff7ab8',
   'accent2': '#7ad9ff',
   'bg': '#0e070c',
   'border': '#33202c',
   'btn': 'rgba(255,122,184,14)',
   'btnhover': 'rgba(255,122,184,34)',
   'card': '#1f111b',
   'err': '#ff5c7a',
   'input': '#150a12',
   'muted': '#8a6a80',
   'ok': '#8affc1',
   'panel': '#170d14',
   'scene': {'ground': '#2a0f20',
             'm1': '#55203c',
             'm2': '#3f1830',
             'moon': '#ffe9f2',
             'petals': ['#ffc7dd', '#ffabd0', '#ff9ec7', '#ff8dc0'],
             'sky1': '#241019',
             'sky2': '#6e2c4c',
             'sky3': '#c97697',
             'trunk': '#4a2b3a'},
   'text': '#ffe9f4',
   'warn': '#ffd25c'},
  {'accent': '#d63384',
   'accent2': '#2aa8d8',
   'bg': '#fbeef4',
   'border': '#e8ccd9',
   'btn': 'rgba(200,50,130,12)',
   'btnhover': 'rgba(220,60,140,30)',
   'card': '#ffffff',
   'err': '#d21f45',
   'input': '#f5e4ec',
   'muted': '#7d5f70',
   'ok': '#1d8a5a',
   'panel': '#fdf4f8',
   'scene': {'ground': '#7d4462',
             'm1': '#c98aa8',
             'm2': '#a86a8c',
             'moon': '#ffffff',
             'petals': ['#ffb8d4', '#ff9ec7', '#ff8dc0', '#ffd0e2'],
             'sky1': '#ffd9e8',
             'sky2': '#ffb3d1',
             'sky3': '#fff0f6',
             'trunk': '#5c3a4a'},
   'text': '#26091a',
   'warn': '#b58200'})]


PALETTES = [(n, d, l) for n, d, l in WORLDS]


def _lc(c1, c2, t):
    a, b = QColor(c1), QColor(c2)
    f = lambda x, y: int(x + (y - x) * t)
    return QColor(f(a.red(), b.red()), f(a.green(), b.green()), f(a.blue(), b.blue()))


def _lcs(c1, c2, t):  # вернуть строку hex
    return _lc(c1, c2, t).name()


def build_qss(th):
    """EN: stylesheet from (possibly interpolated) theme. RU: стили из темы."""
    a = th["accent"]
    def hx(k):
        v = th[k]
        return v if v.startswith("#") else "#20242c"
    return f"""
QWidget {{ background: transparent; color: {th['text']}; font-size: 13px;
         font-family: "Noto Sans", "Inter", sans-serif; }}
#glass {{ background: transparent; border-radius: 16px; }}
#titlebar {{ background: transparent; }}
#titlebar QLabel {{ color: {th['muted']}; font-weight: bold; letter-spacing: 3px; }}
#nav {{ background: rgba(255,255,255,10); border-radius: 12px; border: 1px solid {hx('border')}; }}
#nav QListWidget {{ background: transparent; border: none; outline: none; }}
#nav QListWidget::item {{ padding: 12px 14px; border-radius: 10px; margin: 3px 6px; color: {th['muted']}; }}
#nav QListWidget::item:hover {{ background: rgba(127,200,255,26); color: {th['text']}; }}
#nav QListWidget::item:selected {{ background: {a}; color: #04121a; font-weight: 700; }}
QPushButton {{ background: {th['btn']}; border: 1px solid {hx('border')};
             border-radius: 10px; padding: 8px 16px; }}
QPushButton:hover {{ background: {th['btnhover']}; border-color: {a}; }}
QPushButton:pressed {{ background: rgba(127,200,255,60); }}
QPushButton#primary {{ background: {a}; border: none; color: #04121a; font-weight: 700; }}
QPushButton#primary:hover {{ background: {_lcs(a, '#ffffff', 0.25)}; }}
QPushButton#good {{ background: {th['ok']}; border: none; color: #04140c; font-weight: 800; }}
QPushButton#good:hover {{ background: {_lcs(th['ok'], '#ffffff', 0.2)}; }}
QPushButton#ghost {{ background: transparent; border: none; font-size: 15px; }}
QPushButton#ghost:hover {{ background: rgba(127,200,255,40); border-radius: 8px; }}
QLineEdit, QComboBox, QTextEdit {{ background: {hx('input')}; border: 1px solid {hx('border')};
                                 border-radius: 10px; padding: 6px 10px; selection-background-color: {a}; }}
QComboBox QAbstractItemView {{ background: {hx('panel')}; }}
QFrame#card {{ background: {hx('card')}; border: 1px solid {hx('border')}; border-radius: 16px; }}
QFrame#card:hover {{ border-color: {a}; }}
QFrame#panel {{ background: {hx('panel')}; border: 1px solid {hx('border')}; border-radius: 14px; }}
QLabel#big {{ font-size: 22px; font-weight: 800; }}
QLabel#title {{ font-size: 15px; font-weight: 700; }}
QLabel#muted {{ color: {th['muted']}; font-size: 12px; }}
QLabel#chip {{ background: {th['accent2']}; color: white; border-radius: 8px; padding: 2px 8px; font-size: 11px; }}
QLabel#ok {{ color: {th['ok']}; font-weight: 600; }}
QLabel#warn {{ color: {th['warn']}; font-weight: 600; }}
QLabel#err {{ color: {th['err']}; font-weight: 600; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 8px; }}
QScrollBar::handle:vertical {{ background: rgba(127,200,255,70); border-radius: 4px; min-height: 30px; }}
QProgressBar {{ border: 1px solid {hx('border')}; border-radius: 8px; background: rgba(0,0,0,50); text-align: center; height: 14px; }}
QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {a}, stop:1 {th['accent2']}); border-radius: 8px; }}
"""


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
        return th

    def palette_name(self):
        return PALETTES[self._pal % len(PALETTES)][0]

    def set_palette(self, idx):
        idx = idx % len(PALETTES)
        if idx != self._pal:
            self._pal = idx
            i18n.save("theme", idx)
            self.changed.emit()

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
        out["world"] = self.palette_name().lower()
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
        self._cars = []   # EN: city traffic / RU: трафик города
        self._timer = QTimer(self)
        self._timer.setInterval(80)          # EN: one 12.5fps timer for everything
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
        elif world == "sakura":
            self._draw_sakura(pt, w, h, sc, ov)
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
        for depth, (kcol, kwin, wd, op) in enumerate((("far", .09, .12, .85), ("mid", .14, .16, .95), ("near", .2, .2, 1))):
            p.setOpacity(op)
            x = -40
            while x < w:
                bw = rnd.randint(120, 230)
                bh = rnd.randint(int(h * .18), int(h * (.6 if kcol == "near" else .42)))
                top = base - bh
                p.fillRect(x, top, bw, bh, QColor(sc[kcol]))
                if rnd.random() < .3:
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
        sx, sy = w // 2, int(h * .62)
        rg = QRadialGradient(sx, sy, 150)
        rg.setColorAt(0, QColor(sc["sun1"]))
        rg.setColorAt(0.55, QColor(sc["sun2"]))
        rg.setColorAt(1, QColor(255, 144, 64, 0))
        p.fillRect(pm_rect(w, h), rg)
        p.setPen(QPen(QColor(sc["m1"]).darker(120), 2))
        for bx, by in ((w*.2, h*.32), (w*.24, h*.3), (w*.72, h*.26), (w*.76, h*.28)):
            p.drawArc(int(bx), int(by), 16, 8, 0, 5760)
        for pts, col in (([(-40, h*.82), (w*.18, h*.48), (w*.33, h*.66), (w*.52, h*.42), (w*.75, h*.66), (w*.9, h*.5), (w+40, h*.7)], sc["m1"]),
                         ([(-40, h*.92), (w*.15, h*.68), (w*.35, h*.85), (w*.55, h*.6), (w*.74, h*.85), (w+40, h*.75)], sc["m2"])):
            p.fillRect(0, 0, 0, 0, QColor(0, 0, 0, 0))
            path = QPainterPath()
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.closeSubpath()
            p.fillPath(path, QColor(col))
        p.fillRect(0, int(h * .88), w, h, QColor(sc["ground"]))
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
        mx, my = int(w * .78), int(h * .2)
        rg = QRadialGradient(mx, my, 100)
        rg.setColorAt(0, QColor(sc["moon"]))
        rg.setColorAt(1, QColor(255, 233, 242, 0))
        p.fillRect(mx - 100, my - 100, 200, 200, rg)
        p.setPen(Qt.NoPen)
        for pts, col in (([(-60, h*.82), (w*.19, h*.52), (w*.39, h*.8), (w*.61, h*.48), (w*.81, h*.78), (w+60, h*.58)], sc["m1"]),
                         ([(-60, h*.95), (w*.16, h*.72), (w*.35, h*.92), (w*.61, h*.7), (w*.86, h*.9), (w+60, h*.8)], sc["m2"])):
            path = QPainterPath()
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.closeSubpath()
            p.fillPath(path, QColor(col))
        p.fillRect(0, int(h * .9), w, h, QColor(sc["ground"]))
        rnd = random.Random(11)
        for tx, ts in ((w*.13, 1.3), (w*.38, 1.0), (w*.6, 1.35), (w*.85, 1.05)):
            ty = h * .92
            p.setPen(QPen(QColor(sc["trunk"]), int(12 * ts), Qt.SolidLine, Qt.RoundCap))
            p.drawLine(int(tx), int(ty), int(tx), int(ty - 130 * ts))
            p.setPen(Qt.NoPen)
            for _ in range(70):
                a = rnd.uniform(0, 6.283)
                r = rnd.uniform(0, 1) ** .5
                cx = tx + 100 * ts * r * math.cos(a)
                cy = ty - 70 * ts - 80 * ts * r * math.sin(a)
                c = QColor(rnd.choice(sc["petals"]))
                c.setAlpha(rnd.randint(120, 240))
                p.setBrush(c)
                p.drawEllipse(int(cx), int(cy), int(rnd.uniform(8, 20) * ts), int(rnd.uniform(8, 20) * ts))

    # ---------- динамика: дождь, лепестки ----------
    def _rain_step(self):
        sc = self._sc()
        w, h = self.width(), self.height()
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
            p.setPen(QColor(sc["rhead"] if random.random() < .1 else sc["rfg"]))
            p.drawText(x, y, ch)
            if y > h and random.random() > .976:
                self._drops[i] = 0
            self._drops[i] += 1

    def _petals_step(self):
        w, h = self.width(), self.height()
        if not self._petals:
            self._petals = [dict(x=random.uniform(0, w), y=random.uniform(-h, 0),
                                 vy=random.uniform(.6, 1.8), ph=random.uniform(0, 6.28),
                                 r=random.uniform(0, 360), s=random.uniform(4, 9))
                            for _ in range(24)]
        for pt in self._petals:
            pt["y"] += pt["vy"]
            pt["x"] += math.sin(pt["y"] * .02 + pt["ph"]) * .8
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
        w, h = self.width(), self.height()
        if not self._cars:
            self._cars = [dict(x=random.uniform(0, w), d=random.choice([-1, 1]),
                               v=random.uniform(3.0, 5.5), lane=random.randint(0, 1))
                          for _ in range(7)]
        for c in self._cars:
            c["x"] += c["v"] * c["d"]
            if c["x"] < -30:
                c["x"] = w + 20
            if c["x"] > w + 30:
                c["x"] = -20

    def _draw_cars(self, p):
        w, h = self.width(), self.height()
        road_y = h - 46
        p.fillRect(0, road_y - 4, w, 34, QColor(0, 0, 0, 140))
        p.setPen(QPen(QColor(255, 220, 140, 60), 1, Qt.DashLine))
        p.drawLine(0, road_y + 13, w, road_y + 13)
        p.setPen(Qt.NoPen)
        for c in self._cars:
            y = road_y + 4 + c["lane"] * 14
            head = QColor(255, 244, 200, 230) if c["d"] > 0 else QColor(255, 90, 80, 230)
            tail = QColor(255, 60, 60, 200) if c["d"] > 0 else QColor(255, 244, 200, 200)
            hx = c["x"] + (6 if c["d"] > 0 else -2)
            tx = c["x"] - (2 if c["d"] > 0 else -6)
            p.setBrush(head)
            p.drawEllipse(int(hx), int(y), 4, 3)
            p.setBrush(tail)
            p.drawEllipse(int(tx), int(y), 3, 3)

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
        self._bkey = (self.theme.palette_name(), round(self.theme.t * 12) if self.theme else 0, self.size())

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
        if self._cache is None or self._cache.width() != self.width() + self._ov * 2 or key != self._scene_key:
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
            p.drawPixmap(int(-self._ov + self._px * -16), int(-self._ov + self._py * -12), self._cache)
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
# EN: generic workers. RU: фоновые потоки.
# ============================================================
class Worker(QThread):
    line = Signal(str)
    done = Signal()

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        self.fn()
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
            cmd = host_prefix() + ["pkexec", "bash", str(script)] + (["--auto"] if script == INSTALL_ARCH else [])
        elif shutil.which("pkexec"):
            cmd = ["pkexec", "bash", str(script)] + (["--auto"] if script == INSTALL_ARCH else [])
        else:
            term = None
            for t in (["konsole", "-e"], ["gnome-terminal", "--"], ["alacritty", "-e"],
                      ["kitty", "-e"], ["xterm", "-e"]):
                if shutil.which(t[0]):
                    term = t
                    break
            if not term:
                self.line.emit("❌ Нет pkexec/терминала — вручную: sudo bash install_arch.sh")
                self.done.emit(1)
                return
            cmd = term + ["sudo", "bash", str(INSTALL_SCRIPT), "--auto"]
        self.line.emit("$ " + " ".join(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, errors="replace", bufsize=1)
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
        t = QLabel(_("New game")); t.setObjectName("big"); lay.addWidget(t)
        self.name = QLineEdit(); self.name.setPlaceholderText(_("Name"))
        lay.addWidget(self.name)
        row = QHBoxLayout()
        self.exe = QLineEdit(initial_exe); self.exe.setPlaceholderText("Путь к .exe / Path to .exe")
        b = QPushButton("Обзор…"); b.clicked.connect(self.browse_exe)
        scan = QPushButton("📂 Сканировать папку"); scan.clicked.connect(self.scan)
        row.addWidget(self.exe, 1); row.addWidget(b); row.addWidget(scan)
        lay.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel(_("Preset") + ":"))
        self.preset = QComboBox()
        for k, v in PRESETS.items():
            self.preset.addItem(f"{v['label']}  ({k})", k)
        self.preset.setCurrentIndex(list(PRESETS.keys()).index("dx11"))
        row2.addWidget(self.preset, 1)
        btn_auto = QPushButton("🔍 Авто"); btn_auto.setToolTip("Определить по .exe")
        btn_auto.clicked.connect(self.auto_preset)
        btn_web = QPushButton("🌐 База"); btn_web.setToolTip("Спросить PCGamingWiki")
        btn_web.clicked.connect(self.web_preset)
        row2.addWidget(btn_auto)
        row2.addWidget(btn_web)
        lay.addLayout(row2)
        self.detect_label = QLabel(""); self.detect_label.setObjectName("muted")
        lay.addWidget(self.detect_label)
        self.own = QCheckBox(_("Own prefix"))
        self.own.setChecked(bool(_cfg("own_prefix", True)))
        lay.addWidget(self.own)
        self.args = QLineEdit(); self.args.setPlaceholderText(_("Arguments"))
        lay.addWidget(self.args)
        lay.addWidget(QLabel("💡 Потом жми «🚀 Починить и запустить»."))
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText(_("Add"))
        bb.button(QDialogButtonBox.Ok).setObjectName("primary")
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
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
        f, _ = QFileDialog.getOpenFileName(self, "Выбери .exe", str(pathlib.Path.home()), "Exe (*.exe)")
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
            QMessageBox.information(self, "Zapusk", "Подходящих .exe не нашлось / No game .exe found")
            return
        pick, ok = QInputDialog.getItem(self, "Найденные exe / Found", "Похоже на игру / Looks like the game:", found, 0, False)
        if ok and pick:
            self.exe.setText(pick)
            if not self.name.text():
                self.name.setText(pathlib.Path(pick).stem)
            self.auto_preset()

    def accept(self):
        if not self.exe.text() or not pathlib.Path(self.exe.text()).exists():
            QMessageBox.warning(self, "Zapusk", "Укажи существующий .exe / Choose a valid .exe")
            return
        if not self.name.text():
            self.name.setText(pathlib.Path(self.exe.text()).stem)
        try:
            g = library.add(self.name.text(), self.exe.text(), self.preset.currentData(),
                            shared_prefix=not self.own.isChecked(), args=self.args.text())
        except ValueError as e:
            QMessageBox.warning(self, "Zapusk", str(e))
            return
        self.result_game = g
        super().accept()


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
        self.exe = QLineEdit(g.get("exe", "")); lay.addWidget(self.exe)
        lay.addWidget(QLabel(_("Work dir") + ":"))
        self.workdir = QLineEdit(g.get("workdir", "")); lay.addWidget(self.workdir)
        lay.addWidget(QLabel(_("Arguments") + ":"))
        self.args = QLineEdit(g.get("args", "")); lay.addWidget(self.args)
        lay.addWidget(QLabel(_("Preset") + ":"))
        self.preset = QComboBox()
        for k, v in PRESETS.items():
            self.preset.addItem(f"{v['label']} ({k})", k)
        cur = g.get("preset", "dx11")
        self.preset.setCurrentIndex(list(PRESETS.keys()).index(cur) if cur in PRESETS else 1)
        lay.addWidget(self.preset)

        def chk(title, key, default=False):
            c = QCheckBox(title); c.setChecked(g.get(key, default))
            setattr(self, key, c); lay.addWidget(c)
            return c
        chk(_("GameMode"), "gamemode", True)
        chk(_("MangoHUD"), "mangohud")
        chk("Fsync", "fsync", True)
        chk("Esync", "esync", True)
        chk("DXVK HUD", "dxvk_hud")
        chk("Wine debug-лог", "debug")
        chk("Large Address Aware", "large_address")

        lay.addWidget(QLabel(_("Virtual desktop") + ":"))
        self.vdesk = QLineEdit(g.get("virtual_desktop", "")); lay.addWidget(self.vdesk)

        row = QHBoxLayout()
        for text, fn in (("🚀 " + _("Fix & Launch"), self.fix_run),
                         ("📁 " + _("Game folder"), self.opengame),
                         ("📂 " + _("Prefix"), self.openpfx),
                         ("🗑 " + _("Remove"), self.remove)):
            b = QPushButton(text); b.clicked.connect(fn); row.addWidget(b)
        lay.addLayout(row)

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Save).setText(_("Save"))
        bb.button(QDialogButtonBox.Save).setObjectName("primary")
        bb.accepted.connect(self.save); bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def collect(self):
        return dict(exe=self.exe.text().strip() or self.game["exe"],
                    workdir=self.workdir.text().strip() or str(pathlib.Path(self.exe.text()).parent),
                    args=self.args.text(), preset=self.preset.currentData(),
                    gamemode=self.gamemode.isChecked(), mangohud=self.mangohud.isChecked(),
                    fsync=self.fsync.isChecked(), esync=self.esync.isChecked(),
                    dxvk_hud=self.dxvk_hud.isChecked(), debug=self.debug.isChecked(),
                    large_address=self.large_address.isChecked(),
                    virtual_desktop=self.vdesk.text().strip())

    def save(self):
        library.update(self.game["name"], self.collect())
        self.accept()

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
        t = QLabel(f"🗑 {game['name']}"); t.setObjectName("big"); lay.addWidget(t)
        self.cb_files = QCheckBox(f"Удалить файлы игры / Delete game files\n{game.get('workdir','')}")
        self.cb_prefix = QCheckBox("Удалить префикс Wine / Delete Wine prefix")
        lay.addWidget(self.cb_files); lay.addWidget(self.cb_prefix)
        lay.addWidget(QLabel("Из списка игра удаляется всегда. / Always removed from the list."))
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText(_("Remove"))
        bb.button(QDialogButtonBox.Ok).setObjectName("danger")
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
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
        chip = QLabel(game.get("preset", "")); chip.setObjectName("chip")
        top.addWidget(chip); top.addStretch(1)
        lay.addLayout(top)
        t = QLabel(game["name"]); t.setObjectName("title"); t.setWordWrap(True)
        lay.addWidget(t)
        m = QLabel(pathlib.Path(game["exe"]).name); m.setObjectName("muted"); m.setWordWrap(True)
        lay.addWidget(m)
        lay.addStretch(1)
        row = QHBoxLayout()
        run = QPushButton("🚀 " + _("Fix & Launch")); run.setObjectName("good")
        run.clicked.connect(lambda: win.fix_and_launch(library.get(game["name"]) or game))
        row.addWidget(run)
        lay.addLayout(row)
        row2 = QHBoxLayout()
        quick = QPushButton("▶ " + _("Launch")); quick.clicked.connect(lambda: win.launch(game))
        cfg = QPushButton("⚙"); cfg.setFixedWidth(42); cfg.clicked.connect(lambda: win.settings(game))
        folder = QPushButton("📂"); folder.setFixedWidth(42)
        folder.setToolTip(_("Game folder"))
        folder.clicked.connect(lambda: win.opengamefolder(game))
        logs = QPushButton("📋"); logs.setFixedWidth(42); logs.clicked.connect(lambda: win.show_logs(game))
        rm = QPushButton("🗑"); rm.setFixedWidth(42)
        rm.setToolTip(_("Remove"))
        rm.setObjectName("danger")
        rm.clicked.connect(lambda: win.remove_game(game))
        row2.addWidget(quick); row2.addWidget(cfg); row2.addWidget(folder); row2.addWidget(logs); row2.addWidget(rm)
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
        self.setMouseTracking(True)   # EN: get moves WITHOUT pressed buttons
                                      # RU: движения БЕЗ зажатой кнопки
        self._parts = []
        self._t = 0.0
        self._mouse = None
        self._timer = QTimer(self)
        self._timer.setInterval(40)          # ~25 fps, только на старте / EN: only during boot
        self._timer.timeout.connect(self._tick)
        self._fade = None

    # ---------- particle setup ----------
    def _build(self):
        """EN: sample the wordmark pixels -> particle targets. RU: точки букв -> цели частиц."""
        w, h = self.width(), self.height()
        img = QImage(w, h, QImage.Format_ARGB32)
        img.fill(0)
        pt = QPainter(img)
        f = QFont("Noto Sans", 46)               # EN: smaller wordmark / RU: слово компактнее
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
        if len(targets) > 450:      # EN: cap particle count / RU: ограничиваем число частиц
            k = len(targets) // 450 + 1
            targets = targets[::k]

        self._parts = []
        n = len(targets)
        for i, (tx, ty) in enumerate(targets):
            side = i % 4            # EN: fly in from 4 sides / RU: влетают с 4 сторон
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
            hue = (i / max(n - 1, 1))          # EN: full rainbow / RU: вся радуга
            self._parts.append(dict(sx=sx, sy=sy, tx=tx, ty=ty, delay=delay,
                                    bx=0.0, by=0.0, px=sx, py=sy, hue=hue))

    # ---------- lifecycle ----------
    def _build_stars(self):
        """EN: opaque minimal backdrop (no stars, nothing leaks through).
           RU: непрозрачный минимальный фон — ничего не просвечивает."""
        pm = QPixmap(self.size())
        pm.fill(QColor(5, 6, 8, 255))
        self._bgpix = pm

    def start(self):
        self._build_stars()
        self._build()
        self.show()
        self.raise_()
        self._timer.start()

    def _tick(self):
        self._t += 0.033
        if self._t > 6.0:               # EN: boot show max ~6s / RU: показ максимум ~6 сек
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

        # --- EN: particles — fly in, assemble, wobble, 3D depth / RU: частицы ---
        assembled = t > 2.6
        for p in self._parts:
            lt = max(0.0, min(1.0, (t - p["delay"]) / 0.85))
            ease = 1 - (1 - lt) ** 3                      # easeOutCubic
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
        light_side = self._to > self._f
        front = w * (1 - p) if light_side else w * p

        def crest_x(y, off=0.0):
            return (front + off
                    + math.sin(y * 0.045 + p * 7.0) * 26
                    + math.sin(y * 0.013 + p * 3.0) * 14)

        def crest_path(off=0.0):
            path = QPainterPath()
            path.moveTo(crest_x(0, off), -40)
            for i in range(1, 33):
                y = h * i / 32
                path.lineTo(crest_x(y, off), y)
            return path

        # --- EN: trailing soft wave behind the main one / RU: вторая волна сзади ---
        trail = 85 if light_side else -85
        band = QPainterPath()
        band.moveTo(crest_x(0), -40)
        for i in range(33):
            y = h * i / 32
            band.lineTo(crest_x(y), y)
        for i in range(32, -1, -1):
            y = h * i / 32
            band.lineTo(crest_x(y, trail), y)
        band.closeSubpath()
        tg = QLinearGradient(crest_x(0, min(trail, 0)), 0, crest_x(0, max(trail, 0)), 0)
        tg.setColorAt(0, QColor(0, 229, 255, 30) if light_side else QColor(255, 47, 214, 30))
        tg.setColorAt(1, QColor(255, 47, 214, 30) if light_side else QColor(0, 229, 255, 30))
        qp.fillPath(band, QBrush(tg))

        # --- EN: main liquid body / RU: основное жидкое тело ---
        body = QPainterPath()
        body.moveTo(crest_x(0), -40)
        for i in range(33):
            y = h * i / 32
            body.lineTo(crest_x(y), y)
        body.lineTo(crest_x(h, 220 if light_side else -220), h + 40)
        body.lineTo(crest_x(0, 220 if light_side else -220), -40)
        body.closeSubpath()
        bg = QLinearGradient(crest_x(0, -140), 0, crest_x(0, 140), 0)
        bg.setColorAt(0.0, QColor(0, 229, 255, 40))
        bg.setColorAt(0.5, QColor(255, 255, 255, 46))
        bg.setColorAt(1.0, QColor(255, 47, 214, 40))
        qp.fillPath(body, QBrush(bg))

        # --- EN: soft shadow under the crest / RU: мягкая тень под гребнем ---
        qp.setPen(QPen(QColor(0, 0, 0, 46), 10))
        qp.drawPath(crest_path())

        # --- EN: glow crest / RU: светящийся гребень ---
        qp.setPen(QPen(QColor(0, 229, 255, 70), 7))
        qp.drawPath(crest_path())

        # --- EN: specular highlight (liquid-glass shine) / RU: блик жидкого стекла ---
        qp.setPen(QPen(QColor(255, 255, 255, 150), 2))
        qp.drawPath(crest_path(3 if light_side else -3))

        # --- EN: foam bubbles / RU: пена ---
        qp.setPen(Qt.NoPen)
        for i in range(14):
            y = (i * 89 + int(p * 620)) % h
            fx = crest_x(y) + (16 if light_side else -16)
            r = 2 + (i % 4)
            qp.setBrush(QColor(255, 255, 255, 80))
            qp.drawEllipse(int(fx), int(y), r * 2, r * 2)
        qp.end()


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
        t = QLabel(_("New game")); t.setObjectName("big"); lay.addWidget(t)
        self.name = QLineEdit(); self.name.setPlaceholderText(_("Name"))
        lay.addWidget(self.name)
        row = QHBoxLayout()
        self.exe = QLineEdit(initial_exe); self.exe.setPlaceholderText("Путь к .exe / Path to .exe")
        b = QPushButton("Обзор…"); b.clicked.connect(self.browse_exe)
        scan = QPushButton("📂 Сканировать папку"); scan.clicked.connect(self.scan)
        row.addWidget(self.exe, 1); row.addWidget(b); row.addWidget(scan)
        lay.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel(_("Preset") + ":"))
        self.preset = QComboBox()
        for k, v in PRESETS.items():
            self.preset.addItem(f"{v['label']}  ({k})", k)
        self.preset.setCurrentIndex(list(PRESETS.keys()).index("dx11"))
        row2.addWidget(self.preset, 1)
        btn_auto = QPushButton("🔍 Авто"); btn_auto.setToolTip("Определить по .exe")
        btn_auto.clicked.connect(self.auto_preset)
        btn_web = QPushButton("🌐 База"); btn_web.setToolTip("Спросить PCGamingWiki")
        btn_web.clicked.connect(self.web_preset)
        row2.addWidget(btn_auto)
        row2.addWidget(btn_web)
        lay.addLayout(row2)
        self.detect_label = QLabel(""); self.detect_label.setObjectName("muted")
        lay.addWidget(self.detect_label)
        self.own = QCheckBox(_("Own prefix"))
        self.own.setChecked(bool(_cfg("own_prefix", True)))
        lay.addWidget(self.own)
        self.args = QLineEdit(); self.args.setPlaceholderText(_("Arguments"))
        lay.addWidget(self.args)
        lay.addWidget(QLabel("💡 Потом жми «🚀 Починить и запустить»."))
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText(_("Add"))
        bb.button(QDialogButtonBox.Ok).setObjectName("primary")
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
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
        f, _ = QFileDialog.getOpenFileName(self, "Выбери .exe", str(pathlib.Path.home()), "Exe (*.exe)")
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
            QMessageBox.information(self, "Zapusk", "Подходящих .exe не нашлось / No game .exe found")
            return
        pick, ok = QInputDialog.getItem(self, "Найденные exe / Found", "Похоже на игру / Looks like the game:", found, 0, False)
        if ok and pick:
            self.exe.setText(pick)
            if not self.name.text():
                self.name.setText(pathlib.Path(pick).stem)
            self.auto_preset()

    def accept(self):
        if not self.exe.text() or not pathlib.Path(self.exe.text()).exists():
            QMessageBox.warning(self, "Zapusk", "Укажи существующий .exe / Choose a valid .exe")
            return
        if not self.name.text():
            self.name.setText(pathlib.Path(self.exe.text()).stem)
        try:
            g = library.add(self.name.text(), self.exe.text(), self.preset.currentData(),
                            shared_prefix=not self.own.isChecked(), args=self.args.text())
        except ValueError as e:
            QMessageBox.warning(self, "Zapusk", str(e))
            return
        self.result_game = g
        super().accept()


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
        self.exe = QLineEdit(g.get("exe", "")); lay.addWidget(self.exe)
        lay.addWidget(QLabel(_("Work dir") + ":"))
        self.workdir = QLineEdit(g.get("workdir", "")); lay.addWidget(self.workdir)
        lay.addWidget(QLabel(_("Arguments") + ":"))
        self.args = QLineEdit(g.get("args", "")); lay.addWidget(self.args)
        lay.addWidget(QLabel(_("Preset") + ":"))
        self.preset = QComboBox()
        for k, v in PRESETS.items():
            self.preset.addItem(f"{v['label']} ({k})", k)
        cur = g.get("preset", "dx11")
        self.preset.setCurrentIndex(list(PRESETS.keys()).index(cur) if cur in PRESETS else 1)
        lay.addWidget(self.preset)

        def chk(title, key, default=False):
            c = QCheckBox(title); c.setChecked(g.get(key, default))
            setattr(self, key, c); lay.addWidget(c)
            return c
        chk(_("GameMode"), "gamemode", True)
        chk(_("MangoHUD"), "mangohud")
        chk("Fsync", "fsync", True)
        chk("Esync", "esync", True)
        chk("DXVK HUD", "dxvk_hud")
        chk("Wine debug-лог", "debug")
        chk("Large Address Aware", "large_address")

        lay.addWidget(QLabel(_("Virtual desktop") + ":"))
        self.vdesk = QLineEdit(g.get("virtual_desktop", "")); lay.addWidget(self.vdesk)

        row = QHBoxLayout()
        for text, fn in (("🚀 " + _("Fix & Launch"), self.fix_run),
                         ("📁 " + _("Game folder"), self.opengame),
                         ("📂 " + _("Prefix"), self.openpfx),
                         ("🗑 " + _("Remove"), self.remove)):
            b = QPushButton(text); b.clicked.connect(fn); row.addWidget(b)
        lay.addLayout(row)

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Save).setText(_("Save"))
        bb.button(QDialogButtonBox.Save).setObjectName("primary")
        bb.accepted.connect(self.save); bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def collect(self):
        return dict(exe=self.exe.text().strip() or self.game["exe"],
                    workdir=self.workdir.text().strip() or str(pathlib.Path(self.exe.text()).parent),
                    args=self.args.text(), preset=self.preset.currentData(),
                    gamemode=self.gamemode.isChecked(), mangohud=self.mangohud.isChecked(),
                    fsync=self.fsync.isChecked(), esync=self.esync.isChecked(),
                    dxvk_hud=self.dxvk_hud.isChecked(), debug=self.debug.isChecked(),
                    large_address=self.large_address.isChecked(),
                    virtual_desktop=self.vdesk.text().strip())

    def save(self):
        library.update(self.game["name"], self.collect())
        self.accept()

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
        t = QLabel(f"🗑 {game['name']}"); t.setObjectName("big"); lay.addWidget(t)
        self.cb_files = QCheckBox(f"Удалить файлы игры / Delete game files\n{game.get('workdir','')}")
        self.cb_prefix = QCheckBox("Удалить префикс Wine / Delete Wine prefix")
        lay.addWidget(self.cb_files); lay.addWidget(self.cb_prefix)
        lay.addWidget(QLabel("Из списка игра удаляется всегда. / Always removed from the list."))
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText(_("Remove"))
        bb.button(QDialogButtonBox.Ok).setObjectName("danger")
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
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
        chip = QLabel(game.get("preset", "")); chip.setObjectName("chip")
        top.addWidget(chip); top.addStretch(1)
        lay.addLayout(top)
        t = QLabel(game["name"]); t.setObjectName("title"); t.setWordWrap(True)
        lay.addWidget(t)
        m = QLabel(pathlib.Path(game["exe"]).name); m.setObjectName("muted"); m.setWordWrap(True)
        lay.addWidget(m)
        lay.addStretch(1)
        row = QHBoxLayout()
        run = QPushButton("🚀 " + _("Fix & Launch")); run.setObjectName("good")
        run.clicked.connect(lambda: win.fix_and_launch(library.get(game["name"]) or game))
        row.addWidget(run)
        lay.addLayout(row)
        row2 = QHBoxLayout()
        quick = QPushButton("▶ " + _("Launch")); quick.clicked.connect(lambda: win.launch(game))
        cfg = QPushButton("⚙"); cfg.setFixedWidth(42); cfg.clicked.connect(lambda: win.settings(game))
        folder = QPushButton("📂"); folder.setFixedWidth(42)
        folder.setToolTip(_("Game folder"))
        folder.clicked.connect(lambda: win.opengamefolder(game))
        logs = QPushButton("📋"); logs.setFixedWidth(42); logs.clicked.connect(lambda: win.show_logs(game))
        rm = QPushButton("🗑"); rm.setFixedWidth(42)
        rm.setToolTip(_("Remove"))
        rm.setObjectName("danger")
        rm.clicked.connect(lambda: win.remove_game(game))
        row2.addWidget(quick); row2.addWidget(cfg); row2.addWidget(folder); row2.addWidget(logs); row2.addWidget(rm)
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
        self.setMouseTracking(True)   # EN: get moves WITHOUT pressed buttons
                                      # RU: движения БЕЗ зажатой кнопки
        self._parts = []
        self._t = 0.0
        self._mouse = None
        self._timer = QTimer(self)
        self._timer.setInterval(40)          # ~25 fps, только на старте / EN: only during boot
        self._timer.timeout.connect(self._tick)
        self._fade = None

    # ---------- particle setup ----------
    def _build(self):
        """EN: sample the wordmark pixels -> particle targets. RU: точки букв -> цели частиц."""
        w, h = self.width(), self.height()
        img = QImage(w, h, QImage.Format_ARGB32)
        img.fill(0)
        pt = QPainter(img)
        f = QFont("Noto Sans", 46)               # EN: smaller wordmark / RU: слово компактнее
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
        if len(targets) > 450:      # EN: cap particle count / RU: ограничиваем число частиц
            k = len(targets) // 450 + 1
            targets = targets[::k]

        self._parts = []
        n = len(targets)
        for i, (tx, ty) in enumerate(targets):
            side = i % 4            # EN: fly in from 4 sides / RU: влетают с 4 сторон
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
            hue = (i / max(n - 1, 1))          # EN: full rainbow / RU: вся радуга
            self._parts.append(dict(sx=sx, sy=sy, tx=tx, ty=ty, delay=delay,
                                    bx=0.0, by=0.0, px=sx, py=sy, hue=hue))

    # ---------- lifecycle ----------
    def _build_stars(self):
        """EN: static starfield backdrop, rendered once. RU: звёздный фон, рисуем один раз."""
        w, h = self.width(), self.height()
        pm = QPixmap(w, h)
        pm.fill(QColor(5, 6, 10))
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        for (cx, cy, col) in ((w * 0.2, h * 0.25, QColor(0, 229, 255, 14)),
                              (w * 0.85, h * 0.8, QColor(255, 47, 214, 12))):
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
        if self._t > 6.0:               # EN: boot show max ~6s / RU: показ максимум ~6 сек
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
            ease = 1 - (1 - lt) ** 3                      # easeOutCubic
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
        light_side = self._to > self._f          # EN: dark->light / RU: тёмная→светлая
        front = w * (1 - p) if light_side else w * p

        # EN: wave body — translucent liquid band behind the crest
        # RU: тело волны — полупрозрачная жидкая полоса за гребнем
        path = QPainterPath()
        pts = []
        for i in range(0, 33):
            y = h * i / 32
            fx = front + math.sin(y * 0.045 + p * 7) * 26 + math.sin(y * 0.013 + p * 3) * 14
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
        grad = QLinearGradient(front - 160 if not light_side else front, 0,
                               front if not light_side else front + 160, 0)
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
            fx = front + math.sin(y * 0.045 + p * 7) * 26 + math.sin(y * 0.013 + p * 3) * 14
            r = 2 + (i % 4)
            qp.setBrush(QColor(255, 255, 255, 70))
            qp.drawEllipse(int(fx + (14 if light_side else -14)), int(y), r * 2, r * 2)
        qp.end()


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
        logo.setStyleSheet("font-weight:800; font-size:14px; letter-spacing:3px; color:#00e5ff;")
        lay.addWidget(logo)
        lay.addStretch(1)
        # EN: language selector / RU: выбор языка
        self.combo_lang = QComboBox()
        for code, (n, fl) in i18n.LANGS.items():
            self.combo_lang.addItem(f"{fl} {n}", code)
        self.combo_lang.setCurrentIndex(max(list(i18n.LANGS.keys()).index(i18n.current()), 0))
        self.combo_lang.setFixedWidth(150)
        self.combo_lang.setToolTip(_("Language"))
        self.combo_lang.currentIndexChanged.connect(
            lambda i: win.set_language(self.combo_lang.itemData(i)))
        lay.addWidget(self.combo_lang)
        # EN: palette selector / RU: выбор палитры
        self.combo_theme = QComboBox()
        for pi, (nm, _dk, _lt) in enumerate(PALETTES):
            self.combo_theme.addItem(f"🎨 {nm}", pi)
        self.combo_theme.setCurrentIndex(win.theme._pal)
        self.combo_theme.setFixedWidth(110)
        self.combo_theme.setToolTip(_("Theme"))
        self.combo_theme.currentIndexChanged.connect(
            lambda i: win.theme.set_palette(self.combo_theme.itemData(i)))
        lay.addWidget(self.combo_theme)
        self.btn_theme = QPushButton("🌙"); self.btn_theme.setObjectName("ghost")
        self.btn_theme.setToolTip("Dark / Light")
        self.btn_theme.clicked.connect(win.toggle_theme)
        lay.addWidget(self.btn_theme)
        for sym, fn, tip in (("—", win.showMinimized, "Свернуть / Minimize"),
                             ("▢", win.toggle_max, "Развернуть / Maximize"),
                             ("✕", win.close, "Закрыть / Close")):
            b = QPushButton(sym); b.setObjectName("ghost"); b.setToolTip(tip); b.setFixedSize(38, 32)
            b.clicked.connect(fn)
            lay.addWidget(b)
        self._drag = None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.win.frameGeometry().topLeft()

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

        self.theme = Theme()   # EN: theme must exist before TitleBar / RU: тема нужна до TitleBar
        # EN: neon carbon frame (paints its own background+border)
        # RU: неоновая карбоновая рамка (рисует фон и подсветку сама)
        self.glass = NeonFrame()
        root = QVBoxLayout(self.glass)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.titlebar = TitleBar(self)
        root.addWidget(self.titlebar)

        body = QHBoxLayout(); body.setContentsMargins(14, 2, 14, 14)
        root.addLayout(body, 1)

        navw = QFrame(); navw.setObjectName("nav"); navw.setFixedWidth(210)
        nl = QVBoxLayout(navw)
        self.nav = QListWidget()
        self.nav.addItems(["🎮  " + _("Library"), "🔄  " + _("Updates"), "🚀  " + _("Optimization"), "⚙️  " + _("Setup"), "🔧  " + _("Settings"), "📋  " + _("Logs")])
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
        self.wave = WaveOverlay(self.glass, None)   # theme проставим в run_gui
        self.stack.setGraphicsEffect(None)
        self.nav.setCurrentRow(0)
        self.refresh()
        self.refresh_updates()
        self.refresh_optimize()

    def showEvent(self, e):
        super().showEvent(e)
        self.stack.show()   # EN: no splash — content immediately / RU: без заставки

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
            QMessageBox.information(self, "Zapusk",
                "Язык сохранён. Перезапусти приложение.\nLanguage saved. Restart the app.")

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
        self._anim.setStartValue(1.0); self._anim.setEndValue(0.0)
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
        self._anim2.setStartValue(0.0); self._anim2.setEndValue(1.0)
        self._anim2.finished.connect(lambda: self.stack.setGraphicsEffect(None))
        self._anim2.start()

    # ================= БИБЛИОТЕКА / LIBRARY =================
    def _build_library(self):
        p = QWidget(); lay = QVBoxLayout(p)
        top = QHBoxLayout()
        title = QLabel(_("My games")); title.setObjectName("big")
        add = QPushButton("＋ " + _("Add game")); add.setObjectName("primary")
        add.clicked.connect(lambda: self.add_game(""))
        ref = QPushButton(_("Refresh")); ref.clicked.connect(self.refresh)
        top.addWidget(title); top.addStretch(1); top.addWidget(ref); top.addWidget(add)
        lay.addLayout(top)
        hint = QLabel(_("Drop hint"))
        hint.setObjectName("muted")
        lay.addWidget(hint)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        self.grid_host = QWidget(); self.grid = QGridLayout(self.grid_host)
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
        if not gs:
            hint = QLabel(_("Empty"))
            hint.setObjectName("muted")
            self.grid.addWidget(hint, 0, 0)
        for i, g in enumerate(gs):
            self.grid.addWidget(Card(g, self), i // 3, i % 3)
        self.refresh_log_combo()

    def add_game(self, initial_exe=""):
        d = AddGameDialog(self, initial_exe)
        if d.exec():
            self.refresh()
            if d.result_game and bool(_cfg("auto_fix", True)):
                self.fix_and_launch(d.result_game, launch=False)   # EN: auto-config, no start

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
            if QMessageBox.question(self, "Zapusk",
                    f"Точно удалить ФАЙЛЫ игры?\n{d}\n\nThis will delete the game folder!") != QMessageBox.Yes:
                return
            shutil.rmtree(d, ignore_errors=True)
        if dlg.cb_prefix.isChecked():
            if not g.get("shared_prefix"):
                shutil.rmtree(PREFIXES_DIR / g["slug"], ignore_errors=True)
            else:
                QMessageBox.information(self, "Zapusk",
                    "Префикс общий — оставил его. / Shared prefix kept.")
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
                    QMessageBox.information(self, "Zapusk", f"Нет подходящего .exe / No game .exe:\n{p}")

    # ================= ОБНОВЛЕНИЯ / UPDATES =================
    def _build_updates(self):
        p = QWidget(); lay = QVBoxLayout(p)
        t = QLabel(_("Updates")); t.setObjectName("big"); lay.addWidget(t)
        d = QLabel("Раннеры и трансляторы — Zapusk качает сам и следит за версиями.\nRunners & translation layers — auto-download with version tracking.")
        d.setObjectName("muted"); lay.addWidget(d)

        ge = QFrame(); ge.setObjectName("panel"); gl = QVBoxLayout(ge)
        gl.addWidget(QLabel("🎮 " + _("GEProton")))
        self.ge_status = QLabel("…"); self.ge_status.setObjectName("muted"); self.ge_status.setWordWrap(True)
        gl.addWidget(self.ge_status)
        self.ge_progress = QProgressBar(); self.ge_progress.hide()
        gl.addWidget(self.ge_progress)
        row = QHBoxLayout()
        self.btn_ge = QPushButton("⬇ " + _("Download latest")); self.btn_ge.setObjectName("primary")
        self.btn_ge.clicked.connect(self.update_ge)
        row.addWidget(self.btn_ge); row.addStretch(1)
        gl.addLayout(row)
        lay.addWidget(ge)

        dx = QFrame(); dx.setObjectName("panel"); dl2 = QVBoxLayout(dx)
        dl2.addWidget(QLabel("🧊 " + _("DXVK card")))
        self.dx_status = QLabel("…"); self.dx_status.setObjectName("muted"); self.dx_status.setWordWrap(True)
        dl2.addWidget(self.dx_status)
        row2 = QHBoxLayout()
        btn_check = QPushButton("🔎 " + _("Check"))
        btn_check.clicked.connect(self.refresh_updates)
        btn_up = QPushButton("⬆ " + _("Update pm")); btn_up.setObjectName("primary")
        btn_up.clicked.connect(self.update_pacman)
        row2.addWidget(btn_check); row2.addWidget(btn_up); row2.addStretch(1)
        dl2.addLayout(row2)
        lay.addWidget(dx)

        lay.addStretch(1)
        self.stack.addWidget(p)

    def _restyle(self, lbl, objname):
        """EN: force Qt to re-apply the #ok/#warn/#err color. RU: принудительно перекрасить."""
        lbl.setObjectName(objname)
        lbl.style().unpolish(lbl); lbl.style().polish(lbl)

    def refresh_updates(self):
        from zapusk.core import runners
        inst = runners.installed_ge()
        try:
            tag, _, _ = runners.latest_ge_proton()
            if inst:
                self.ge_status.setText(f"Установлен / Installed: {inst}   •   Последний / Latest: {tag}")
                self._restyle(self.ge_status, "ok" if inst == tag else "warn")
            else:
                self.ge_status.setText(f"Не установлен / Not installed   •   Последний / Latest: {tag}")
                self._restyle(self.ge_status, "err")
        except Exception as e:
            self.ge_status.setText(f"⚠ Нет связи с GitHub / Cannot reach GitHub: {e}\n"
                                   "Проверь интернет / Check your connection.")
            self._restyle(self.ge_status, "warn")
        try:
            dv = runners.pacman_ver("dxvk"); vp = runners.pacman_ver("vkd3d-proton")
            ld = runners.latest_dxvk(); lv = runners.latest_vkd3d()
            def stat(cur, latest, name):
                if not cur:
                    return f"{name}: ❌ не установлен / not installed"
                return f"{name}: {cur} (latest: {latest})"
            self.dx_status.setText(stat(dv, ld, "DXVK") + "\n" + stat(vp, lv, "VKD3D-Proton"))
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
                runners.install_ge(tmp, lambda i, n: self._ge_signal(int(i * 100 / max(n, 1))))
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
        self.dx_status.setText("Обновление: pacman -Sy dxvk vkd3d-proton… (введи пароль)")
        cmd = host_prefix() + ["pkexec", "sh", "-c",
               "pacman -Sy --needed --noconfirm dxvk; "
               "pacman -S --needed --noconfirm vkd3d-proton || "
               "pacman -S --needed --noconfirm vkd3d || true"]
        p = subprocess.Popen(cmd)
        p.wait()
        self.refresh_updates()
        from zapusk.core import runners
        if not runners.pacman_ver("vkd3d-proton") and not runners.pacman_ver("vkd3d"):
            self.dx_status.setText(self.dx_status.text() +
                "\n⚠ vkd3d-proton нет в твоих репозиториях — вручную: yay -S vkd3d-proton")

    # ================= ОПТИМИЗАЦИЯ / OPTIMIZE =================
    def _build_optimize(self):
        p = QWidget(); lay = QVBoxLayout(p)
        t = QLabel(_("Optimization title")); t.setObjectName("big"); lay.addWidget(t)

        def panel(title, status_attr):
            f = QFrame(); f.setObjectName("panel"); l = QVBoxLayout(f)
            l.addWidget(QLabel(title))
            lbl = QLabel("…"); lbl.setWordWrap(True)
            setattr(self, status_attr, lbl)
            l.addWidget(lbl)
            return f, l

        gov, gl = panel("🔥 " + _("Governor"), "gov_status")
        b = QPushButton("⚡ " + _("Enable Perf")); b.setObjectName("primary"); b.clicked.connect(self.opt_governor)
        gl.addWidget(b); lay.addWidget(gov)

        sw, sl = panel("💾 " + _("Swappiness"), "sw_status")
        b2 = QPushButton("⚡ " + _("Set 10")); b2.setObjectName("primary"); b2.clicked.connect(self.opt_swappiness)
        sl.addWidget(b2); lay.addWidget(sw)

        gm, ml = panel("🎯 " + _("GameMode daemon"), "gm_status")
        b3 = QPushButton("⚡ " + _("Enable")); b3.setObjectName("primary"); b3.clicked.connect(self.opt_gamemode)
        ml.addWidget(b3); lay.addWidget(gm)

        sc, cl = panel("🧹 " + _("Shader cache"), "sc_status")
        b4 = QPushButton("🗑 " + _("Clear")); b4.clicked.connect(self.opt_clear_cache)
        cl.addWidget(b4); lay.addWidget(sc)

        lay.addStretch(1)
        self.stack.addWidget(p)

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
        self.gm_status.setText("Активен / Active ✅" if gm else "Не активен / Inactive ❌")
        self._restyle(self.gm_status, "ok" if gm else "err")
        gpu = optimize.vulkan_driver()
        if gpu:
            self.sc_status.setText(f"GPU: {gpu}")
            self._restyle(self.sc_status, "muted")

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
        p = QWidget(); sl = QVBoxLayout(p)
        t = QLabel(_("Setup")); t.setObjectName("big"); sl.addWidget(t)
        sd = QLabel("Один раз: системный стек (Wine, DXVK, драйверы Vulkan). / One-time system setup.")
        sd.setObjectName("muted"); sl.addWidget(sd)
        row = QHBoxLayout()
        self.btn_install = QPushButton("🔧 " + _("Install all"))
        self.btn_install.setObjectName("good")
        self.btn_install.clicked.connect(self.auto_install)
        btn_check = QPushButton("🔎 " + _("Check system"))
        btn_check.clicked.connect(lambda: self.run_doctor(silent=False))
        row.addWidget(self.btn_install); row.addWidget(btn_check); row.addStretch(1)
        sl.addLayout(row)
        self.progress = QProgressBar(); self.progress.setRange(0, 0); self.progress.hide()
        sl.addWidget(self.progress)
        self.setup_out = QTextEdit(); self.setup_out.setReadOnly(True)
        sl.addWidget(self.setup_out, 1)
        self.stack.addWidget(p)

    def auto_install(self):
        if not INSTALL_SCRIPT.exists():
            QMessageBox.warning(self, "Zapusk", f"Не найден / Not found:\n{INSTALL_SCRIPT}")
            return
        self.setup_out.setPlainText("Устанавливаю системный стек / Installing…\nВведи пароль / Enter password when asked.\n")
        self.progress.show(); self.btn_install.setEnabled(False)
        self._inst = AutoInstallThread()
        self._inst.line.connect(lambda s: self.setup_out.append(s))
        self._inst.done.connect(self._after_install)
        self._inst.start()

    def _after_install(self, code):
        self.progress.hide(); self.btn_install.setEnabled(True)
        self.setup_out.append(f"\n{'✅' if code == 0 else '⚠'} Готово / Done (code {code}). Перезагрузись / Reboot, затем «Проверить систему».")
        self.run_doctor(silent=True)

    def run_doctor(self, silent=False):
        from zapusk.core.system import doctor
        if not silent:
            self.setup_out.setPlainText("Проверяю / Checking…")
        QApplication.processEvents()
        self.setup_out.setPlainText(doctor())

    # ================= ЛОГИ / LOGS =================
    def _build_logs(self):
        p = QWidget(); lg = QVBoxLayout(p)
        lg.addWidget(QLabel(_("Logs")))
        self.log_combo = QComboBox(); self.log_combo.currentTextChanged.connect(self.load_log)
        lg.addWidget(self.log_combo)
        self.log_out = QTextEdit(); self.log_out.setReadOnly(True)
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
            txt = lp.read_text(encoding='utf-8', errors='replace')
            self.log_out.setPlainText("\n".join(txt.splitlines()[-400:]))
        else:
            self.log_out.setPlainText(_("No log"))

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
        p = QWidget(); lay = QVBoxLayout(p)
        t = QLabel(_("Settings")); t.setObjectName("big"); lay.addWidget(t)

        # --- language ---
        lang = QFrame(); lang.setObjectName("panel"); ll = QVBoxLayout(lang)
        ll.addWidget(QLabel("🌐 " + _("Language")))
        self.set_lang_combo = QComboBox()
        for code, (n, fl) in i18n.LANGS.items():
            self.set_lang_combo.addItem(f"{fl} {n}", code)
        self.set_lang_combo.setCurrentIndex(max(list(i18n.LANGS.keys()).index(i18n.current()), 0))
        self.set_lang_combo.currentIndexChanged.connect(
            lambda i: self.set_language(self.set_lang_combo.itemData(i)))
        ll.addWidget(self.set_lang_combo)
        lay.addWidget(lang)

        # --- theme ---
        th = QFrame(); th.setObjectName("panel"); tl = QVBoxLayout(th)
        tl.addWidget(QLabel("🎨 " + _("Theme")))
        self.set_theme_combo = QComboBox()
        for pi, (nm, _dk, _lt) in enumerate(PALETTES):
            self.set_theme_combo.addItem(f"🎨 {nm}", pi)
        self.set_theme_combo.setCurrentIndex(self.theme._pal)
        self.set_theme_combo.currentIndexChanged.connect(
            lambda i: self.theme.set_palette(self.set_theme_combo.itemData(i)))
        tl.addWidget(self.set_theme_combo)
        row = QHBoxLayout()
        dl = QPushButton("🌙 / ☀️"); dl.clicked.connect(self.toggle_theme)
        row.addWidget(dl); row.addStretch(1)
        tl.addLayout(row)
        lay.addWidget(th)

        # --- behaviour ---
        beh = QFrame(); beh.setObjectName("panel"); bl = QVBoxLayout(beh)
        bl.addWidget(QLabel("⚙️"))
        self.cb_autofix = QCheckBox("Авто-установка зависимостей при добавлении игры / Auto-fix on add")
        self.cb_autofix.setChecked(bool(_cfg("auto_fix", True)))
        self.cb_autofix.toggled.connect(lambda v: i18n.save("auto_fix", bool(v)))
        bl.addWidget(self.cb_autofix)
        self.cb_ownprefix = QCheckBox("По умолчанию отдельный префикс / Own prefix by default")
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
        QMessageBox.information(self, "Zapusk",
            f"{_('Launched')}: {g['name']}\n{_('Log')}: {lp}\n\n{_('Not starting')}")

    def fix_and_launch(self, game):
        if not game:
            return
        g = library.get(game["name"]) or game
        preset = PRESETS.get(g.get("preset", "dx11"), PRESETS["dx11"])
        prefix = prefix_path(g["slug"], g.get("shared_prefix", False))
        lp = LOGS_DIR / f"{g['slug']}.log"
        self.nav.setCurrentRow(3)
        self.setup_out.setPlainText(f"Чиним / Fixing '{g['name']}'… лог / log: {lp}\n")
        self.progress.show(); self.btn_install.setEnabled(False)
        from zapusk.core.deps import fix_game

        def job():
            fix_game(prefix, preset, log=str(lp), progress=lambda m: self._fix_line.sig.emit(m))

        self._fix_line = _Signal()
        self._fix_line.sig.connect(lambda m: self.setup_out.append(f"  → {m}"))
        self._worker = Worker(job)
        self._launch_after = launch
        self._worker.done.connect(lambda: self._after_fix(g, lp))
        self._worker.start()

    def _after_fix(self, g, lp):
        self.progress.hide(); self.btn_install.setEnabled(True)
        preset = PRESETS.get(g.get("preset", "dx11"), {})
        if preset.get("note"):
            self.setup_out.append(f"\n💡 {preset['note']}")
        if getattr(self, "_launch_after", True):
            self.setup_out.append(f"\n✅ Запускаю / Launching {g['name']}…")
            self.launch(g)
        else:
            self.setup_out.append(f"\n✅ Готово! Жми ▶ {g['name']}")


def run_gui():
    """EN: app entry — animated theme + neon window. RU: вход — тема и неоновое окно."""
    ensure_dirs()
    app = QApplication(sys.argv)
    app.setFont(QFont("Noto Sans", 10))
    win = MainWindow()
    theme = win.theme
    win.wave.theme = theme
    win.glass.theme = theme
    def _apply_theme():
        app.setStyleSheet(theme.qss())
        win.glass.invalidate()      # EN: frame bg follows theme / RU: фон едет за темой
    theme.changed.connect(_apply_theme)
    app.setStyleSheet(theme.qss())
    app.installEventFilter(ParallaxFilter(win))
    win.show()
    return app.exec()
