from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    key = Column(String(10), unique=True, nullable=False, index=True)
    description = Column(Text)
    lead_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True, index=True)

    lead = relationship("User", foreign_keys=[lead_id])
    tickets = relationship("Ticket", back_populates="project")
    sla_policies = relationship("SLAPolicy", back_populates="project")
