from typing import Any, List
from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
