# SPDX-License-Identifier: GPL-3.0-or-later
import os, re, subprocess, pathlib

DATA_DIR = pathlib.Path.home() / ".local/share/zapusk"
PREFIXES_DIR = DATA_DIR / "prefixes"
LOGS_DIR = DATA_DIR / "logs"
DEFAULT_PREFIX = PREFIXES_DIR / "default"
LIBRARY_FILE = DATA_DIR / "library.json"

def ensure_dirs():
    for d in (DATA_DIR, PREFIXES_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

def slugify(name: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9а-яА-Я_-]+', '-', name).strip('-')
    return s[:60] or "game"

def which(cmd: str):
    from shutil import which as _w
    return _w(cmd)

def run(cmd, env=None, cwd=None, log=None):
    """Запустить команду, дублируя вывод в log-файл (если задан)."""
    lp = open(log, 'a', encoding='utf-8', errors='replace') if log else open(os.devnull, 'w')
    lp.write(f"\n$ {' '.join(str(c) for c in cmd)}\n"); lp.flush()
    p = subprocess.Popen(cmd, env=env, cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, errors='replace', bufsize=1)
    out_lines = []
    for line in p.stdout:
        out_lines.append(line)
        lp.write(line); lp.flush()
    p.wait()
    if log: lp.close()
    return p.returncode, ''.join(out_lines)

def run_detached(cmd, env=None, cwd=None, log=None):
    out = open(log, 'a', encoding='utf-8', errors='replace') if log else open(os.devnull, 'w')
    out.write(f"\n$ {' '.join(str(c) for c in cmd)}\n"); out.flush()
    p = subprocess.Popen(cmd, env=env, cwd=cwd, stdout=out, stderr=subprocess.STDOUT,
                         start_new_session=True, text=True)
    return p
