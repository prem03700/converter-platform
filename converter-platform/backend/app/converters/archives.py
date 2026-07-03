"""
Archive format conversions. ZIP <-> TAR <-> TAR.GZ are fully functional
using the Python standard library. 7Z support uses py7zr if installed
(read+write). RAR is read-only by nature of the format (there is no
open-source RAR *writer* — the format is proprietary to WinRAR), so RAR
only appears as a source, never as a target.
"""
import io
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

from app.converters.base import BaseConverter, ConversionError, ConversionResult

ARCHIVE_EXTS = {"zip", "tar", "gz", "7z", "rar"}


class ArchiveConverter(BaseConverter):
    category = "archive"
    supported_conversions = {
        "zip": {"tar", "gz", "7z"},
        "tar": {"zip", "gz", "7z"},
        "gz": {"zip", "tar", "7z"},
        "7z": {"zip", "tar", "gz"},
        "rar": {"zip", "tar", "gz"},  # extract-and-repack only; cannot produce .rar
    }

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            extract_dir = Path(tmpdir) / "extracted"
            extract_dir.mkdir()
            self._extract(data, source_ext, extract_dir)
            output_bytes = self._pack(extract_dir, target_ext)

        mime = {
            "zip": "application/zip",
            "tar": "application/x-tar",
            "gz": "application/gzip",
            "7z": "application/x-7z-compressed",
        }[target_ext]
        return ConversionResult(data=output_bytes, output_extension=target_ext, output_mime_type=mime)

    def _extract(self, data: bytes, source_ext: str, extract_dir: Path) -> None:
        buf = io.BytesIO(data)
        try:
            if source_ext == "zip":
                with zipfile.ZipFile(buf) as zf:
                    zf.extractall(extract_dir)
            elif source_ext == "tar":
                with tarfile.open(fileobj=buf, mode="r:*") as tf:
                    tf.extractall(extract_dir)
            elif source_ext == "gz":
                with tarfile.open(fileobj=buf, mode="r:gz") as tf:
                    tf.extractall(extract_dir)
            elif source_ext == "7z":
                try:
                    import py7zr
                except ImportError as e:
                    raise ConversionError("7z support requires the 'py7zr' package") from e
                with py7zr.SevenZipFile(buf, mode="r") as zf:
                    zf.extractall(extract_dir)
            elif source_ext == "rar":
                try:
                    import rarfile
                except ImportError as e:
                    raise ConversionError(
                        "RAR support requires the 'rarfile' package and the system "
                        "'unrar' (or 'unar') utility to be installed"
                    ) from e
                with rarfile.RarFile(buf) as rf:
                    rf.extractall(extract_dir)
            else:
                raise ConversionError(f"Unsupported archive source: {source_ext}")
        except ConversionError:
            raise
        except Exception as e:
            raise ConversionError(f"Could not extract {source_ext} archive: {e}") from e

    def _pack(self, source_dir: Path, target_ext: str) -> bytes:
        if target_ext == "zip":
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for path in source_dir.rglob("*"):
                    if path.is_file():
                        zf.write(path, path.relative_to(source_dir))
            return buf.getvalue()

        if target_ext in ("tar", "gz"):
            mode = "w:gz" if target_ext == "gz" else "w"
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode=mode) as tf:
                tf.add(source_dir, arcname=".")
            return buf.getvalue()

        if target_ext == "7z":
            try:
                import py7zr
            except ImportError as e:
                raise ConversionError("7z support requires the 'py7zr' package") from e
            with tempfile.NamedTemporaryFile(suffix=".7z", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                with py7zr.SevenZipFile(tmp_path, mode="w") as zf:
                    zf.writeall(source_dir, arcname=".")
                return Path(tmp_path).read_bytes()
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        raise ConversionError(f"Unsupported archive target: {target_ext}")
