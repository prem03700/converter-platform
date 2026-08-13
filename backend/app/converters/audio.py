"""
Audio conversions via FFmpeg. Fully functional.
"""
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from app.converters.base import BaseConverter, ConversionError, ConversionResult

AUDIO_EXTS = {"mp3", "wav", "aac", "flac", "ogg"}

CODEC_ARGS = {
    "mp3": ["-c:a", "libmp3lame"],
    "wav": ["-c:a", "pcm_s16le"],
    "aac": ["-c:a", "aac"],
    "flac": ["-c:a", "flac"],
    "ogg": ["-c:a", "libvorbis"],
}

MIME_TYPES = {
    "mp3": "audio/mpeg", "wav": "audio/wav", "aac": "audio/aac",
    "flac": "audio/flac", "ogg": "audio/ogg",
}

FFMPEG_TIMEOUT_SECONDS = 300


class AudioConverter(BaseConverter):
    category = "audio"
    supported_conversions = {ext: AUDIO_EXTS - {ext} for ext in AUDIO_EXTS}

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
            if "bitrate" in options:
                cmd += ["-b:a", options["bitrate"]]
            cmd.append(str(output_path))

            try:
                result = subprocess.run(
                    cmd, capture_output=True, timeout=FFMPEG_TIMEOUT_SECONDS, check=False,
                )
            except subprocess.TimeoutExpired as e:
                raise ConversionError("Audio conversion timed out") from e

            if result.returncode != 0 or not output_path.exists():
                stderr = result.stderr.decode(errors="ignore") if result.stderr else ""
                raise ConversionError(f"FFmpeg conversion failed: {stderr[-500:]}")

            output_bytes = output_path.read_bytes()

        return ConversionResult(
            data=output_bytes, output_extension=target_ext,
            output_mime_type=MIME_TYPES.get(target_ext, "application/octet-stream"),
        )
