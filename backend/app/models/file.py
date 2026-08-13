import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class FileRecord(Base):
    """An uploaded source file, before any conversion."""

    __tablename__ = "files"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)

    original_filename = Column(String, nullable=False)
    storage_key = Column(String, nullable=False)  # path/key in the storage backend
    mime_type = Column(String, nullable=False)
    extension = Column(String, nullable=False)
    category = Column(String, nullable=False)  # document | image | audio | video | archive | ebook | code
    size_bytes = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="files")
    conversions = relationship("Conversion", back_populates="source_file", cascade="all, delete-orphan")
