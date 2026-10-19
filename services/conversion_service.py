from __future__ import annotations

from pathlib import Path

from converters.pdf_converter import PDFConverter

from .dependency_check import DependencyChecker
from .registry import get_registry


class ConversionService:
    """Find the supported conversion routes for a file and run a conversion."""

    @staticmethod
    def get_supported_formats(file_path: str | Path) -> list[str]:
        path = Path(file_path)
        suffix = path.suffix.lower()
        for entry in get_registry():
            if suffix in entry.extensions:
                if entry.kind == "audio-video":
                    from converters.audio_video_converter import AudioVideoConverter

                    values = AudioVideoConverter.supported_output_formats(suffix)
                    return [
                        value for value in values
                        if DependencyChecker.dependency_available("ffmpeg")
                    ]
                available = [
                    option.value
                    for option in entry.options
                    if all(DependencyChecker.dependency_available(name) for name in option.required_dependencies)
                ]
                if entry.kind == "image":
                    same_format = {
                        ".png": "PNG",
                        ".jpg": "JPEG",
                        ".jpeg": "JPEG",
                        ".webp": "WEBP",
                        ".bmp": "BMP",
                        ".tif": "TIFF",
                        ".tiff": "TIFF",
                        ".gif": "GIF",
                        ".ico": "ICO",
                    }.get(suffix)
                    return [output_format for output_format in available if output_format != same_format]
                return available
        return []

    @staticmethod
    def get_common_formats(file_paths: list[str | Path]) -> list[str]:
        if not file_paths:
            return []
        common_formats = ConversionService.get_supported_formats(file_paths[0])
        for file_path in file_paths[1:]:
            supported = set(ConversionService.get_supported_formats(file_path))
            common_formats = [fmt for fmt in common_formats if fmt in supported]
        if len(file_paths) > 1 and all(Path(path).suffix.lower() == ".pdf" for path in file_paths):
            if DependencyChecker.dependency_available("PyMuPDF"):
                common_formats.append("PDF_MERGE")
        return common_formats

    @staticmethod
    def get_unavailable_format_messages(file_path: str | Path) -> list[str]:
        suffix = Path(file_path).suffix.lower()
        messages: list[str] = []
        for entry in get_registry():
            if suffix not in entry.extensions:
                continue
            for option in entry.options:
                missing = [
                    dependency
                    for dependency in option.required_dependencies
                    if not DependencyChecker.dependency_available(dependency)
                ]
                if missing:
                    explanation = DependencyChecker.explain_missing(file_path, option.value)
                    if explanation:
                        if explanation not in messages:
                            messages.append(explanation)
        return messages

    @staticmethod
    def get_format_label(file_path: str | Path, output_format: str) -> str:
        for entry in get_registry():
            if Path(file_path).suffix.lower() in entry.extensions:
                for option in entry.options:
                    if option.value == output_format:
                        return option.label
        if output_format == "PDF_MERGE":
            return "Merge selected PDFs"
        return output_format

    @staticmethod
    def build_output_path(input_path: str | Path, target_format: str) -> Path:
        source_path = Path(input_path)
        stem = source_path.stem
        target_ext = f".{target_format.lower()}"
        candidate = source_path.with_name(f"{stem}_converted{target_ext}")

        counter = 1
        while candidate.exists():
            candidate = source_path.with_name(f"{stem}_converted_{counter}{target_ext}")
            counter += 1
        return candidate

    @staticmethod
    def build_output_directory(input_path: str | Path, description: str) -> Path:
        source_path = Path(input_path)
        candidate = source_path.with_name(f"{source_path.stem}_converted_{description}")
        counter = 1
        while candidate.exists():
            candidate = source_path.with_name(f"{source_path.stem}_converted_{description}_{counter}")
            counter += 1
        return candidate

    @staticmethod
    def batch_convert_files(
        file_paths: list[str | Path],
        output_format: str,
        quality: int = 90,
        background_color: str = "white",
        page_range: str = "",
    ) -> list[str]:
        if output_format.upper() == "PDF_MERGE":
            if len(file_paths) < 2 or any(Path(path).suffix.lower() != ".pdf" for path in file_paths):
                raise ValueError("PDF merge requires at least two PDF files.")
            stem = Path(file_paths[0]).stem
            target = Path(file_paths[0]).with_name(f"{stem}_merged.pdf")
            counter = 1
            while target.exists():
                target = Path(file_paths[0]).with_name(f"{stem}_merged_{counter}.pdf")
                counter += 1
            for file_path in file_paths:
                ConversionService.validate_conversion(file_path, "PDF_MERGE")
            return [PDFConverter.merge_pdfs(file_paths, target)]

        unsupported = [
            str(file_path)
            for file_path in file_paths
            if output_format.upper() not in ConversionService.get_supported_formats(file_path)
        ]
        if unsupported:
            raise ValueError(
                f"Output format {output_format} is not supported for: {', '.join(unsupported)}"
            )
        results: list[str] = []
        for file_path in file_paths:
            results.append(
                ConversionService.convert_file(
                    file_path,
                    output_format,
                    quality=quality,
                    background_color=background_color,
                    page_range=page_range,
                )
            )
        return results

    @staticmethod
    def validate_conversion(input_path: str | Path, output_format: str, quality: int = 90, background_color: str = "white") -> None:
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file does not exist: {path}")
        if not path.is_file():
            raise ValueError(f"Input path is not a file: {path}")
        missing = DependencyChecker.check_dependencies_for(input_path, output_format)
        if missing:
            raise RuntimeError(DependencyChecker.explain_missing(input_path, output_format))

    @staticmethod
    def convert_file(
        input_path: str | Path,
        output_format: str,
        quality: int = 90,
        background_color: str = "white",
        page_range: str = "",
    ) -> str:
        source_path = Path(input_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Input file does not exist: {source_path}")
        if not source_path.is_file():
            raise ValueError(f"Input path is not a file: {source_path}")
        suffix = source_path.suffix.lower()
        output_format = output_format.upper()
        entries = get_registry()

        ConversionService.validate_conversion(source_path, output_format, quality=quality, background_color=background_color)
        if output_format not in ConversionService.get_supported_formats(source_path):
            raise ValueError(f"Output format {output_format} is not supported for {source_path.suffix or 'this file type'}.")

        for entry in entries:
            if suffix not in entry.extensions:
                continue

            if entry.kind == "image":
                return entry.conversion_function(
                    source_path,
                    ConversionService.build_output_path(source_path, output_format),
                    output_format,
                    quality=quality,
                    background_color=background_color,
                )

            if entry.kind == "document":
                target = ConversionService.build_output_path(source_path, "pdf")
                return entry.conversion_function(source_path, target)

            if entry.kind == "office":
                target = ConversionService.build_output_path(source_path, "pdf")
                return entry.conversion_function(source_path, target)

            if entry.kind == "spreadsheet":
                target = ConversionService.build_output_path(source_path, output_format.lower())
                return entry.conversion_function(source_path, target)

            if entry.kind == "pdf":
                if output_format in {"PNG", "JPEG"}:
                    output_dir = ConversionService.build_output_directory(
                        source_path,
                        f"{output_format.lower()}_pages",
                    )
                    converted = PDFConverter.pdf_to_images(
                        source_path,
                        output_dir,
                        output_format=output_format,
                        page_range=page_range or None,
                    )
                    return converted[0] if converted else str(output_dir)
                if output_format == "DOCX":
                    return PDFConverter.pdf_to_docx(
                        source_path,
                        ConversionService.build_output_path(source_path, "docx"),
                    )
                if output_format == "PDF_SPLIT":
                    output_dir = ConversionService.build_output_directory(source_path, "split")
                    converted = PDFConverter.split_pdf(source_path, output_dir)
                    return converted[0] if converted else str(output_dir)
                if output_format == "PDF_EXTRACT":
                    if not page_range:
                        raise ValueError("Enter page numbers to extract, such as 1-3,5.")
                    return PDFConverter.extract_pages(
                        source_path,
                        ConversionService.build_output_path(source_path, "pdf"),
                        page_range,
                    )
                if output_format == "PDF_ROTATE":
                    return PDFConverter.rotate_pages(
                        source_path,
                        ConversionService.build_output_path(source_path, "pdf"),
                    )
                if output_format == "PDF_COMPRESS":
                    return PDFConverter.compress_pdf(
                        source_path,
                        ConversionService.build_output_path(source_path, "pdf"),
                    )
                if output_format == "PDF_MERGE":
                    raise ValueError("Select at least two PDFs to merge.")

            if entry.kind == "audio-video":
                return entry.conversion_function(
                    source_path,
                    ConversionService.build_output_path(source_path, output_format),
                    output_format,
                    quality=7,
                )

        raise ValueError(f"Unsupported file type: {source_path}")
