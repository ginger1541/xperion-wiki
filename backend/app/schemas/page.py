"""
Page 스키마 - API 요청/응답 모델
"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Any
from datetime import datetime


class PageBase(BaseModel):
    """페이지 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = None
    author: Optional[str] = Field(None, max_length=100)
    status: str = Field("active", pattern="^(active|archived|draft)$")
    project_id: Optional[str] = Field(None, max_length=50, description="프로젝트(세계관) ID")


class PageCreate(PageBase):
    """페이지 생성 요청"""
    slug: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = []


class PageUpdate(PageBase):
    """페이지 수정 요청"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    expected_sha: Optional[str] = Field(None, description="동시성 제어를 위한 현재 SHA")
    force: bool = Field(False, description="충돌 무시하고 강제 저장")


class PageResponse(PageBase):
    """페이지 응답 (목록용)"""
    id: int
    slug: str
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    view_count: int
    github_sha: Optional[str] = None

    @field_serializer('tags')
    def serialize_tags(self, tags: Any, _info) -> List[str]:
        """Tag 객체를 문자열 리스트로 변환"""
        if isinstance(tags, list):
            return [tag.name if hasattr(tag, 'name') else str(tag) for tag in tags]
        return []

    class Config:
        from_attributes = True  # SQLAlchemy 모델을 Pydantic으로 변환 허용


class PageDetail(PageResponse):
    """페이지 상세 응답"""
    content_html: Optional[str] = None
    github_url: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    related_pages: Optional[List[PageResponse]] = []


class PageListResponse(BaseModel):
    """페이지 목록 응답"""
    total: int
    pages: List[PageResponse]
