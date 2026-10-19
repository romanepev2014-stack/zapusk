# EN: build a standalone binary: pyinstaller zapusk.spec
# RU: сборка единого бинарника: pyinstaller zapusk.spec
a = Analysis(
    ['zapusk/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[('install_arch.sh', '.'), ('requirements.txt', '.')],
    hiddenimports=['zapusk.gui', 'zapusk.cli'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas,
    name='zapusk',
    console=False,
    upx=True,
)
