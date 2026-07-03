"""
Converter registry.

This is the "select the appropriate conversion engine" step from the
spec's conversion flow. Converters are tried in order; the first one
that declares support for the requested (source_ext -> target_ext) pair
wins. To add a new format: write a BaseConverter subclass and add it to
_ALL_CONVERTERS — nothing else in the app needs to change.
"""
from functools import lru_cache

from app.converters.archives import ArchiveConverter
from app.converters.base import BaseConverter, ConversionError
from app.converters.code import CodeToHtmlConverter, DataFormatConverter
from app.converters.documents_text import TextDocConverter
from app.converters.ebooks import EbookConverter
from app.converters.images import ImageConverter
from app.converters.office import OfficeConverter
from app.converters.pdf import PdfConverter
from app.converters.video import VideoConverter
from app.converters.audio import AudioConverter

# Order matters: lighter-weight / no-external-binary converters are
# tried before the heavier LibreOffice fallback.
_ALL_CONVERTERS: list[type[BaseConverter]] = [
    ImageConverter,
    PdfConverter,
    TextDocConverter,
    DataFormatConverter,
    CodeToHtmlConverter,
    ArchiveConverter,
    VideoConverter,
    AudioConverter,
    EbookConverter,
    OfficeConverter,  # general office fallback, tried last
]


@lru_cache
def _instances() -> list[BaseConverter]:
    return [cls() for cls in _ALL_CONVERTERS]


def get_converter(source_ext: str, target_ext: str) -> BaseConverter:
    source_ext, target_ext = source_ext.lower(), target_ext.lower()
    for converter in _instances():
        if converter.supports(source_ext, target_ext):
            return converter
    raise ConversionError(f"No converter available for .{source_ext} -> .{target_ext}")


def list_supported_targets(source_ext: str) -> set[str]:
    targets: set[str] = set()
    for converter in _instances():
        targets |= converter.supported_conversions.get(source_ext.lower(), set())
    return targets
