from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from .base import Base

class IdeaStatus(str, enum.Enum):
    NEW = "NEW"
    EVALUATING = "EVALUATING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(IdeaStatus), default=IdeaStatus.NEW, nullable=False)
    priority = Column(Integer, default=2, nullable=False)  # 1: High, 2: Medium, 3: Low
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
