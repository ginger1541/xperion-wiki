"""
Project Model - 세계관/프로젝트 관리
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Project(Base):
    """프로젝트(세계관) 모델"""

    __tablename__ = "projects"

    # Primary Key
    id = Column(String(50), primary_key=True)  # dagosian, estua, citron

    # Basic Info
    title = Column(String(200), nullable=False)  # 다고시안 듀얼단
    description = Column(Text)  # 세계관 설명

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Stats
    doc_count = Column(Integer, default=0)  # 문서 개수 (캐시)

    # Color for UI
    color = Column(String(50), default="bg-blue-500")  # Tailwind color class

    # Relationships
    pages = relationship("Page", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title})>"
