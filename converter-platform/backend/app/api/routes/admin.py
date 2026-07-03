import shutil
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.config import settings
from app.database import get_db
from app.models.conversion import Conversion, ConversionStatus
from app.models.file import FileRecord
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(skip: int = 0, limit: int = 100, _admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).offset(skip).limit(min(limit, 500)).all()


@router.patch("/users/{user_id}/disable", response_model=UserOut)
def disable_user(user_id: str, _admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    target.is_active = False
    db.commit()
    db.refresh(target)
    return target


@router.patch("/users/{user_id}/enable", response_model=UserOut)
def enable_user(user_id: str, _admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    target.is_active = True
    db.commit()
    db.refresh(target)
    return target


@router.get("/statistics")
def platform_statistics(_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {
        "total_users": db.query(func.count(User.id)).scalar() or 0,
        "total_files": db.query(func.count(FileRecord.id)).scalar() or 0,
        "total_storage_bytes": int(db.query(func.coalesce(func.sum(FileRecord.size_bytes), 0)).scalar() or 0),
        "total_conversions": db.query(func.count(Conversion.id)).scalar() or 0,
        "conversions_by_status": {
            status_value.value: db.query(func.count(Conversion.id))
            .filter(Conversion.status == status_value)
            .scalar()
            or 0
            for status_value in ConversionStatus
        },
    }


@router.get("/system-health")
def system_health(_admin: User = Depends(get_current_admin)):
    disk = shutil.disk_usage(settings.LOCAL_STORAGE_PATH if settings.STORAGE_BACKEND == "local" else "/")
    redis_ok = True
    redis_error = None
    try:
        import redis as redis_lib

        client = redis_lib.from_url(settings.REDIS_URL, socket_connect_timeout=1)
        client.ping()
    except Exception as e:
        redis_ok = False
        redis_error = str(e)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "ok",  # if this handler is running, the DB dependency chain already succeeded
        "redis": "ok" if redis_ok else f"unreachable: {redis_error}",
        "task_mode": "eager (synchronous)" if settings.RUN_TASKS_EAGERLY else "celery (background)",
        "storage_backend": settings.STORAGE_BACKEND,
        "disk_total_gb": round(disk.total / 1e9, 2),
        "disk_used_gb": round(disk.used / 1e9, 2),
        "disk_free_gb": round(disk.free / 1e9, 2),
    }


@router.get("/logs")
def get_logs(lines: int = 200, _admin: User = Depends(get_current_admin)):
    # Placeholder: wire this up to your actual log aggregator (e.g. Loki,
    # CloudWatch, or a structured log table) in production. Returning an
    # explicit "not configured" response rather than fabricating log data.
    return {
        "message": "Log aggregation is not configured in this build. "
        "Wire this endpoint to your logging backend (e.g. CloudWatch, Loki, ELK).",
        "lines_requested": lines,
    }
