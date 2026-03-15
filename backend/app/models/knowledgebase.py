from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class KnowledgeBaseArticle(Base, TimestampMixin):
    __tablename__ = "knowledge_base_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True)
    keywords = Column(Text, nullable=True)  # stored as comma-separated, e.g. "#cardwithdraw,#settlement"
    problem = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    solution = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    author = relationship("User")
