# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\Users\\marku\\Documents\\phoenix-desktop/gui', 'gui'), ('C:\\Users\\marku\\Documents\\phoenix-desktop\\venv\\Lib\\site-packages/customtkinter', 'customtkinter'), ('C:\\Users\\marku\\Documents\\phoenix-desktop\\venv\\Lib\\site-packages/plyer', 'plyer'), ('C:\\Users\\marku\\Documents\\phoenix-desktop\\venv\\Lib\\site-packages/pystray', 'pystray')]
binaries = []
hiddenimports = ['PIL._tkinter_finder', 'win32timezone', 'pystray._win32', 'plyer.platforms.win.notification', 'customtkinter', 'darkdetect']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('plyer')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pystray')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['tray_app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PhoenixTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\marku\\Documents\\phoenix-desktop\\phoenix_icon.ico'],
)
