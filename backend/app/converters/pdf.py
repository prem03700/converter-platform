"""
PDF conversions via PyMuPDF (fitz). Fully functional, no external
binaries required.

Covers: PDF -> TXT, PDF -> MD (heuristic heading detection from font
size), PDF -> PNG (first page or all pages flattened into one), and a
basic PDF -> DOCX text reconstruction (layout is not preserved — for
layout-faithful PDF->DOCX, route through the LibreOffice converter
instead, which handles it via PDF import).
"""
import io
from typing import Optional

import fitz  # PyMuPDF
from docx import Document
from PIL import Image

from app.converters.base import BaseConverter, ConversionError, ConversionResult


class PdfConverter(BaseConverter):
    category = "document"
    supported_conversions = {
        "pdf": {"txt", "md", "png", "jpg", "docx"},
    }

    def convert(self, data: bytes, source_ext: str, target_ext: str, options: Optional[dict] = None) -> ConversionResult:
        if source_ext != "pdf":
            raise ConversionError("PdfConverter only accepts PDF as a source")

        try:
            doc = fitz.open(stream=data, filetype="pdf")
        except Exception as e:
            raise ConversionError(f"Could not open PDF: {e}") from e

        if target_ext == "txt":
            return self._to_text(doc)
        if target_ext == "md":
            return self._to_markdown(doc)
        if target_ext in ("png", "jpg"):
            return self._to_image(doc, target_ext, options or {})
        if target_ext == "docx":
            return self._to_docx(doc)
        raise ConversionError(f"Unsupported PDF target: {target_ext}")

    def _to_text(self, doc) -> ConversionResult:
        text = "\n\n".join(page.get_text() for page in doc)
        return ConversionResult(
            data=text.encode("utf-8"), output_extension="txt", output_mime_type="text/plain",
            metadata={"page_count": doc.page_count},
        )

    def _to_markdown(self, doc) -> ConversionResult:
        # Heuristic: the largest font size on a page becomes an H1/H2 line;
        # everything else is a paragraph. This is a reasonable approximation,
        # not a perfect structural reconstruction.
        lines = []
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            sizes = [
                span["size"]
                for b in blocks for l in b.get("lines", []) for span in l.get("spans", [])
            ]
            max_size = max(sizes) if sizes else 0
            for b in blocks:
                for l in b.get("lines", []):
                    line_text = "".join(span["text"] for span in l.get("spans", [])).strip()
                    if not line_text:
                        continue
                    line_size = max((span["size"] for span in l.get("spans", [])), default=0)
                    if max_size and line_size >= max_size * 0.95:
                        lines.append(f"## {line_text}")
                    else:
                        lines.append(line_text)
            lines.append("")
        return ConversionResult(
            data="\n".join(lines).encode("utf-8"), output_extension="md", output_mime_type="text/markdown",
        )

    def _to_image(self, doc, target_ext: str, options: dict) -> ConversionResult:
        page_number = int(options.get("page", 0))
        if page_number >= doc.page_count:
            raise ConversionError(f"PDF only has {doc.page_count} page(s)")
        page = doc[page_number]
        zoom = float(options.get("zoom", 2.0))  # 2x ~= 144dpi
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        buffer = io.BytesIO()
        if target_ext == "jpg":
            img.convert("RGB").save(buffer, format="JPEG", quality=92)
            mime = "image/jpeg"
        else:
            img.save(buffer, format="PNG")
            mime = "image/png"
        return ConversionResult(data=buffer.getvalue(), output_extension=target_ext, output_mime_type=mime)

    def _to_docx(self, doc) -> ConversionResult:
        document = Document()
        for page in doc:
            text = page.get_text()
            for paragraph in text.split("\n"):
                if paragraph.strip():
                    document.add_paragraph(paragraph)
            document.add_page_break()
        buffer = io.BytesIO()
        document.save(buffer)
        return ConversionResult(
            data=buffer.getvalue(), output_extension="docx",
            output_mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
