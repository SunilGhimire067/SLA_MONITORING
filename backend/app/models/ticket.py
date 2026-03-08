from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin
from app.core.constants import TicketPriority, TicketStatus


class Ticket(Base, TimestampMixin):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(Enum(TicketPriority), nullable=False, default=TicketPriority.P3)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"))
    tags = Column(JSON)
    first_response_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))

    project = relationship("Project", back_populates="tickets")
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    team = relationship("Team")
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    sla_record = relationship("SLARecord", back_populates="ticket", uselist=False)
