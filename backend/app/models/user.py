from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True))

    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    avatar_url = Column(String(500))
    phone = Column(String(20))
    timezone = Column(String(50), default="UTC")
    last_login_at = Column(DateTime(timezone=True))

    role = relationship("Role", back_populates="users", lazy="joined")
    team_memberships = relationship("TeamMembership", back_populates="user")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
