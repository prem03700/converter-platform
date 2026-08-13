"""
Video conversions via FFmpeg. Fully functional — requires the `ffmpeg`
binary on the host (already present in the project's Docker image).
"""
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from app.converters.base import BaseConverter, ConversionError, ConversionResult

VIDEO_EXTS = {"mp4", "avi", "mov", "mkv", "webm"}

CODEC_ARGS = {
    "mp4": ["-c:v", "libx264", "-c:a", "aac"],
    "webm": ["-c:v", "libvpx-vp9", "-c:a", "libopus"],
    "avi": ["-c:v", "mpeg4", "-c:a", "mp3"],
    "mov": ["-c:v", "libx264", "-c:a", "aac"],
    "mkv": ["-c:v", "libx264", "-c:a", "aac"],
}

MIME_TYPES = {
    "mp4": "video/mp4", "avi": "video/x-msvideo", "mov": "video/quicktime",
    "mkv": "video/x-matroska", "webm": "video/webm",
}

FFMPEG_TIMEOUT_SECONDS = 600


class VideoConverter(BaseConverter):
    category = "video"
    supported_conversions = {ext: VIDEO_EXTS - {ext} for ext in VIDEO_EXTS}

    def __init__(self):
        self._ffmpeg_path = shutil.which("ffmpeg")

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        if not self._ffmpeg_path:
            raise ConversionError("FFmpeg is not installed on this server.")
        options = options or {}

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_path = tmp / f"{uuid.uuid4().hex}.{source_ext}"
            output_path = tmp / f"{uuid.uuid4().hex}.{target_ext}"
            input_path.write_bytes(data)

            cmd = [self._ffmpeg_path, "-y", "-i", str(input_path), *CODEC_ARGS.get(target_ext, [])]
            if "resolution" in options:
                cmd += ["-vf", f"scale={options['resolution']}"]
            if "bitrate" in options:
                cmd += ["-b:v", options["bitrate"]]
            cmd.append(str(output_path))

            try:
                result = subprocess.run(
                    cmd, capture_output=True, timeout=FFMPEG_TIMEOUT_SECONDS, check=False,
                )
            except subprocess.TimeoutExpired as e:
                raise ConversionError("Video conversion timed out") from e

            if result.returncode != 0 or not output_path.exists():
                stderr = result.stderr.decode(errors="ignore") if result.stderr else ""
                raise ConversionError(f"FFmpeg conversion failed: {stderr[-500:]}")

            output_bytes = output_path.read_bytes()

        return ConversionResult(
            data=output_bytes, output_extension=target_ext,
            output_mime_type=MIME_TYPES.get(target_ext, "application/octet-stream"),
        )
