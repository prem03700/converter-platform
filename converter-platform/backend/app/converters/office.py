"""
Office document conversions via LibreOffice headless, exactly as named
in the spec. This is the general-purpose fallback for office formats
that don't have a lighter-weight pure-Python path (e.g. DOCX -> PDF,
PPTX -> PDF, ODT -> DOCX, XLSX -> CSV).

Requires the `soffice` binary (package: libreoffice) to be installed on
the host / present in the Docker image. Each call spins up a fresh,
isolated LibreOffice user profile so concurrent conversions on the same
worker don't collide.
"""
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from app.converters.base import BaseConverter, ConversionError, ConversionResult

OFFICE_EXTS = {"docx", "doc", "odt", "rtf", "pptx", "ppt", "xlsx", "xls"}
TARGET_EXTS = OFFICE_EXTS | {"pdf", "csv", "txt", "html"}

MIME_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
    "odt": "application/vnd.oasis.opendocument.text",
    "rtf": "application/rtf",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "ppt": "application/vnd.ms-powerpoint",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "csv": "text/csv",
    "txt": "text/plain",
    "html": "text/html",
}

SOFFICE_TIMEOUT_SECONDS = 120


class OfficeConverter(BaseConverter):
    category = "document"
    supported_conversions = {ext: TARGET_EXTS - {ext} for ext in OFFICE_EXTS}

    def __init__(self):
        self._soffice_path = shutil.which("soffice") or shutil.which("libreoffice")

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        if not self._soffice_path:
            raise ConversionError(
                "LibreOffice ('soffice') is not installed on this server. "
                "Install the 'libreoffice' package to enable office document conversions."
            )
        if target_ext not in TARGET_EXTS:
            raise ConversionError(f"Unsupported office target format: {target_ext}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_path = tmp_path / f"input.{source_ext}"
            input_path.write_bytes(data)

            profile_dir = tmp_path / f"profile_{uuid.uuid4().hex}"
            cmd = [
                self._soffice_path,
                "--headless",
                "--norestore",
                f"-env:UserInstallation=file://{profile_dir}",
                "--convert-to", target_ext,
                "--outdir", str(tmp_path),
                str(input_path),
            ]
            try:
                result = subprocess.run(
                    cmd, capture_output=True, timeout=SOFFICE_TIMEOUT_SECONDS, check=False,
                )
            except subprocess.TimeoutExpired as e:
                raise ConversionError("LibreOffice conversion timed out") from e

            output_path = tmp_path / f"input.{target_ext}"
            if result.returncode != 0 or not output_path.exists():
                stderr = result.stderr.decode(errors="ignore") if result.stderr else ""
                raise ConversionError(f"LibreOffice conversion failed: {stderr[:500]}")

            output_bytes = output_path.read_bytes()

        return ConversionResult(
            data=output_bytes,
            output_extension=target_ext,
            output_mime_type=MIME_TYPES.get(target_ext, "application/octet-stream"),
        )
