from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    ticket_id: Optional[int] = None
    type: str
    channel: str
    title: str
    message: Optional[str] = None
    is_read: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EscalationRuleCreate(BaseModel):
    name: str
    project_id: Optional[int] = None
    priority: Optional[str] = None
    trigger_type: str
    trigger_threshold_minutes: Optional[int] = 0
    escalate_to_user_id: Optional[int] = None
    escalate_to_team_id: Optional[int] = None
    notify_channels: Optional[List[str]] = None


class EscalationRuleUpdate(BaseModel):
    name: Optional[str] = None
    project_id: Optional[int] = None
    priority: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_threshold_minutes: Optional[int] = None
    escalate_to_user_id: Optional[int] = None
    escalate_to_team_id: Optional[int] = None
    notify_channels: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EscalationRuleResponse(BaseModel):
    id: int
    name: str
    project_id: Optional[int] = None
    priority: Optional[str] = None
    trigger_type: str
    trigger_threshold_minutes: int = 0
    escalate_to_user_id: Optional[int] = None
    escalate_to_team_id: Optional[int] = None
    notify_channels: Optional[List[str]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
