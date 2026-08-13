from app.database import SessionLocal
from app.services.conversion_service import run_conversion
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.process_conversion", bind=True, max_retries=2)
def process_conversion(self, conversion_id: str) -> None:
    db = SessionLocal()
    try:
        run_conversion(db, conversion_id)
    finally:
        db.close()
