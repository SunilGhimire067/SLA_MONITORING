from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str  # admin, manager, engineer, viewer
    phone: Optional[str] = None
    timezone: Optional[str] = "UTC"


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    timezone: Optional[str] = None
    permissions: list[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
