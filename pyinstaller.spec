# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files


datas = collect_data_files(
    "pymupdf",
    includes=["layout/resources/onnx/*.yaml", "layout/resources/onnx/*.onnx"],
)

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "services",
        "services.conversion_service",
        "services.registry",
        "ui",
        "ui.popup",
        "converters",
        "converters.image_converter",
        "converters.office_converter",
        "converters.pdf_converter",
        "PIL",
        "fitz",
        "reportlab",
        "docx",
        "pdf2docx",
        "openpyxl",
        "converters.audio_video_converter",
        "windows",
        "windows.context_menu",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LocalFileConverter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LocalFileConverter",
)
