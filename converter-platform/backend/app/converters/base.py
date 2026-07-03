"""
Common converter interface.

Every converter (images, documents, audio, video, archives, ebooks...)
implements this same interface, which is what makes the architecture
"add a new format = minimal changes": write a class with `convert()`,
declare which extensions it supports, and register it.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class ConversionError(Exception):
    """Raised by a converter when a conversion cannot be completed."""


@dataclass
class ConversionResult:
    data: bytes
    output_extension: str
    output_mime_type: str
    metadata: Optional[dict] = None  # e.g. extracted text, page count, AI tags...


class BaseConverter(ABC):
    #: e.g. "image", "document", "audio", "video", "archive", "ebook", "code"
    category: str = ""

    #: {"source_ext": {"target_ext", "target_ext", ...}}
    supported_conversions: dict[str, set[str]] = {}

    def supports(self, source_ext: str, target_ext: str) -> bool:
        return target_ext in self.supported_conversions.get(source_ext, set())

    @abstractmethod
    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        """Performs the conversion and returns the resulting bytes + metadata."""
