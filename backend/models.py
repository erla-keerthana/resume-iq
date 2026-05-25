import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)
    provider = Column(String, default="local")
    created_at = Column(DateTime, default=_utcnow)

    analyses = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    job_description = Column(Text, nullable=False)
    workflow_type = Column(String, default="analysis")
    ats_score = Column(Integer, default=0)
    match_score = Column(Integer, default=0)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="analyses")
