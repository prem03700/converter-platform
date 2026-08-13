import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    storage_used_bytes = Column(String, default="0")  # stored as string to avoid bigint driver issues on sqlite
    plan = Column(String, default="free")  # free | pro | enterprise (future billing)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    files = relationship("FileRecord", back_populates="owner", cascade="all, delete-orphan")
    conversions = relationship("Conversion", back_populates="owner", cascade="all, delete-orphan")
