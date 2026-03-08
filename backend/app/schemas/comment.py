from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CommentCreate(BaseModel):
    body: str
    is_internal: bool = False


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    author_name: Optional[str] = None
    body: str
    is_internal: bool
    created_at: datetime

    model_config = {"from_attributes": True}
