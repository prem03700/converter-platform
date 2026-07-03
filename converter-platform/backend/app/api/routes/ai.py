from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.converters.base import ConversionError
from app.database import get_db
from app.models.user import User
from app.services import ai_service
from app.services.file_service import get_owned_file, read_file_bytes

router = APIRouter(prefix="/ai", tags=["ai"])


class TextTaskRequest(BaseModel):
    file_id: str
    target_language: str | None = None


@router.post("/ocr/image-to-text")
def ocr_image_to_text(file_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_owned_file(db, user, file_id)
    if not record or record.category != "image":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image file not found")
    text = ai_service.image_to_text(read_file_bytes(record))
    return {"file_id": file_id, "extracted_text": text}


@router.post("/ocr/searchable-pdf")
def ocr_searchable_pdf(file_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_owned_file(db, user, file_id)
    if not record or record.extension != "pdf":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "PDF file not found")
    try:
        pdf_bytes = ai_service.pdf_make_searchable(read_file_bytes(record))
    except ConversionError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="searchable.pdf"'},
    )


def _extract_text_for_ai(record, raw: bytes) -> str:
    if record.extension == "pdf":
        import fitz

        doc = fitz.open(stream=raw, filetype="pdf")
        return "\n\n".join(page.get_text() for page in doc)
    if record.extension in ("txt", "md", "html"):
        return raw.decode("utf-8", errors="replace")
    if record.extension == "docx":
        import io

        from docx import Document

        doc = Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs)
    raise HTTPException(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"AI text features aren't supported for .{record.extension} files yet. "
        "Supported: pdf, txt, md, html, docx.",
    )


@router.post("/summarize")
def summarize(payload: TextTaskRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _run_text_task(payload, "summarize", user, db)


@router.post("/tags")
def generate_tags(payload: TextTaskRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _run_text_task(payload, "tags", user, db)


@router.post("/keywords")
def generate_keywords(payload: TextTaskRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _run_text_task(payload, "keywords", user, db)


@router.post("/headings")
def extract_headings(payload: TextTaskRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _run_text_task(payload, "headings", user, db)


@router.post("/metadata")
def generate_metadata(payload: TextTaskRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _run_text_task(payload, "metadata", user, db)


@router.post("/translate")
def translate(payload: TextTaskRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _run_text_task(payload, "translate", user, db)


def _run_text_task(payload: TextTaskRequest, task: str, user: User, db: Session):
    record = get_owned_file(db, user, payload.file_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    text = _extract_text_for_ai(record, read_file_bytes(record))
    try:
        result = ai_service.llm_text_task(text, task, payload.target_language)
    except ConversionError as e:
        # Honest failure: no ANTHROPIC_API_KEY configured, or the model call failed.
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    return {"file_id": payload.file_id, "task": task, "result": result}
