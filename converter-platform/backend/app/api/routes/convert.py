from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.converters.registry import list_supported_targets
from app.database import get_db
from app.models.conversion import Conversion, ConversionStatus
from app.models.user import User
from app.schemas.conversion import ConversionOut, ConvertRequest
from app.services.conversion_service import run_conversion
from app.services.file_service import get_owned_file
from app.storage import get_storage

router = APIRouter(prefix="/convert", tags=["convert"])


@router.get("/supported-targets/{file_id}")
def supported_targets(file_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_owned_file(db, user, file_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
    return {"source_extension": record.extension, "targets": sorted(list_supported_targets(record.extension))}


@router.post("", response_model=ConversionOut, status_code=status.HTTP_202_ACCEPTED)
def convert_file(payload: ConvertRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    source_file = get_owned_file(db, user, payload.file_id)
    if not source_file:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Source file not found")

    targets = list_supported_targets(source_file.extension)
    target_format = payload.target_format.lower().lstrip(".")
    if target_format not in targets:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Cannot convert .{source_file.extension} to .{target_format}. "
            f"Supported targets: {sorted(targets)}",
        )

    conversion = Conversion(
        owner_id=user.id,
        source_file_id=source_file.id,
        target_format=target_format,
        status=ConversionStatus.PENDING,
    )
    db.add(conversion)
    db.commit()
    db.refresh(conversion)

    if settings.RUN_TASKS_EAGERLY:
        # Local-dev mode: no Celery/Redis needed, runs inline.
        run_conversion(db, conversion.id)
        db.refresh(conversion)
    else:
        from app.workers.tasks import process_conversion

        task = process_conversion.delay(conversion.id)
        conversion.celery_task_id = task.id
        db.commit()
        db.refresh(conversion)

    return conversion


@router.get("/{conversion_id}/status", response_model=ConversionOut)
def conversion_status(conversion_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversion = (
        db.query(Conversion)
        .filter(Conversion.id == conversion_id, Conversion.owner_id == user.id)
        .first()
    )
    if not conversion:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversion not found")
    return conversion


@router.post("/{conversion_id}/cancel", response_model=ConversionOut)
def cancel_conversion(conversion_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversion = (
        db.query(Conversion)
        .filter(Conversion.id == conversion_id, Conversion.owner_id == user.id)
        .first()
    )
    if not conversion:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversion not found")
    if conversion.status not in (ConversionStatus.PENDING, ConversionStatus.PROCESSING):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only pending/processing conversions can be cancelled")

    if conversion.celery_task_id:
        from app.workers.celery_app import celery_app

        celery_app.control.revoke(conversion.celery_task_id, terminate=True)

    conversion.status = ConversionStatus.CANCELLED
    db.commit()
    db.refresh(conversion)
    return conversion


@router.get("/{conversion_id}/download")
def download_converted(conversion_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversion = (
        db.query(Conversion)
        .filter(Conversion.id == conversion_id, Conversion.owner_id == user.id)
        .first()
    )
    if not conversion:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversion not found")
    if conversion.status != ConversionStatus.COMPLETED or not conversion.output_storage_key:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Conversion is not complete (status: {conversion.status})")

    data = get_storage().read(conversion.output_storage_key)
    filename = f"converted.{conversion.target_format}"
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
