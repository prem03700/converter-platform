"""
Code/data file conversions.

JSON <-> YAML <-> XML are genuine structural conversions (fully
functional, via PyYAML + xmltodict/dicttoxml).

For source code (Python/JS/C/C++/Java), a byte-for-byte "conversion" to
another language isn't a well-defined, safe operation (that's
transpilation, not file conversion, and doing it reliably needs a real
compiler toolchain or an LLM with no correctness guarantees). What IS
useful and fully supported here: rendering any code file to syntax-
highlighted HTML for preview/sharing, via Pygments.
"""
import json
from typing import Optional

import dicttoxml
import xmltodict
import yaml
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

from app.converters.base import BaseConverter, ConversionError, ConversionResult

DATA_EXTS = {"json", "xml", "yaml", "yml"}
CODE_EXTS = {"py", "js", "c", "cpp", "java"}


class DataFormatConverter(BaseConverter):
    """JSON / XML / YAML <-> each other."""

    category = "code"
    supported_conversions = {
        "json": {"xml", "yaml", "yml"},
        "yaml": {"json", "xml", "yml"},
        "yml": {"json", "xml", "yaml"},
        "xml": {"json", "yaml", "yml"},
    }

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        norm_target = "yaml" if target_ext == "yml" else target_ext
        norm_source = "yaml" if source_ext == "yml" else source_ext

        try:
            obj = self._parse(data, norm_source)
            out_bytes = self._serialize(obj, norm_target)
        except ConversionError:
            raise
        except Exception as e:
            raise ConversionError(f"Could not convert {source_ext} -> {target_ext}: {e}") from e

        mime = {"json": "application/json", "xml": "application/xml", "yaml": "application/yaml"}[norm_target]
        return ConversionResult(data=out_bytes, output_extension=target_ext, output_mime_type=mime)

    @staticmethod
    def _parse(data: bytes, ext: str):
        text = data.decode("utf-8")
        if ext == "json":
            return json.loads(text)
        if ext == "yaml":
            return yaml.safe_load(text)
        if ext == "xml":
            return xmltodict.parse(text)
        raise ConversionError(f"Unsupported data source format: {ext}")

    @staticmethod
    def _serialize(obj, ext: str) -> bytes:
        if ext == "json":
            return json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")
        if ext == "yaml":
            return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False).encode("utf-8")
        if ext == "xml":
            if not isinstance(obj, dict):
                obj = {"root": obj}
            return dicttoxml.dicttoxml(obj, custom_root="root", attr_type=False)
        raise ConversionError(f"Unsupported data target format: {ext}")


class CodeToHtmlConverter(BaseConverter):
    """Source code -> syntax-highlighted HTML, for preview/sharing."""

    category = "code"
    supported_conversions = {ext: {"html"} for ext in CODE_EXTS}

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        if target_ext != "html":
            raise ConversionError("Source code files can only be converted to HTML (syntax-highlighted preview)")
        text = data.decode("utf-8", errors="replace")
        try:
            lexer = get_lexer_for_filename(f"file.{source_ext}")
        except ClassNotFound:
            from pygments.lexers import TextLexer

            lexer = TextLexer()
        formatter = HtmlFormatter(full=True, linenos=True, style="monokai", title=f"file.{source_ext}")
        html = highlight(text, lexer, formatter)
        return ConversionResult(data=html.encode("utf-8"), output_extension="html", output_mime_type="text/html")
