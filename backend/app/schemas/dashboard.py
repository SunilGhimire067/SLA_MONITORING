from typing import Optional
from pydantic import BaseModel


class OverviewKPI(BaseModel):
    total_tickets: int
    open: int
    in_progress: int
    blocked: int
    resolved: int
    closed: int
    sla_compliance_pct: Optional[float] = None
    avg_resolution_minutes: Optional[float] = None


class TicketsByStatusResponse(BaseModel):
    status: str
    count: int


class SLAComplianceResponse(BaseModel):
    priority: str
    total: int
    met: int
    breached: int
    compliance_pct: Optional[float] = None


class MTTRResponse(BaseModel):
    period: str
    avg_minutes: float
    ticket_count: int


class EngineerPerformance(BaseModel):
    engineer_id: int
    engineer_name: str
    tickets_resolved: int
    avg_resolution_minutes: Optional[float] = None
    sla_compliance_pct: Optional[float] = None


class TeamPerformance(BaseModel):
    team_id: int
    team_name: str
    tickets_resolved: int
    avg_resolution_minutes: Optional[float] = None
    sla_compliance_pct: Optional[float] = None
