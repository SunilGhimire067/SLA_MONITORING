from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel


class TicketCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    priority: str = "P3"
    assignee_id: Optional[int] = None
    team_id: Optional[int] = None
    tags: Optional[List[str]] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    team_id: Optional[int] = None
    tags: Optional[List[str]] = None


class StatusTransition(BaseModel):
    status: str  # open, in_progress, blocked, resolved, closed


class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    project_id: int
    project_key: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    reporter_id: int
    reporter_name: Optional[str] = None
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    team_id: Optional[int] = None
    tags: Optional[Any] = None
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    sla: Optional[Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
