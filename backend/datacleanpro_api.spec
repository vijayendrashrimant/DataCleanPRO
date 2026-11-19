# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for DataCleanPro API
# Produces:  backend/dist/datacleanpro_api  (Linux/macOS)
#            backend/dist/datacleanpro_api.exe  (Windows)
#
# Build:  python build_exe.py
#         (or directly: pyinstaller datacleanpro_api.spec)

import sys
from pathlib import Path

block_cipher = None

# ── Hidden imports ─────────────────────────────────────────────────────────────
# uvicorn, fastapi and their dependencies use dynamic imports that PyInstaller
# cannot detect via static analysis.  List them explicitly.
hidden_imports = [
    # uvicorn internals
    "uvicorn",
    "uvicorn.main",
    "uvicorn.config",
    "uvicorn.server",
    "uvicorn.lifespan",
    "uvicorn.lifespan.off",
    "uvicorn.lifespan.on",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.protocols.websockets.wsproto_impl",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.logging",
    "uvicorn.middleware",
    "uvicorn.middleware.proxy_headers",
    "uvicorn.middleware.message_logger",
    # fastapi / starlette
    "fastapi",
    "starlette",
    "starlette.routing",
    "starlette.middleware",
    "starlette.middleware.cors",
    "starlette.responses",
    "starlette.background",
    "starlette.staticfiles",
    "starlette.testclient",
    # pydantic
    "pydantic",
    "pydantic.v1",
    "pydantic_core",
    # http
    "h11",
    "httptools",
    "anyio",
    "anyio.abc",
    "anyio._backends._asyncio",
    "sniffio",
    # data
    "pandas",
    "pandas._libs",
    "pandas._libs.tslibs",
    "pandas._libs.tslibs.base",
    "pandas._libs.tslibs.np_datetime",
    "pandas._libs.tslibs.nattype",
    "pandas._libs.tslibs.offsets",
    "pandas._libs.tslibs.timestamps",
    "pandas._libs.tslibs.timedeltas",
    "pandas._libs.tslibs.timezones",
    "pandas._libs.tslibs.parsing",
    "pandas._libs.tslibs.conversion",
    "pandas._libs.tslibs.period",
    "pandas._libs.tslibs.strptime",
    "pandas._libs.tslibs.dtypes",
    "numpy",
    "openpyxl",
    "openpyxl.styles",
    "openpyxl.reader.excel",
    "openpyxl.writer.excel",
    "xlrd",
    "chardet",
    "multipart",
    "python_multipart",
    # stdlib async
    "asyncio",
    "email",
    "email.mime",
    "email.mime.multipart",
]

a = Analysis(
    ["main.py"],
    pathex=[str(Path(".").resolve())],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude things we don't need to keep the exe smaller
        "tkinter",
        "matplotlib",
        "scipy",
        "sklearn",
        "PIL",
        "cv2",
        "torch",
        "tensorflow",
        "IPython",
        "jupyter",
        "notebook",
        "pytest",
        "sphinx",
    ],
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
    name="datacleanpro_api",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # compress with UPX if available (reduces size ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # no console window on Windows
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows: embed a version resource and icon
    version=None,
    icon=None,
)
