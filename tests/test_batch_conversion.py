from __future__ import annotations

from pathlib import Path

from PIL import Image

from services.conversion_service import ConversionService


def test_batch_convert_files_creates_multiple_outputs(tmp_path: Path) -> None:
    first = tmp_path / "one.png"
    second = tmp_path / "two.png"
    Image.new("RGBA", (10, 10), (255, 0, 0, 255)).save(first)
    Image.new("RGBA", (12, 8), (0, 255, 0, 255)).save(second)

    outputs = ConversionService.batch_convert_files([first, second], "JPEG", quality=85)

    assert len(outputs) == 2
    assert all(Path(path).exists() for path in outputs)
    assert all(Path(path).suffix.lower() in {".jpeg", ".jpg"} for path in outputs)
