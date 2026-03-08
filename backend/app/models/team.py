from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    lead_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)

    lead = relationship("User", foreign_keys=[lead_id])
    memberships = relationship("TeamMembership", back_populates="team", cascade="all, delete-orphan")


class TeamMembership(Base):
    __tablename__ = "team_memberships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True))

    team = relationship("Team", back_populates="memberships")
    user = relationship("User", back_populates="team_memberships")
