"""
Lightweight text-document conversions that need no external binaries:
TXT <-> MD <-> HTML. This is fully functional.
"""
from typing import Optional

import markdown as md_lib
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md

from app.converters.base import BaseConverter, ConversionError, ConversionResult

TEXT_FAMILY = {"txt", "md", "html"}

MIME = {"txt": "text/plain", "md": "text/markdown", "html": "text/html"}


class TextDocConverter(BaseConverter):
    category = "document"
    supported_conversions = {ext: TEXT_FAMILY - {ext} for ext in TEXT_FAMILY}

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ConversionError(f"Could not decode source as UTF-8 text: {e}") from e

        # Normalize the source into plain text + an HTML representation.
        if source_ext == "md":
            html = md_lib.markdown(text, extensions=["tables", "fenced_code"])
            plain = BeautifulSoup(html, "html.parser").get_text("\n")
        elif source_ext == "html":
            html = text
            plain = BeautifulSoup(html, "html.parser").get_text("\n")
        else:  # txt
            plain = text
            html = "<html><body>\n" + "\n".join(f"<p>{line}</p>" for line in text.splitlines()) + "\n</body></html>"

        if target_ext == "txt":
            out = plain.encode("utf-8")
        elif target_ext == "html":
            out = html.encode("utf-8")
        elif target_ext == "md":
            out = html_to_md(html, heading_style="ATX").strip().encode("utf-8")
        else:
            raise ConversionError(f"Unsupported text target: {target_ext}")

        return ConversionResult(data=out, output_extension=target_ext, output_mime_type=MIME[target_ext])
