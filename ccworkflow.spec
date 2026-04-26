# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()
app_name = "ccworkflow"

web_templates = project_root / "src" / "ccworkflow" / "web" / "templates"
web_static = project_root / "src" / "ccworkflow" / "web" / "static"

added_files = []
if web_templates.exists():
    added_files.append((str(web_templates), "ccworkflow/web/templates"))
if web_static.exists():
    added_files.append((str(web_static), "ccworkflow/web/static"))


a = Analysis(
    ['main.py'],
    pathex=[str(project_root), str(project_root / 'src')],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
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
    name=app_name,
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
