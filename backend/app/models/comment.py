from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    body = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User")
