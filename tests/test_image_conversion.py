from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from converters.image_converter import ImageConverter
from services.conversion_service import ConversionService


def test_png_to_jpeg_conversion(tmp_path: Path) -> None:
    source = tmp_path / "sample.png"
    Image.new("RGBA", (10, 10), (255, 0, 0, 255)).save(source)
    target = tmp_path / "sample_converted.jpeg"

    ImageConverter.convert(source, target, "JPEG", quality=85)

    assert target.exists()
    with Image.open(target) as image:
        assert image.format == "JPEG"
        assert image.size == (10, 10)


def test_webp_to_png_conversion(tmp_path: Path) -> None:
    source = tmp_path / "sample.webp"
    Image.new("RGBA", (12, 8), (0, 255, 0, 180)).save(source)
    target = tmp_path / "sample_converted.png"

    ImageConverter.convert(source, target, "PNG")

    assert target.exists()
    with Image.open(target) as image:
        assert image.format == "PNG"
        assert image.size == (12, 8)


def test_unsupported_format_rejected(tmp_path: Path) -> None:
    source = tmp_path / "sample.png"
    Image.new("RGBA", (10, 10), (255, 0, 0, 255)).save(source)

    try:
        ImageConverter.convert(source, tmp_path / "out.txt", "TXT")
        assert False, "Expected ValueError for unsupported output format"
    except ValueError:
        pass


@pytest.mark.parametrize(
    ("output_format", "expected_format"),
    [("BMP", "BMP"), ("TIFF", "TIFF"), ("GIF", "GIF"), ("ICO", "ICO")],
)
def test_additional_image_formats_convert(tmp_path: Path, output_format: str, expected_format: str) -> None:
    source = tmp_path / "sample.png"
    Image.new("RGBA", (64, 64), (255, 0, 0, 100)).save(source)

    output = Path(ConversionService.convert_file(source, output_format))

    with Image.open(output) as converted:
        assert converted.format == expected_format


def test_output_conflict_uses_another_filename_without_overwriting(tmp_path: Path) -> None:
    source = tmp_path / "sample.png"
    Image.new("RGB", (10, 10), (25, 50, 75)).save(source)
    protected_output = tmp_path / "sample_converted.jpeg"
    protected_output.write_bytes(b"keep")

    converted = Path(ConversionService.convert_file(source, "JPEG"))

    assert converted.name == "sample_converted_1.jpeg"
    assert protected_output.read_bytes() == b"keep"


def test_file_type_registry_lists_supported_formats(tmp_path: Path, monkeypatch) -> None:
    from services.dependency_check import DependencyChecker

    monkeypatch.setattr(DependencyChecker, "dependency_available", staticmethod(lambda _dependency: True))

    assert ConversionService.get_supported_formats(tmp_path / "report.docx") == ["PDF"]
    assert ConversionService.get_supported_formats(tmp_path / "document.pdf") == [
        "PNG",
        "JPEG",
        "DOCX",
        "PDF_SPLIT",
        "PDF_EXTRACT",
        "PDF_ROTATE",
        "PDF_COMPRESS",
    ]
    formats = ConversionService.get_supported_formats(tmp_path / "photo.png")
    assert {"JPEG", "WEBP", "BMP", "TIFF"} <= set(formats)
    assert "PNG" not in formats


def test_missing_input_is_reported(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Input file does not exist"):
        ConversionService.convert_file(tmp_path / "missing.png", "JPEG")
