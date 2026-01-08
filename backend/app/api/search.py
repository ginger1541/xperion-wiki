"""
검색 API - PostgreSQL Trigram 기반
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, or_
from typing import Optional, List
import time
import structlog

from app.db.database import get_db
from app.models.page import Page
from app.schemas.search import SearchResponse, SearchResult

logger = structlog.get_logger()

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search_pages(
    q: str = Query(..., min_length=1, description="검색어"),
    project_id: Optional[str] = Query(None, description="프로젝트(세계관) 필터"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(20, ge=1, le=100, description="결과 수"),
    db: AsyncSession = Depends(get_db)
):
    """
    문서 검색 (PostgreSQL Trigram 기반)

    - **q**: 검색어 (필수)
    - **project_id**: 프로젝트 필터 (통합 검색은 생략)
    - **category**: 카테고리 필터
    - **limit**: 최대 결과 수

    ## 검색 방식
    - 제목 가중치: 3.0
    - 본문 가중치: 1.0
    - 한글 형태소 변화 대응 (Trigram)
    """

    start_time = time.time()

    # 짧은 검색어 (2글자 이하)는 ILIKE 사용
    if len(q) <= 2:
        results = await _search_short_query(db, q, project_id, category, limit)
    else:
        results = await _search_trigram(db, q, project_id, category, limit)

    search_time_ms = int((time.time() - start_time) * 1000)

    logger.info("search_completed", query=q, results=len(results), time_ms=search_time_ms)

    return SearchResponse(
        query=q,
        total=len(results),
        search_time_ms=search_time_ms,
        results=results
    )


async def _search_short_query(
    db: AsyncSession,
    query: str,
    project_id: Optional[str],
    category: Optional[str],
    limit: int
) -> List[SearchResult]:
    """짧은 검색어 처리 (ILIKE 사용)"""

    # ILIKE 검색
    filters = [
        or_(
            Page.title.ilike(f"%{query}%"),
            Page.content.ilike(f"%{query}%")
        )
    ]

    if project_id:
        filters.append(Page.project_id == project_id)

    if category:
        filters.append(Page.category == category)

    sql_query = select(Page).where(*filters).limit(limit)

    result = await db.execute(sql_query)
    pages = result.scalars().all()

    search_results = []
    for page in pages:
        # 매칭 위치 확인
        matched_in = []
        if query.lower() in page.title.lower():
            matched_in.append("title")
        if query.lower() in page.content.lower():
            matched_in.append("content")

        # 간단한 관련도 점수 (제목 매칭이 더 높음)
        score = 0.5
        if "title" in matched_in:
            score = 0.9

        # 태그 추출 (relationship으로 자동 로드됨)
        tag_names = [tag.name for tag in page.tags] if page.tags else []

        search_results.append(SearchResult(
            slug=page.slug,
            title=page.title,
            snippet=_generate_snippet(page.content, query),
            relevance_score=score,
            matched_in=matched_in,
            category=page.category,
            tags=tag_names,
            updated_at=page.updated_at
        ))

    return search_results


async def _search_trigram(
    db: AsyncSession,
    query: str,
    project_id: Optional[str],
    category: Optional[str],
    limit: int
) -> List[SearchResult]:
    """Trigram 기반 검색 (3글자 이상)"""

    # Trigram 유사도 계산
    # similarity(column, query) * weight
    similarity_expr = text(f"""
        (similarity(title, :query) * 3.0) +
        (similarity(content, :query) * 1.0)
    """)

    # WHERE 조건 구축
    where_parts = ["(title % :query OR content % :query)", "status = 'active'"]
    params = {"query": query, "limit": limit}

    if project_id:
        where_parts.append("project_id = :project_id")
        params["project_id"] = project_id

    if category:
        where_parts.append("category = :category")
        params["category"] = category

    where_clause = " AND ".join(where_parts)

    sql_query = text(f"""
        SELECT
            id, slug, title, content, category, updated_at,
            ({similarity_expr.text}) as relevance_score,
            similarity(title, :query) as title_sim,
            similarity(content, :query) as content_sim
        FROM pages
        WHERE {where_clause}
        ORDER BY relevance_score DESC
        LIMIT :limit
    """)

    result = await db.execute(sql_query, params)

    rows = result.fetchall()

    # 검색 결과가 있으면 태그 정보를 가져오기 위해 Page 객체 조회
    page_ids = [row.id for row in rows]

    # Page 객체들을 조회 (tags relationship 포함)
    if page_ids:
        pages_query = select(Page).where(Page.id.in_(page_ids))
        pages_result = await db.execute(pages_query)
        pages = {p.id: p for p in pages_result.scalars().all()}
    else:
        pages = {}

    search_results = []
    for row in rows:
        # 매칭 위치 확인
        matched_in = []
        if row.title_sim > 0.2:
            matched_in.append("title")
        if row.content_sim > 0.2:
            matched_in.append("content")

        # 태그 추출
        page = pages.get(row.id)
        tag_names = [tag.name for tag in page.tags] if page and page.tags else []

        search_results.append(SearchResult(
            slug=row.slug,
            title=row.title,
            snippet=_generate_snippet(row.content, query),
            relevance_score=round(row.relevance_score, 2),
            matched_in=matched_in,
            category=row.category,
            tags=tag_names,
            updated_at=row.updated_at
        ))

    return search_results


def _generate_snippet(content: str, query: str, context_length: int = 150) -> str:
    """
    검색어 주변 텍스트 추출 (snippet)

    Args:
        content: 전체 본문
        query: 검색어
        context_length: snippet 길이

    Returns:
        "...검색어 주변 텍스트..."
    """
    # 대소문자 구분 없이 검색
    lower_content = content.lower()
    lower_query = query.lower()

    pos = lower_content.find(lower_query)

    if pos == -1:
        # 검색어가 없으면 앞부분만 반환
        return content[:context_length] + ("..." if len(content) > context_length else "")

    # 검색어 중심으로 앞뒤 추출
    start = max(0, pos - context_length // 2)
    end = min(len(content), pos + len(query) + context_length // 2)

    snippet = content[start:end]

    # 앞뒤에 ... 추가
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."

    return snippet.strip()
