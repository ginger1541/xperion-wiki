"""
Project Schemas - 프로젝트 요청/응답 모델
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProjectBase(BaseModel):
    """프로젝트 기본 스키마"""
    id: str
    title: str
    description: Optional[str] = None
    color: str = "bg-blue-500"


class ProjectCreate(ProjectBase):
    """프로젝트 생성 스키마"""
    pass


class ProjectUpdate(BaseModel):
    """프로젝트 업데이트 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class ProjectResponse(ProjectBase):
    """프로젝트 응답 스키마"""
    created_at: datetime
    updated_at: datetime
    doc_count: int

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """프로젝트 목록 응답"""
    total: int
    projects: list[ProjectResponse]
