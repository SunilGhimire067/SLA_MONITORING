from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin
from app.core.constants import TicketPriority


class SLAPolicy(Base, TimestampMixin):
    __tablename__ = "sla_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    priority = Column(Enum(TicketPriority), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    response_time_minutes = Column(Integer, nullable=False)
    resolution_time_minutes = Column(Integer, nullable=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    project = relationship("Project", back_populates="sla_policies")
    records = relationship("SLARecord", back_populates="sla_policy")


class SLARecord(Base, TimestampMixin):
    __tablename__ = "sla_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, unique=True)
    sla_policy_id = Column(Integer, ForeignKey("sla_policies.id"), nullable=False)
    response_deadline = Column(DateTime(timezone=True), nullable=False)
    resolution_deadline = Column(DateTime(timezone=True), nullable=False)
    response_met = Column(Boolean)  # None = pending
    resolution_met = Column(Boolean)  # None = pending
    actual_response_minutes = Column(Integer)
    actual_resolution_minutes = Column(Integer)
    response_breached_at = Column(DateTime(timezone=True))
    resolution_breached_at = Column(DateTime(timezone=True))

    ticket = relationship("Ticket", back_populates="sla_record")
    sla_policy = relationship("SLAPolicy", back_populates="records")
