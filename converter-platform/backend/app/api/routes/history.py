from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.conversion import Conversion, ConversionStatus
from app.models.file import FileRecord
from app.models.user import User
from app.schemas.conversion import ConversionOut

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[ConversionOut])
def get_history(
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Conversion)
        .filter(Conversion.owner_id == user.id)
        .order_by(Conversion.created_at.desc())
        .offset(skip)
        .limit(min(limit, 200))
        .all()
    )


@router.get("/stats")
def get_dashboard_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_files = db.query(func.count(FileRecord.id)).filter(FileRecord.owner_id == user.id).scalar() or 0
    total_storage = db.query(func.coalesce(func.sum(FileRecord.size_bytes), 0)).filter(
        FileRecord.owner_id == user.id
    ).scalar() or 0
    total_conversions = db.query(func.count(Conversion.id)).filter(Conversion.owner_id == user.id).scalar() or 0
    completed = db.query(func.count(Conversion.id)).filter(
        Conversion.owner_id == user.id, Conversion.status == ConversionStatus.COMPLETED
    ).scalar() or 0
    failed = db.query(func.count(Conversion.id)).filter(
        Conversion.owner_id == user.id, Conversion.status == ConversionStatus.FAILED
    ).scalar() or 0

    target_formats = [
        row[0] for row in db.query(Conversion.target_format).filter(Conversion.owner_id == user.id).all()
    ]
    favorite_formats = [fmt for fmt, _ in Counter(target_formats).most_common(5)]

    recent = (
        db.query(Conversion)
        .filter(Conversion.owner_id == user.id)
        .order_by(Conversion.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_files": total_files,
        "total_storage_bytes": int(total_storage),
        "total_conversions": total_conversions,
        "completed_conversions": completed,
        "failed_conversions": failed,
        "favorite_formats": favorite_formats,
        "recent_activity": [ConversionOut.model_validate(c).model_dump(mode="json") for c in recent],
    }
