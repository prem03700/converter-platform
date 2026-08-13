"""
AI-powered features, kept deliberately separate from the deterministic
format converters above.

OCR (image->text, scanned PDF -> searchable PDF) runs fully locally via
Tesseract and needs no API key.

Everything else the spec calls "AI Features" (summarize, extract
headings/tags/keywords, translate, generate metadata) is genuinely an
LLM call. Rather than faking these with placeholder text, this module
calls the Anthropic API when ANTHROPIC_API_KEY is configured, and raises
a clear, honest error otherwise — it never silently returns made-up
"AI" output.
"""
import io
import os
from typing import Optional

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from app.converters.base import ConversionError


def image_to_text(image_bytes: bytes, lang: str = "eng") -> str:
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image, lang=lang)


def pdf_make_searchable(pdf_bytes: bytes, lang: str = "eng") -> bytes:
    """
    Adds an invisible OCR text layer to a scanned (image-only) PDF so it
    becomes searchable/selectable, while keeping the original page images
    untouched.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        ocr_data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)

        scale_x = page.rect.width / pix.width
        scale_y = page.rect.height / pix.height

        for i, word in enumerate(ocr_data["text"]):
            if not word.strip():
                continue
            x, y, w, h = (
                ocr_data["left"][i], ocr_data["top"][i],
                ocr_data["width"][i], ocr_data["height"][i],
            )
            rect = fitz.Rect(
                x * scale_x, y * scale_y, (x + w) * scale_x, (y + h) * scale_y,
            )
            # render_mode=3 -> invisible text, sits exactly over the scanned word
            page.insert_textbox(rect, word, fontsize=rect.height * 0.8, render_mode=3)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _get_anthropic_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ConversionError(
            "This AI feature requires ANTHROPIC_API_KEY to be configured on the "
            "server. It has not been set, so no AI processing was performed."
        )
    import anthropic

    return anthropic.Anthropic(api_key=api_key)


def llm_text_task(text: str, task: str, target_language: Optional[str] = None) -> str:
    """
    task: one of 'summarize' | 'tags' | 'keywords' | 'headings' | 'translate' | 'metadata'
    Truncates very long input — for production use, chunk + map-reduce
    long documents instead of truncating.
    """
    client = _get_anthropic_client()
    truncated = text[:20000]

    prompts = {
        "summarize": "Summarize the following document in 3-5 sentences.",
        "tags": "Generate 5-10 short topical tags for the following document, as a comma-separated list.",
        "keywords": "Extract the 10 most important keywords from the following document, as a comma-separated list.",
        "headings": "Extract the document's heading/section structure as a markdown outline.",
        "metadata": "Generate a JSON object with title, author (if inferable), summary, and topics for this document.",
        "translate": f"Translate the following document into {target_language or 'English'}, preserving structure.",
    }
    instruction = prompts.get(task)
    if not instruction:
        raise ConversionError(f"Unknown AI task: {task}")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": f"{instruction}\n\n---\n\n{truncated}"}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
