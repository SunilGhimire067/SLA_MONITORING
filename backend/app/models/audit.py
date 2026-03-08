from sqlalchemy import Column, BigInteger, Integer, String, Enum, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.core.constants import AuditAction


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False)
    action = Column(Enum(AuditAction), nullable=False, index=True)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), index=True)

    user = relationship("User")
