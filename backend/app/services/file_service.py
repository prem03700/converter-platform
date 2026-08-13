from sqlalchemy.orm import Session

from app.models.file import FileRecord
from app.models.user import User
from app.storage import get_storage
from app.utils.validation import FileValidationError, validate_upload


def save_uploaded_file(db: Session, owner: User, filename: str, raw_bytes: bytes) -> FileRecord:
    meta = validate_upload(filename, len(raw_bytes), raw_bytes)

    file_id = __import__("uuid").uuid4().hex
    storage_key = f"users/{owner.id}/uploads/{file_id}.{meta['extension']}"

    storage = get_storage()
    storage.save(storage_key, raw_bytes)

    record = FileRecord(
        owner_id=owner.id,
        original_filename=meta["clean_filename"],
        storage_key=storage_key,
        mime_type=meta["mime_type"],
        extension=meta["extension"],
        category=meta["category"],
        size_bytes=len(raw_bytes),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_owned_file(db: Session, owner: User, file_id: str) -> FileRecord | None:
    return (
        db.query(FileRecord)
        .filter(FileRecord.id == file_id, FileRecord.owner_id == owner.id)
        .first()
    )


def delete_file(db: Session, owner: User, file_id: str) -> bool:
    record = get_owned_file(db, owner, file_id)
    if not record:
        return False
    storage = get_storage()
    try:
        storage.delete(record.storage_key)
    except FileValidationError:
        pass
    db.delete(record)
    db.commit()
    return True


def read_file_bytes(record: FileRecord) -> bytes:
    return get_storage().read(record.storage_key)
