from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

from converters.office_converter import OfficeConverter


class DependencyChecker:
    """Detect whether the local engine needed for a conversion is available."""

    @staticmethod
    def check_dependencies_for(file_path: str | Path, output_format: str | None = None) -> list[str]:
        suffix = Path(file_path).suffix.lower()
        target = output_format.upper() if output_format else None
        missing: list[str] = []

        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".ico"}:
            missing.extend(DependencyChecker._missing_modules(("PIL",), "Pillow"))
        elif suffix == ".txt":
            missing.extend(DependencyChecker._missing_modules(("reportlab",), "ReportLab"))
        elif suffix in {".doc", ".docx", ".pptx", ".html", ".htm"}:
            if target == "PDF" and not OfficeConverter.libreoffice_path():
                missing.append("LibreOffice")
        elif suffix in {".xlsx", ".csv"}:
            missing.extend(DependencyChecker._missing_modules(("openpyxl",), "openpyxl"))
        elif suffix == ".pdf":
            if not any(importlib.util.find_spec(module) is not None for module in ("pymupdf", "fitz")):
                missing.append("PyMuPDF")
            if target == "DOCX":
                missing.extend(DependencyChecker._missing_modules(("pdf2docx",), "pdf2docx"))
        elif suffix in {".mp3", ".wav", ".m4a", ".flac", ".mp4", ".mov", ".avi", ".mkv", ".webm"}:
            if not shutil.which("ffmpeg"):
                missing.append("FFmpeg")

        return list(dict.fromkeys(missing))

    @staticmethod
    def _missing_modules(modules: tuple[str, ...], label: str) -> list[str]:
        if all(importlib.util.find_spec(module) is not None for module in modules):
            return []
        return [label]

    @staticmethod
    def dependency_available(dependency: str) -> bool:
        if dependency == "libreoffice":
            return OfficeConverter.libreoffice_path() is not None
        if dependency == "ffmpeg":
            return shutil.which("ffmpeg") is not None
        if dependency == "PyMuPDF":
            return any(importlib.util.find_spec(module) is not None for module in ("pymupdf", "fitz"))
        module_names = {
            "Pillow": ("PIL",),
            "ReportLab": ("reportlab",),
            "PyMuPDF": ("pymupdf", "fitz"),
            "pdf2docx": ("pdf2docx",),
            "openpyxl": ("openpyxl",),
        }
        modules = module_names.get(dependency, (dependency,))
        if dependency == "PyMuPDF":
            return any(importlib.util.find_spec(module) is not None for module in modules)
        return all(importlib.util.find_spec(module) is not None for module in modules)

    @staticmethod
    def explain_missing(file_path: str | Path, output_format: str | None = None) -> str:
        missing = DependencyChecker.check_dependencies_for(file_path, output_format)
        if not missing:
            return ""
        instructions = {
            "FFmpeg": "FFmpeg is required for this conversion. Install FFmpeg locally and ensure it is on PATH.",
            "PyMuPDF": "PyMuPDF is required for PDF operations. Install project dependencies and retry.",
            "pdf2docx": "The pdf2docx package is required for PDF-to-Word conversion. Install project dependencies and retry.",
            "openpyxl": "openpyxl is required for spreadsheet conversions. Install project dependencies and retry.",
            "LibreOffice": "LibreOffice is required for this document conversion. Install it locally; the app does not download it.",
            "ReportLab": "ReportLab is required for text-to-PDF conversion. Install project dependencies and retry.",
            "Pillow": "Pillow is required for image conversion. Install project dependencies and retry.",
        }
        return " ".join(instructions[item] for item in missing)
