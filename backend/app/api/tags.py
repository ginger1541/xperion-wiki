"""
Tags API - 태그 관리
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.models.tag import Tag
from app.models.page import Page
from app.schemas.page import PageResponse, PageListResponse

router = APIRouter()


class TagResponse(BaseModel):
    """태그 응답"""
    id: int
    name: str
    display_name: str | None = None
    color: str | None = None
    usage_count: int = 0

    class Config:
        from_attributes = True


@router.get("", response_model=List[TagResponse])
async def get_tags(
    db: AsyncSession = Depends(get_db)
):
    """
    전체 태그 목록 조회 (사용 빈도순)
    """

    query = select(Tag).order_by(Tag.usage_count.desc())
    result = await db.execute(query)
    tags = result.scalars().all()

    return [TagResponse.model_validate(tag) for tag in tags]


@router.get("/{tag_name}/pages", response_model=PageListResponse)
async def get_pages_by_tag(
    tag_name: str,
    status: str = Query("active", description="문서 상태"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 문서 수"),
    db: AsyncSession = Depends(get_db)
):
    """
    특정 태그의 문서 목록 조회

    - **tag_name**: 태그 이름 (예: 종족/엘프)
    - **status**: active, archived, draft
    - **page**: 페이지 번호
    - **limit**: 페이지당 문서 수
    """

    # 태그 조회
    tag_query = select(Tag).where(Tag.name == tag_name)
    tag_result = await db.execute(tag_query)
    tag = tag_result.scalar_one_or_none()

    if not tag:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "TAG_NOT_FOUND",
                "message": f"태그를 찾을 수 없습니다: {tag_name}"
            }
        )

    # 해당 태그를 가진 문서 조회
    # Tag의 pages relationship을 사용하되, 필터링과 페이지네이션 적용
    query = (
        select(Page)
        .join(Page.tags)
        .where(Tag.id == tag.id)
        .where(Page.status == status)
        .order_by(Page.updated_at.desc())
    )

    # 페이지네이션
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    pages = result.scalars().all()

    # 전체 개수 조회
    count_query = (
        select(func.count(Page.id))
        .join(Page.tags)
        .where(Tag.id == tag.id)
        .where(Page.status == status)
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    return PageListResponse(
        total=total,
        pages=[PageResponse.model_validate(p) for p in pages]
    )
