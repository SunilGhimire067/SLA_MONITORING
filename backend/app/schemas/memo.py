from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MemoCreate(BaseModel):
    title: str
    content: str = ""


class MemoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class MemoResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    author_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
