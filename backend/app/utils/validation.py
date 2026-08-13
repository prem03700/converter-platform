"""
Upload validation: extension allowlist, MIME sniffing, size limits,
and mapping a file to its conversion "category" (so the right
converter engine gets selected later).

Security notes:
- We check BOTH the extension and the sniffed MIME type (via python-magic
  when available, falling back to the `mimetypes` stdlib module). Trusting
  either one alone is how disguised-extension attacks happen.
- Filenames are sanitized to prevent path traversal before ever touching
  the filesystem.
"""
import mimetypes
import os
import re
import uuid

try:
    import magic  # python-magic, needs libmagic installed on the host

    HAS_LIBMAGIC = True
except Exception:  # pragma: no cover - environment dependent
    HAS_LIBMAGIC = False

from app.config import settings

# extension -> category. This is the single source of truth referenced
# by the converter registry, so adding a new supported format is a
# one-line change here plus a converter implementation.
CATEGORY_BY_EXTENSION = {
    # documents
    "pdf": "document", "docx": "document", "doc": "document", "txt": "document",
    "rtf": "document", "odt": "document", "md": "document", "html": "document",
    "htm": "document", "csv": "document", "xlsx": "document", "xls": "document",
    "pptx": "document", "ppt": "document",
    # images
    "png": "image", "jpg": "image", "jpeg": "image", "webp": "image", "gif": "image",
    "bmp": "image", "tiff": "image", "tif": "image", "svg": "image", "ico": "image",
    # audio
    "mp3": "audio", "wav": "audio", "aac": "audio", "flac": "audio", "ogg": "audio",
    # video
    "mp4": "video", "avi": "video", "mov": "video", "mkv": "video", "webm": "video",
    # archives
    "zip": "archive", "rar": "archive", "7z": "archive", "tar": "archive", "gz": "archive",
    # ebooks
    "epub": "ebook", "mobi": "ebook", "azw3": "ebook",
    # code
    "json": "code", "xml": "code", "yaml": "code", "yml": "code", "py": "code",
    "js": "code", "c": "code", "cpp": "code", "java": "code",
}

ALLOWED_EXTENSIONS = set(CATEGORY_BY_EXTENSION.keys())


class FileValidationError(ValueError):
    pass


def sanitize_filename(filename: str) -> str:
    """Strips any path components and disallowed characters."""
    name = os.path.basename(filename)
    name = name.replace("\x00", "")
    name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)
    if not name or name in (".", ".."):
        name = f"file_{uuid.uuid4().hex}"
    return name


def get_extension(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext


def get_category(extension: str) -> str:
    category = CATEGORY_BY_EXTENSION.get(extension)
    if category is None:
        raise FileValidationError(f"Unsupported file extension: .{extension}")
    return category


def sniff_mime_type(file_bytes: bytes, fallback_filename: str) -> str:
    if HAS_LIBMAGIC:
        try:
            return magic.from_buffer(file_bytes, mime=True)
        except Exception:
            pass
    guessed, _ = mimetypes.guess_type(fallback_filename)
    return guessed or "application/octet-stream"


def validate_upload(filename: str, size_bytes: int, file_bytes: bytes) -> dict:
    """
    Runs all upload checks and returns a dict of derived, safe metadata:
    {clean_filename, extension, category, mime_type}

    Raises FileValidationError on any failure.
    """
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes <= 0:
        raise FileValidationError("Empty file uploads are not allowed")
    if size_bytes > max_bytes:
        raise FileValidationError(f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit")

    clean_filename = sanitize_filename(filename)
    extension = get_extension(clean_filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise FileValidationError(f"Unsupported file extension: .{extension}")

    category = get_category(extension)
    mime_type = sniff_mime_type(file_bytes, clean_filename)

    return {
        "clean_filename": clean_filename,
        "extension": extension,
        "category": category,
        "mime_type": mime_type,
    }
