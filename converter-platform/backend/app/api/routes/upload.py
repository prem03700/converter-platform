from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.file import FileRecord
from app.models.user import User
from app.schemas.file import FileOut
from app.services.file_service import (
    delete_file,
    get_owned_file,
    read_file_bytes,
    save_uploaded_file,
)
from app.utils.validation import FileValidationError

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    raw = await file.read()
    try:
        record = save_uploaded_file(db, user, file.filename, raw)
    except FileValidationError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return record


@router.post("/upload-multiple", response_model=list[FileOut], status_code=status.HTTP_201_CREATED)
async def upload_multiple(files: list[UploadFile], user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = []
    for file in files:
        raw = await file.read()
        try:
            results.append(save_uploaded_file(db, user, file.filename, raw))
        except FileValidationError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{file.filename}: {e}")
    return results


@router.get("", response_model=list[FileOut])
def list_files(
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(FileRecord)
        .filter(FileRecord.owner_id == user.id)
        .order_by(FileRecord.created_at.desc())
        .offset(skip)
        .limit(min(limit, 200))
        .all()
    )


@router.get("/{file_id}/download")
def download_file(file_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_owned_file(db, user, file_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    data = read_file_bytes(record)
    return Response(
        content=data,
        media_type=record.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{record.original_filename}"'},
    )


@router.get("/{file_id}/preview")
def preview_file(file_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_owned_file(db, user, file_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    data = read_file_bytes(record)
    # Previewable types are streamed inline; everything else should be
    # downloaded instead of "previewed".
    previewable = {"image/png", "image/jpeg", "image/webp", "image/gif", "application/pdf", "text/plain"}
    if record.mime_type not in previewable:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "No inline preview available for this file type")
    return Response(content=data, media_type=record.mime_type)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_file(file_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not delete_file(db, user, file_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    return None
