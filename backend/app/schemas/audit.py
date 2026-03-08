from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    entity_type: str
    entity_id: int
    action: str
    old_values: Optional[Any] = None
    new_values: Optional[Any] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuditExportRequest(BaseModel):
    report_type: str  # PCI, ISO, SOC2
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    format: str = "csv"
