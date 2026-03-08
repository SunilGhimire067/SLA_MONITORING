from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin
from app.core.constants import (
    NotificationType, NotificationChannel, TriggerType, TicketPriority
)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="SET NULL"))
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False, default=NotificationChannel.IN_APP)
    title = Column(String(300), nullable=False)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))

    user = relationship("User")
    ticket = relationship("Ticket")


class EscalationRule(Base, TimestampMixin):
    __tablename__ = "escalation_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    priority = Column(Enum(TicketPriority))
    trigger_type = Column(Enum(TriggerType), nullable=False)
    trigger_threshold_minutes = Column(Integer, default=0)
    escalate_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    escalate_to_team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"))
    notify_channels = Column(JSON)  # ["email", "teams"]
    is_active = Column(Boolean, default=True, index=True)

    project = relationship("Project")
    escalate_to_user = relationship("User")
    escalate_to_team = relationship("Team")
