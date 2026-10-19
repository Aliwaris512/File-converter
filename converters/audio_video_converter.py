from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class AudioVideoConverter:
    """Audio and video conversion using FFmpeg as a local engine."""

    @staticmethod
    def supported_input_extensions() -> set[str]:
        return {".mp3", ".wav", ".mp4", ".m4a", ".mov", ".avi", ".mkv", ".webm", ".flac"}

    @staticmethod
    def supported_output_formats(input_extension: str) -> list[str]:
        normalized = input_extension.lower()
        if normalized in {".mp3", ".wav", ".flac", ".m4a"}:
            return ["MP3", "WAV"]
        if normalized in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
            return ["MP4", "WEBM", "AVI"]
        return []

    @staticmethod
    def _ffmpeg_path() -> str:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("FFmpeg is not installed or not on PATH. Install FFmpeg to enable audio/video conversion.")
        return ffmpeg

    @staticmethod
    def convert(input_path: str | Path, output_path: str | Path, output_format: str, quality: int = 7) -> str:
        source = Path(input_path)
        destination = Path(output_path)
        format_name = output_format.upper()

        if not source.exists():
            raise FileNotFoundError(f"Input file does not exist: {source}")

        ffmpeg = AudioVideoConverter._ffmpeg_path()
        if source.suffix.lower() in {".mp3", ".wav", ".m4a", ".flac"}:
            if format_name not in {"MP3", "WAV"}:
                raise ValueError(f"Unsupported audio output format: {output_format}")
            cmd = [
                ffmpeg,
                "-y",
                "-i",
                str(source),
                "-vn",
                "-ar",
                "44100",
                "-acodec",
                "libmp3lame" if format_name == "MP3" else "pcm_s16le",
            ]
            if format_name == "MP3":
                cmd.extend(["-q:a", str(max(1, min(9, quality)))])
            cmd.append(str(destination))
        elif source.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
            if format_name not in {"MP4", "WEBM", "AVI"}:
                raise ValueError(f"Unsupported video output format: {output_format}")
            cmd = [ffmpeg, "-y", "-i", str(source)]
            if format_name == "MP4":
                cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", "-pix_fmt", "yuv420p"])
            elif format_name == "WEBM":
                cmd.extend(["-c:v", "libvpx-vp9", "-c:a", "libopus", "-pix_fmt", "yuv420p"])
            else:
                cmd.extend(["-c:v", "mpeg4", "-c:a", "mp3"])
            cmd.append(str(destination))
        else:
            raise ValueError(f"Unsupported media type: {source.suffix}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip() or "FFmpeg conversion failed."
            raise RuntimeError(message)
        return str(destination)
