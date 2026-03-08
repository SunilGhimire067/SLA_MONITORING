from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    key: str = Field(..., max_length=10)
    description: Optional[str] = None
    lead_id: Optional[int] = None

    @property
    def normalized_key(self) -> str:
        return self.key.upper()

    def model_post_init(self, __context) -> None:
        object.__setattr__(self, "key", self.key.upper())


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    lead_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    key: str
    description: Optional[str] = None
    lead_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
