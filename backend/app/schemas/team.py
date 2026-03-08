from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    lead_id: Optional[int] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    lead_id: Optional[int] = None


class TeamMemberAdd(BaseModel):
    user_id: int


class TeamMemberResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    joined_at: Optional[datetime] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    lead_id: Optional[int] = None
    members: List[TeamMemberResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}
