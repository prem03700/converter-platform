from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ConvertRequest(BaseModel):
    file_id: str
    target_format: str
    ai_cleanup: bool = False
    ai_options: Optional[dict] = None


class ConversionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_file_id: str
    target_format: str
    status: str
    progress_percent: int
    error_message: Optional[str]
    output_size_bytes: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
