from __future__ import annotations

from pathlib import Path
class ImageConverter:
    """Handles raster image conversion tasks in a safe, local-only manner."""

    @staticmethod
    def supported_input_extensions() -> set[str]:
        return {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".ico"}

    @staticmethod
    def supported_output_formats(input_extension: str) -> list[str]:
        normalized = input_extension.lower()
        if normalized not in ImageConverter.supported_input_extensions():
            return []
        formats = ["PNG", "JPEG", "WEBP", "BMP", "TIFF", "GIF", "ICO"]
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
        }.get(normalized)
        return [output_format for output_format in formats if output_format != same_format]

    @staticmethod
    def convert(input_path: str | Path, output_path: str | Path, output_format: str, quality: int = 90, background_color: str = "white") -> str:
        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_file}")

        if not input_file.is_file():
            raise ValueError(f"Input path is not a file: {input_file}")

        output_format = output_format.upper()
        valid_formats = {"PNG", "JPEG", "WEBP", "BMP", "TIFF", "GIF", "ICO"}
        if output_format not in valid_formats:
            raise ValueError(f"Unsupported output format: {output_format}")

        if quality < 1 or quality > 100:
            raise ValueError("Quality must be between 1 and 100")

        try:
            from PIL import Image, UnidentifiedImageError
        except ImportError as exc:
            raise RuntimeError("Pillow is required for image conversion. Install project dependencies and retry.") from exc

        try:
            with Image.open(input_file) as source:
                if source.mode in ("RGBA", "LA", "P") and output_format == "JPEG":
                    image = Image.new("RGB", source.size, background_color)
                    image.paste(source.convert("RGBA"), (0, 0), source.convert("RGBA"))
                    image.convert("RGB").save(output_file, format="JPEG", quality=quality)
                    return str(output_file)

                converted = source.copy()
                if source.mode == "RGBA" and output_format == "PNG":
                    converted = converted.convert("RGBA")
                elif source.mode == "P" and output_format in {"PNG", "WEBP"}:
                    converted = converted.convert("RGBA")
                elif output_format == "PNG" and source.mode not in {"RGB", "L", "RGBA", "P", "LA"}:
                    converted = converted.convert("RGBA")
                elif output_format == "JPEG" and source.mode not in {"RGB", "L", "RGBA", "P", "CMYK"}:
                    converted = converted.convert("RGB")
                elif output_format == "WEBP" and source.mode not in {"RGB", "L", "RGBA", "P", "LA"}:
                    converted = converted.convert("RGBA")

                if output_format == "JPEG":
                    converted = converted.convert("RGB")
                    converted.save(output_file, format="JPEG", quality=quality)
                elif output_format == "WEBP":
                    converted.save(output_file, format="WEBP", quality=quality)
                elif output_format == "GIF":
                    rgba = converted.convert("RGBA")
                    alpha = rgba.getchannel("A")
                    converted = rgba.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT)
                    transparent_mask = alpha.point(lambda value: 255 if value < 128 else 0)
                    converted.paste(255, mask=transparent_mask)
                    converted.save(output_file, format=output_format, transparency=255)
                else:
                    converted.save(output_file, format=output_format)

                return str(output_file)
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise ValueError(f"Unable to convert image: {exc}") from exc
