from __future__ import annotations

from pathlib import Path

from converters.audio_video_converter import AudioVideoConverter


def test_audio_supported_formats() -> None:
    assert ".mp3" in AudioVideoConverter.supported_input_extensions()
    assert "MP3" in AudioVideoConverter.supported_output_formats(".wav")


def test_video_conversion_uses_ffmpeg(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "clip.mp4"
    source.write_bytes(b"fake video")
    target = tmp_path / "clip_converted.mp4"

    calls = []

    def fake_run(cmd, capture_output, text):
        calls.append(cmd)
        return type("Result", (), {"returncode": 0, "stderr": "", "stdout": ""})()

    monkeypatch.setattr("converters.audio_video_converter.shutil.which", lambda _: "ffmpeg")
    monkeypatch.setattr("converters.audio_video_converter.subprocess.run", fake_run)

    result = AudioVideoConverter.convert(source, target, "MP4")

    assert result == str(target)
    assert calls and calls[0][0] == "ffmpeg"


def test_missing_ffmpeg_raises_runtime_error(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "clip.mp4"
    source.write_bytes(b"fake video")

    monkeypatch.setattr("converters.audio_video_converter.shutil.which", lambda _: None)

    try:
        AudioVideoConverter.convert(source, tmp_path / "out.mp4", "MP4")
        assert False, "Expected RuntimeError when ffmpeg is missing"
    except RuntimeError:
        pass
