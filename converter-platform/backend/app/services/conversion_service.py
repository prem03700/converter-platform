"""
Conversion orchestration: this is the "select engine -> convert -> store
output" part of the spec's conversion flow. Shared by the synchronous
eager-mode path and the Celery worker so behavior is identical either way.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.converters.base import ConversionError
from app.converters.registry import get_converter
from app.models.conversion import Conversion, ConversionStatus
from app.models.file import FileRecord
from app.storage import get_storage


def run_conversion(db: Session, conversion_id: str) -> None:
    """
    Executes a single conversion job end-to-end and updates its DB row.
    Safe to call from a Celery task or directly in-process (eager mode).
    """
    conversion = db.query(Conversion).filter(Conversion.id == conversion_id).first()
    if not conversion:
        return

    conversion.status = ConversionStatus.PROCESSING
    conversion.progress_percent = 10
    db.commit()

    try:
        source_file = db.query(FileRecord).filter(FileRecord.id == conversion.source_file_id).first()
        if not source_file:
            raise ConversionError("Source file no longer exists")

        storage = get_storage()
        input_bytes = storage.read(source_file.storage_key)
        conversion.progress_percent = 30
        db.commit()

        converter = get_converter(source_file.extension, conversion.target_format)
        result = converter.convert(input_bytes, source_file.extension, conversion.target_format)
        conversion.progress_percent = 80
        db.commit()

        output_key = f"users/{conversion.owner_id}/outputs/{uuid.uuid4().hex}.{result.output_extension}"
        storage.save(output_key, result.data)

        conversion.output_storage_key = output_key
        conversion.output_size_bytes = len(result.data)
        conversion.status = ConversionStatus.COMPLETED
        conversion.progress_percent = 100
        conversion.completed_at = datetime.now(timezone.utc)
        db.commit()

    except ConversionError as e:
        conversion.status = ConversionStatus.FAILED
        conversion.error_message = str(e)
        db.commit()
    except Exception as e:  # pragma: no cover - safety net for unexpected engine errors
        conversion.status = ConversionStatus.FAILED
        conversion.error_message = f"Unexpected error: {e}"
        db.commit()
