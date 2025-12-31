# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Tempo

a = Analysis(
    ['tempo/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'click',
        'rich',
        'rich.console',
        'rich.panel',
        'rich.progress',
        'rich.table',
        'rich.text',
        'rich.live',
        'rich.spinner',
        'yaml',
        'dateutil',
        'dateutil.parser',
        'dateutil.tz',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='tempo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

