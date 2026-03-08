from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SLAPolicyCreate(BaseModel):
    name: str
    priority: str  # P1, P2, P3, P4
    project_id: Optional[int] = None
    response_time_minutes: int
    resolution_time_minutes: int
    is_default: Optional[bool] = False


class SLAPolicyUpdate(BaseModel):
    name: Optional[str] = None
    response_time_minutes: Optional[int] = None
    resolution_time_minutes: Optional[int] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class SLAPolicyResponse(BaseModel):
    id: int
    name: str
    priority: str
    project_id: Optional[int] = None
    response_time_minutes: int
    resolution_time_minutes: int
    is_default: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SLARecordResponse(BaseModel):
    id: int
    ticket_id: int
    ticket_number: Optional[str] = None
    sla_policy_id: int
    response_deadline: Optional[datetime] = None
    resolution_deadline: Optional[datetime] = None
    response_met: Optional[bool] = None
    resolution_met: Optional[bool] = None
    actual_response_minutes: Optional[int] = None
    actual_resolution_minutes: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
