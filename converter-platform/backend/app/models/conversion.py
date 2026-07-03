import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class ConversionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Conversion(Base):
    __tablename__ = "conversions"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    source_file_id = Column(String, ForeignKey("files.id"), nullable=False)

    target_format = Column(String, nullable=False)
    ai_options = Column(Text, nullable=True)  # JSON-encoded optional AI post-processing flags

    status = Column(Enum(ConversionStatus), default=ConversionStatus.PENDING)
    progress_percent = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    output_storage_key = Column(String, nullable=True)
    output_size_bytes = Column(Integer, nullable=True)

    celery_task_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="conversions")
    source_file = relationship("FileRecord", back_populates="conversions")
