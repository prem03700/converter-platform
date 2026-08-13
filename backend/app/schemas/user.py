from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str | None
    is_admin: bool
    plan: str
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = None
