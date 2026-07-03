from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    mime_type: str
    extension: str
    category: str
    size_bytes: int
    created_at: datetime
