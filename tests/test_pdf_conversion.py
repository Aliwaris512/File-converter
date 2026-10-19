from __future__ import annotations

from pathlib import Path

from reportlab.pdfgen import canvas

from converters.pdf_converter import PDFConverter
from services.conversion_service import ConversionService


def test_text_to_pdf_creates_output_file(tmp_path: Path) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("hello world", encoding="utf-8")
    target = tmp_path / "notes.pdf"

    PDFConverter.text_to_pdf(source, target)

    assert target.exists()
    assert target.suffix.lower() == ".pdf"


def test_pdf_to_images_exports_pages(tmp_path: Path) -> None:
    source = tmp_path / "sample.pdf"
    pdf_canvas = canvas.Canvas(str(source))
    pdf_canvas.drawString(50, 750, "Page 1")
    pdf_canvas.showPage()
    pdf_canvas.drawString(50, 750, "Page 2")
    pdf_canvas.save()

    output_dir = tmp_path / "pages"
    result = PDFConverter.pdf_to_images(source, output_dir)

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(Path(path).exists() for path in result)


def test_pdf_to_jpeg_exports_jpeg_pages(tmp_path: Path) -> None:
    source = tmp_path / "sample.pdf"
    pdf_canvas = canvas.Canvas(str(source))
    pdf_canvas.drawString(50, 750, "JPEG page")
    pdf_canvas.save()

    result = PDFConverter.pdf_to_images(source, tmp_path / "jpeg_pages", output_format="JPEG")

    assert len(result) == 1
    assert Path(result[0]).suffix == ".jpg"
    assert Path(result[0]).read_bytes().startswith(b"\xff\xd8")


def test_pdf_to_word_extracts_text(tmp_path: Path) -> None:
    from docx import Document

    source = tmp_path / "sample.pdf"
    pdf_canvas = canvas.Canvas(str(source))
    pdf_canvas.drawString(50, 750, "Text for Word")
    pdf_canvas.save()

    output = Path(ConversionService.convert_file(source, "DOCX"))
    word_document = Document(output)

    assert output.suffix == ".docx"
    assert "Text for Word" in "\n".join(paragraph.text for paragraph in word_document.paragraphs)


def test_pdf_supported_formats_are_specific_to_pdf_conversion(tmp_path: Path) -> None:
    source = tmp_path / "sample.pdf"
    source.touch()

    formats = ConversionService.get_supported_formats(source)
    assert {"PNG", "JPEG", "PDF_SPLIT", "PDF_EXTRACT", "PDF_ROTATE", "PDF_COMPRESS"} <= set(formats)


def test_pdf_split_extract_rotate_and_compress(tmp_path: Path) -> None:
    source = tmp_path / "sample.pdf"
    pdf_canvas = canvas.Canvas(str(source))
    for page_number in range(3):
        pdf_canvas.drawString(50, 750, f"Page {page_number + 1}")
        pdf_canvas.showPage()
    pdf_canvas.save()

    split_result = PDFConverter.split_pdf(source, tmp_path / "split")
    extracted = PDFConverter.extract_pages(source, tmp_path / "extracted.pdf", "1,3")
    rotated = PDFConverter.rotate_pages(source, tmp_path / "rotated.pdf")
    compressed = PDFConverter.compress_pdf(source, tmp_path / "compressed.pdf")

    import pymupdf as fitz

    assert len(split_result) == 3
    with fitz.open(extracted) as extracted_document:
        assert extracted_document.page_count == 2
    with fitz.open(rotated) as rotated_document:
        assert rotated_document[0].rotation == 90
    assert Path(compressed).exists()


def test_pdf_merge_creates_a_new_file_without_overwriting(tmp_path: Path) -> None:
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    for path in (first, second):
        pdf_canvas = canvas.Canvas(str(path))
        pdf_canvas.drawString(50, 750, path.stem)
        pdf_canvas.save()
    protected = tmp_path / "first_merged.pdf"
    protected.write_bytes(b"keep")

    result = ConversionService.batch_convert_files([first, second], "PDF_MERGE")

    assert len(result) == 1
    assert Path(result[0]).name == "first_merged_1.pdf"
    assert protected.read_bytes() == b"keep"
