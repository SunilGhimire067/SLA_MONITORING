from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class KBArticleCreate(BaseModel):
    title: str
    category: str
    subcategory: Optional[str] = None
    keywords: Optional[str] = None
    problem: str
    description: Optional[str] = None
    solution: str


class KBArticleUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    keywords: Optional[str] = None
    problem: Optional[str] = None
    description: Optional[str] = None
    solution: Optional[str] = None


class KBArticleResponse(BaseModel):
    id: int
    title: str
    category: str
    subcategory: Optional[str] = None
    keywords: Optional[str] = None
    problem: str
    description: Optional[str] = None
    solution: str
    author_id: int
    author_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
