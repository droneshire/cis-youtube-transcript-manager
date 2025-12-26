# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the project root directory
# The makefile runs from project root, so use current working directory
project_root = Path(os.getcwd()).absolute()
src_path = project_root / "src"

# Add src to path for imports
sys.path.insert(0, str(src_path))

block_cipher = None

a = Analysis(
    [str(src_path / "executables" / "launcher.py")],
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        (str(src_path / "executables" / "youtube_app.py"), "executables"),
        (str(src_path / "constants.py"), "."),
        (str(src_path / "youtube_helper.py"), "."),
    ],
    hiddenimports=[
        "streamlit",
        "streamlit.web.cli",
        "streamlit.runtime.scriptrunner.script_runner",
        "streamlit.runtime.state",
        "pandas",
        "youtube_transcript_api",
        "googleapiclient",
        "googleapiclient.discovery",
        "dotenv",
        "constants",
        "youtube_helper",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="youtube-transcript-manager",
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
