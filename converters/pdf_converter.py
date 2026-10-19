from __future__ import annotations

from pathlib import Path


def _pymupdf_module():
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    return pymupdf


class PDFConverter:
    """Local PDF conversion utilities using PyMuPDF and ReportLab."""

    @staticmethod
    def supported_input_extensions() -> set[str]:
        return {".pdf"}

    @staticmethod
    def supported_output_formats(input_extension: str) -> list[str]:
        normalized = input_extension.lower()
        if normalized == ".pdf":
            return ["PNG", "JPEG", "DOCX"]
        return []

    @staticmethod
    def pdf_to_docx(input_path: str | Path, output_path: str | Path) -> str:
        source = Path(input_path)
        destination = Path(output_path)
        from pdf2docx import Converter

        converter = Converter(str(source))
        try:
            converter.convert(str(destination))
        finally:
            converter.close()
        return str(destination)

    @staticmethod
    def text_to_pdf(input_path: str | Path, output_path: str | Path) -> str:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        source = Path(input_path)
        destination = Path(output_path)
        text = source.read_text(encoding="utf-8", errors="replace")
        pdf_canvas = canvas.Canvas(str(destination), pagesize=letter)
        pdf_canvas.setTitle(source.name)
        lines = text.splitlines()
        y_position = 750
        for line in lines:
            if y_position < 50:
                pdf_canvas.showPage()
                y_position = 750
            pdf_canvas.drawString(50, y_position, line[:110])
            y_position -= 18
        pdf_canvas.save()
        return str(destination)

    @staticmethod
    def pdf_to_images(
        input_path: str | Path,
        output_dir: str | Path,
        output_format: str = "PNG",
        page_range: str | None = None,
    ) -> list[str]:
        fitz = _pymupdf_module()

        source = Path(input_path)
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        normalized_format = output_format.upper()
        extensions = {"PNG": ".png", "JPEG": ".jpg"}
        if normalized_format not in extensions:
            raise ValueError(f"Unsupported PDF image format: {output_format}")

        doc = fitz.open(str(source))
        output_paths: list[str] = []
        try:
            selected_pages = (
                set(PDFConverter._parse_page_range(page_range, doc.page_count))
                if page_range
                else None
            )
            for page_index in range(doc.page_count):
                if selected_pages is not None and page_index not in selected_pages:
                    continue
                page = doc[page_index]
                image = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                file_name = output / f"{source.stem}_page_{page_index + 1}{extensions[normalized_format]}"
                image.save(str(file_name))
                output_paths.append(str(file_name))
        finally:
            doc.close()
        return output_paths

    @staticmethod
    def merge_pdfs(input_paths: list[str | Path], output_path: str | Path) -> str:
        fitz = _pymupdf_module()

        if not input_paths:
            raise ValueError("At least one PDF is required to merge.")
        output = Path(output_path)
        merged = fitz.open()
        for path in input_paths:
            pdf = fitz.open(str(path))
            merged.insert_pdf(pdf)
            pdf.close()
        merged.save(str(output))
        merged.close()
        return str(output)

    @staticmethod
    def split_pdf(input_path: str | Path, output_dir: str | Path) -> list[str]:
        fitz = _pymupdf_module()

        source = Path(input_path)
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=False)
        document = fitz.open(str(source))
        output_paths: list[str] = []
        try:
            for page_index in range(document.page_count):
                page_document = fitz.open()
                page_document.insert_pdf(document, from_page=page_index, to_page=page_index)
                page_path = output / f"{source.stem}_page_{page_index + 1}.pdf"
                page_document.save(str(page_path))
                page_document.close()
                output_paths.append(str(page_path))
        finally:
            document.close()
        return output_paths

    @staticmethod
    def extract_pages(input_path: str | Path, output_path: str | Path, page_range: str) -> str:
        fitz = _pymupdf_module()

        source = Path(input_path)
        destination = Path(output_path)
        document = fitz.open(str(source))
        output = fitz.open()
        try:
            indexes = PDFConverter._parse_page_range(page_range, document.page_count)
            if not indexes:
                raise ValueError("Enter at least one valid page number or range, such as 1-3,5.")
            for page_index in indexes:
                output.insert_pdf(document, from_page=page_index, to_page=page_index)
            output.save(str(destination))
        finally:
            output.close()
            document.close()
        return str(destination)

    @staticmethod
    def rotate_pages(input_path: str | Path, output_path: str | Path, degrees: int = 90) -> str:
        fitz = _pymupdf_module()

        if degrees not in {90, 180, 270}:
            raise ValueError("Rotation must be 90, 180, or 270 degrees.")
        source = Path(input_path)
        destination = Path(output_path)
        document = fitz.open(str(source))
        try:
            for page in document:
                page.set_rotation((page.rotation + degrees) % 360)
            document.save(str(destination), garbage=3, deflate=True)
        finally:
            document.close()
        return str(destination)

    @staticmethod
    def compress_pdf(input_path: str | Path, output_path: str | Path) -> str:
        fitz = _pymupdf_module()

        source = Path(input_path)
        destination = Path(output_path)
        document = fitz.open(str(source))
        try:
            document.save(str(destination), garbage=4, deflate=True, clean=True)
        finally:
            document.close()
        return str(destination)

    @staticmethod
    def _parse_page_range(page_range: str, page_count: int) -> list[int]:
        indexes: set[int] = set()
        for part in page_range.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start, end = int(start_text), int(end_text)
                if start < 1 or end < start or end > page_count:
                    raise ValueError(f"Page range '{part}' is outside the PDF's 1-{page_count} page range.")
                indexes.update(range(start - 1, end))
            else:
                page_number = int(part)
                if page_number < 1 or page_number > page_count:
                    raise ValueError(f"Page {page_number} is outside the PDF's 1-{page_count} page range.")
                indexes.add(page_number - 1)
        return sorted(indexes)
