"""
검색 관련 스키마
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class SearchResult(BaseModel):
    """검색 결과 항목"""
    slug: str
    title: str
    snippet: str = Field(..., description="검색어 주변 텍스트")
    relevance_score: float = Field(..., description="관련도 점수 (0.0 ~ 1.0)")
    matched_in: List[str] = Field(default=[], description="매칭된 위치 (title, content, tags)")
    category: Optional[str] = None
    tags: List[str] = Field(default=[])
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """검색 응답"""
    query: str
    total: int
    search_time_ms: Optional[int] = None
    results: List[SearchResult]
    facets: Optional[Dict[str, Dict[str, int]]] = None  # 카테고리, 태그별 문서 수


class SearchFilters(BaseModel):
    """검색 필터 옵션"""
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
