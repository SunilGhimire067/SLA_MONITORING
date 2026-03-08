from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255))
    category = Column(String(50))
    created_at = Column(DateTime(timezone=True))

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("role_id", "permission_id"),)
