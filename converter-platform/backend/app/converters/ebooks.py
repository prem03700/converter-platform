"""
Ebook conversions (EPUB / MOBI / AZW3).

STATUS: scaffold only — not functional in this build. The standard
open-source tool for this is Calibre's `ebook-convert` CLI, which is a
large (~1GB+) install pulling in a full Qt stack. It was intentionally
NOT installed in this build to keep the image lean; install the
`calibre` package on the server/worker and this converter will work
as written below. This class deliberately raises a clear error instead
of silently failing or pretending to convert.
"""
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from app.converters.base import BaseConverter, ConversionError, ConversionResult

EBOOK_EXTS = {"epub", "mobi", "azw3"}

MIME_TYPES = {
    "epub": "application/epub+zip",
    "mobi": "application/x-mobipocket-ebook",
    "azw3": "application/vnd.amazon.ebook",
}


class EbookConverter(BaseConverter):
    category = "ebook"
    supported_conversions = {ext: EBOOK_EXTS - {ext} for ext in EBOOK_EXTS}

    def __init__(self):
        self._ebook_convert_path = shutil.which("ebook-convert")

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        if not self._ebook_convert_path:
            raise ConversionError(
                "Ebook conversion requires Calibre's 'ebook-convert' CLI, which "
                "is not installed on this server. Install the 'calibre' package "
                "to enable EPUB/MOBI/AZW3 conversions."
            )
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_path = tmp / f"{uuid.uuid4().hex}.{source_ext}"
            output_path = tmp / f"{uuid.uuid4().hex}.{target_ext}"
            input_path.write_bytes(data)

            result = subprocess.run(
                [self._ebook_convert_path, str(input_path), str(output_path)],
                capture_output=True, timeout=300, check=False,
            )
            if result.returncode != 0 or not output_path.exists():
                stderr = result.stderr.decode(errors="ignore") if result.stderr else ""
                raise ConversionError(f"ebook-convert failed: {stderr[-500:]}")
            output_bytes = output_path.read_bytes()

        return ConversionResult(
            data=output_bytes, output_extension=target_ext,
            output_mime_type=MIME_TYPES.get(target_ext, "application/octet-stream"),
        )
