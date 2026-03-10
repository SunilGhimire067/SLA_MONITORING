from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Memo(Base, TimestampMixin):
    __tablename__ = "memos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False, default="")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    author = relationship("User")
