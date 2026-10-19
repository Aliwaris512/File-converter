from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from converters.audio_video_converter import AudioVideoConverter
from converters.image_converter import ImageConverter
from converters.office_converter import OfficeConverter
from converters.pdf_converter import PDFConverter


@dataclass(frozen=True)
class ConversionOption:
    label: str
    value: str
    requires_background_color: bool = False
    required_dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class RegistryEntry:
    kind: str
    extensions: tuple[str, ...]
    converter_name: str
    options: tuple[ConversionOption, ...]
    conversion_function: Callable | None


def get_registry() -> list[RegistryEntry]:
    image_formats = (
        ConversionOption("PNG", "PNG", required_dependencies=("Pillow",)),
        ConversionOption("JPEG", "JPEG", requires_background_color=True, required_dependencies=("Pillow",)),
        ConversionOption("WebP", "WEBP", required_dependencies=("Pillow",)),
        ConversionOption("BMP", "BMP", required_dependencies=("Pillow",)),
        ConversionOption("TIFF", "TIFF", required_dependencies=("Pillow",)),
        ConversionOption("GIF", "GIF", required_dependencies=("Pillow",)),
        ConversionOption("ICO", "ICO", required_dependencies=("Pillow",)),
    )
    return [
        RegistryEntry(
            kind="image",
            extensions=(".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".ico"),
            converter_name="ImageConverter",
            options=image_formats,
            conversion_function=ImageConverter.convert,
        ),
        RegistryEntry(
            kind="document",
            extensions=(".txt",),
            converter_name="PDFConverter",
            options=(ConversionOption("PDF", "PDF", required_dependencies=("ReportLab",)),),
            conversion_function=PDFConverter.text_to_pdf,
        ),
        RegistryEntry(
            kind="office",
            extensions=(".docx", ".doc", ".pptx", ".html", ".htm"),
            converter_name="LibreOfficeConverter",
            options=(
                ConversionOption("PDF", "PDF", required_dependencies=("libreoffice",)),
            ),
            conversion_function=OfficeConverter.convert_to_pdf,
        ),
        RegistryEntry(
            kind="spreadsheet",
            extensions=(".xlsx",),
            converter_name="SpreadsheetConverter",
            options=(ConversionOption("CSV", "CSV", required_dependencies=("openpyxl",)),),
            conversion_function=OfficeConverter.xlsx_to_csv,
        ),
        RegistryEntry(
            kind="spreadsheet",
            extensions=(".csv",),
            converter_name="SpreadsheetConverter",
            options=(ConversionOption("XLSX", "XLSX", required_dependencies=("openpyxl",)),),
            conversion_function=OfficeConverter.csv_to_xlsx,
        ),
        RegistryEntry(
            kind="pdf",
            extensions=(".pdf",),
            converter_name="PDFConverter",
            options=(
                ConversionOption("PNG images (one per page)", "PNG", required_dependencies=("PyMuPDF",)),
                ConversionOption("JPEG images (one per page)", "JPEG", required_dependencies=("PyMuPDF",)),
                ConversionOption("Word document (.docx)", "DOCX", required_dependencies=("PyMuPDF", "pdf2docx")),
                ConversionOption("Split into page PDFs", "PDF_SPLIT", required_dependencies=("PyMuPDF",)),
                ConversionOption("Extract pages to PDF", "PDF_EXTRACT", required_dependencies=("PyMuPDF",)),
                ConversionOption("Rotate pages 90°", "PDF_ROTATE", required_dependencies=("PyMuPDF",)),
                ConversionOption("Compress PDF", "PDF_COMPRESS", required_dependencies=("PyMuPDF",)),
            ),
            conversion_function=PDFConverter.pdf_to_images,
        ),
        RegistryEntry(
            kind="audio-video",
            extensions=(".mp3", ".wav", ".m4a", ".flac", ".mp4", ".mov", ".avi", ".mkv", ".webm"),
            converter_name="AudioVideoConverter",
            options=(
                ConversionOption("MP3", "MP3", required_dependencies=("ffmpeg",)),
                ConversionOption("WAV", "WAV", required_dependencies=("ffmpeg",)),
                ConversionOption("MP4", "MP4", required_dependencies=("ffmpeg",)),
                ConversionOption("WEBM", "WEBM", required_dependencies=("ffmpeg",)),
                ConversionOption("AVI", "AVI", required_dependencies=("ffmpeg",)),
            ),
            conversion_function=AudioVideoConverter.convert,
        ),
    ]
