"""
Pages API - 위키 문서 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime
from github import GithubException
import structlog

from app.db.database import get_db
from app.models.page import Page
from app.models.tag import Tag
from app.schemas.page import (
    PageResponse,
    PageListResponse,
    PageDetail,
    PageCreate,
    PageUpdate
)
from app.services.github_client import github_client
from app.services.markdown_utils import create_markdown, extract_metadata_from_page

logger = structlog.get_logger()

router = APIRouter()


async def sync_tags(db: AsyncSession, page: Page, tag_names: list[str]):
    """
    문서의 태그를 동기화합니다.

    Args:
        db: 데이터베이스 세션
        page: Page 객체
        tag_names: 태그 이름 리스트 (예: ["종족/엘프", "클래스/팔라딘"])
    """
    if not tag_names:
        page.tags = []
        return

    # 기존 태그들을 조회하거나 새로 생성
    tags = []
    for tag_name in tag_names:
        # 태그 조회
        query = select(Tag).where(Tag.name == tag_name)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            # 태그 생성
            tag = Tag(
                name=tag_name,
                display_name=tag_name.split('/')[-1],  # "종족/엘프" → "엘프"
                usage_count=0
            )
            db.add(tag)
            logger.info("tag_created", tag_name=tag_name)

        tags.append(tag)

    # 기존 태그의 usage_count 감소 (새 페이지가 아닌 경우만)
    if page.id:  # 페이지가 이미 DB에 존재하는 경우
        # 먼저 기존 태그들을 명시적으로 로드
        await db.refresh(page, ["tags"])
        for old_tag in page.tags:
            old_tag.usage_count = max(0, old_tag.usage_count - 1)

    # 새 태그들의 usage_count 증가
    for tag in tags:
        tag.usage_count += 1

    # 페이지에 태그 할당
    page.tags = tags
    await db.flush()

    logger.info("tags_synced", page_slug=page.slug, tags=tag_names)


@router.get("", response_model=PageListResponse)
async def get_pages(
    project_id: Optional[str] = Query(None, description="프로젝트(세계관) 필터"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    status: str = Query("active", description="문서 상태"),
    sort: str = Query("updated_at", description="정렬 기준"),
    order: str = Query("desc", description="정렬 순서 (asc/desc)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 문서 수"),
    db: AsyncSession = Depends(get_db)
):
    """
    문서 목록 조회

    - **project_id**: 프로젝트 필터 (예: dagosian)
    - **category**: 카테고리 필터 (예: characters/player)
    - **status**: active, archived, draft
    - **sort**: 정렬 기준 (created_at, updated_at, title, view_count)
    - **order**: asc (오름차순) / desc (내림차순)
    - **page**: 페이지 번호 (1부터 시작)
    - **limit**: 페이지당 문서 수 (최대 100)
    """

    # 쿼리 빌드
    query = select(Page).where(Page.status == status)

    # 프로젝트 필터
    if project_id:
        query = query.where(Page.project_id == project_id)

    # 카테고리 필터
    if category:
        query = query.where(Page.category == category)

    # 정렬
    sort_column = getattr(Page, sort, Page.updated_at)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # 페이지네이션
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    # 실행
    result = await db.execute(query)
    pages = result.scalars().all()

    # 전체 개수 조회
    count_query = select(func.count(Page.id)).where(Page.status == status)
    if project_id:
        count_query = count_query.where(Page.project_id == project_id)
    if category:
        count_query = count_query.where(Page.category == category)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    return PageListResponse(
        total=total,
        pages=[PageResponse.model_validate(page) for page in pages]
    )


@router.get("/{slug:path}", response_model=PageDetail)
async def get_page(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    문서 상세 조회

    - **slug**: 문서 식별자 (예: characters/player/elon)
    """

    # 문서 조회
    query = select(Page).where(Page.slug == slug)
    result = await db.execute(query)
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAGE_NOT_FOUND",
                "message": f"문서를 찾을 수 없습니다: {slug}"
            }
        )

    # 조회수 증가
    page.view_count += 1
    await db.commit()
    await db.refresh(page, ["tags"])  # 커밋 후 페이지 객체 새로고침

    # 관련 문서 추천 (같은 태그를 가진 문서들)
    related_pages = await _get_related_pages(db, page)

    # PageDetail 변환 - tags를 수동으로 변환
    page_dict = {
        "id": page.id,
        "slug": page.slug,
        "title": page.title,
        "category": page.category,
        "author": page.author,
        "project_id": page.project_id,
        "content": page.content,
        "summary": page.summary,
        "status": page.status,
        "tags": [tag.name for tag in page.tags],
        "created_at": page.created_at,
        "updated_at": page.updated_at,
        "view_count": page.view_count,
        "github_sha": page.github_sha,
        "content_html": page.content_html,
        "github_url": page.github_url,
        "last_synced_at": page.last_synced_at,
    }
    page_detail = PageDetail.model_validate(page_dict)

    # 관련 문서들도 tags를 수동으로 변환
    related_pages_list = []
    for p in related_pages:
        related_dict = {
            "id": p.id,
            "slug": p.slug,
            "title": p.title,
            "category": p.category,
            "author": p.author,
            "project_id": p.project_id,
            "content": p.content,
            "summary": p.summary,
            "status": p.status,
            "tags": [tag.name for tag in p.tags],
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "view_count": p.view_count,
            "github_sha": p.github_sha,
        }
        related_pages_list.append(PageResponse.model_validate(related_dict))

    page_detail.related_pages = related_pages_list

    return page_detail


async def _get_related_pages(db: AsyncSession, current_page: Page, limit: int = 5) -> list[Page]:
    """
    태그 기반 관련 문서 추천

    Args:
        db: 데이터베이스 세션
        current_page: 현재 문서
        limit: 추천 문서 수

    Returns:
        관련 문서 리스트 (공통 태그 수 기준 정렬)
    """
    if not current_page.tags:
        return []

    # 현재 문서의 태그 ID들
    current_tag_ids = [tag.id for tag in current_page.tags]

    # 같은 태그를 가진 다른 문서들 조회 (공통 태그 수로 정렬)
    # SQL: 각 문서가 현재 문서와 공유하는 태그 수를 계산
    from app.models.tag import page_tags

    query = text("""
        SELECT p.*, COUNT(pt.tag_id) as common_tags
        FROM pages p
        JOIN page_tags pt ON p.id = pt.page_id
        WHERE pt.tag_id IN :tag_ids
          AND p.id != :current_id
          AND p.status = 'active'
        GROUP BY p.id
        ORDER BY common_tags DESC
        LIMIT :limit
    """)

    result = await db.execute(
        query,
        {"tag_ids": tuple(current_tag_ids), "current_id": current_page.id, "limit": limit}
    )
    rows = result.fetchall()

    # Page 객체로 변환
    if not rows:
        return []

    from sqlalchemy.orm import selectinload

    page_ids = [row.id for row in rows]
    pages_query = select(Page).options(selectinload(Page.tags)).where(Page.id.in_(page_ids))
    pages_result = await db.execute(pages_query)
    pages_dict = {p.id: p for p in pages_result.scalars().all()}

    # rows 순서대로 정렬 (common_tags 순)
    related = [pages_dict[row.id] for row in rows if row.id in pages_dict]

    return related


@router.post("", response_model=PageResponse, status_code=201)
async def create_page(
    page_data: PageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    새 문서 생성

    1. GitHub에 Markdown 파일 커밋
    2. PostgreSQL에 메타데이터 캐싱
    """

    # slug 생성 (제공되지 않으면 title에서 생성)
    slug = page_data.slug
    if not slug:
        # 간단한 slug 생성 (실제로는 더 복잡한 로직 필요)
        slug = page_data.title.lower().replace(" ", "-")

    # 중복 체크
    existing = await db.execute(select(Page).where(Page.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SLUG_EXISTS",
                "message": f"이미 존재하는 문서입니다: {slug}"
            }
        )

    try:
        # 1. Frontmatter 생성
        metadata = extract_metadata_from_page(page_data.model_dump())
        markdown_content = create_markdown(metadata, page_data.content)

        # 2. GitHub에 커밋
        github_result = github_client.create_file(
            path=slug,
            content=markdown_content,
            message=f"Create {page_data.title}",
            author_name=page_data.author
        )

        logger.info("page_created_in_github", slug=slug, sha=github_result["sha"])

        # 3. PostgreSQL에 캐싱
        new_page = Page(
            slug=slug,
            title=page_data.title,
            category=page_data.category,
            author=page_data.author,
            project_id=page_data.project_id,  # project_id 추가
            content=page_data.content,
            summary=page_data.summary,
            status=page_data.status,
            github_sha=github_result["sha"],
            github_url=github_result["url"],
            last_synced_at=datetime.now()
        )

        db.add(new_page)
        await db.flush()  # flush하여 new_page.id 생성

        # 4. 태그 동기화
        if page_data.tags:
            await sync_tags(db, new_page, page_data.tags)

        await db.commit()
        await db.refresh(new_page, ["tags"])  # 명시적으로 tags 관계 로드

        logger.info("page_created", slug=slug, id=new_page.id, tags=page_data.tags)

        # Tag 객체를 문자열로 변환
        page_dict = {
            "id": new_page.id,
            "slug": new_page.slug,
            "title": new_page.title,
            "category": new_page.category,
            "author": new_page.author,
            "project_id": new_page.project_id,
            "content": new_page.content,
            "summary": new_page.summary,
            "status": new_page.status,
            "tags": [tag.name for tag in new_page.tags],
            "created_at": new_page.created_at,
            "updated_at": new_page.updated_at,
            "view_count": new_page.view_count,
            "github_sha": new_page.github_sha,
        }
        return PageResponse.model_validate(page_dict)

    except GithubException as e:
        logger.error("github_error", slug=slug, status=e.status, error=str(e))
        raise HTTPException(
            status_code=502,
            detail={
                "code": "GITHUB_ERROR",
                "message": "GitHub 저장에 실패했습니다. 잠시 후 다시 시도해주세요.",
                "retry_after": 5
            }
        )
    except Exception as e:
        logger.error("page_create_failed", slug=slug, error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "문서 생성에 실패했습니다."
            }
        )


@router.put("/{slug:path}", response_model=PageResponse)
async def update_page(
    slug: str,
    page_data: PageUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    문서 수정

    동시성 제어: expected_sha로 낙관적 락
    """

    # 1. 기존 문서 조회
    query = select(Page).where(Page.slug == slug)
    result = await db.execute(query)
    existing_page = result.scalar_one_or_none()

    if not existing_page:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAGE_NOT_FOUND",
                "message": f"문서를 찾을 수 없습니다: {slug}"
            }
        )

    # 2. 동시성 체크 (force=False일 때만)
    if not page_data.force and page_data.expected_sha:
        if existing_page.github_sha != page_data.expected_sha:
            logger.warning("conflict_detected", slug=slug,
                          expected=page_data.expected_sha,
                          current=existing_page.github_sha)

            raise HTTPException(
                status_code=409,
                detail={
                    "code": "CONFLICT",
                    "message": "다른 사용자가 이 문서를 수정했습니다",
                    "details": {
                        "your_sha": page_data.expected_sha,
                        "current_sha": existing_page.github_sha,
                        "last_editor": existing_page.author,
                        "last_edited_at": existing_page.updated_at.isoformat()
                    },
                    "current_content": existing_page.content
                }
            )

    try:
        # 3. 업데이트할 필드 준비
        update_data = page_data.model_dump(exclude_unset=True, exclude={"expected_sha", "force"})

        # 4. Frontmatter 생성
        metadata_dict = {
            "title": update_data.get("title", existing_page.title),
            "category": update_data.get("category", existing_page.category),
            "author": update_data.get("author", existing_page.author),
            "status": update_data.get("status", existing_page.status),
            "summary": update_data.get("summary", existing_page.summary),
            "updated": datetime.now().isoformat(),
        }
        content_text = update_data.get("content", existing_page.content)
        markdown_content = create_markdown(metadata_dict, content_text)

        # 5. GitHub 업데이트
        # force=True면 최신 SHA를 먼저 가져옴
        current_sha = existing_page.github_sha
        if page_data.force:
            github_file = github_client.get_file(slug)
            if github_file:
                current_sha = github_file["sha"]

        github_result = github_client.update_file(
            path=slug,
            content=markdown_content,
            message=f"Update {update_data.get('title', existing_page.title)}",
            sha=current_sha,
            author_name=update_data.get("author", existing_page.author)
        )

        logger.info("page_updated_in_github", slug=slug,
                   old_sha=current_sha, new_sha=github_result["sha"])

        # 6. PostgreSQL 업데이트
        for field, value in update_data.items():
            if field != 'tags':  # tags는 별도 처리
                setattr(existing_page, field, value)

        existing_page.github_sha = github_result["sha"]
        existing_page.github_url = github_result["url"]
        existing_page.last_synced_at = datetime.now()
        existing_page.updated_at = datetime.now()

        # 7. 태그 동기화 (tags가 제공된 경우)
        if page_data.tags is not None:
            await sync_tags(db, existing_page, page_data.tags)

        await db.commit()
        await db.refresh(existing_page, ["tags"])  # 명시적으로 tags 관계 로드

        logger.info("page_updated", slug=slug, tags=page_data.tags)

        # Tag 객체를 문자열로 변환
        page_dict = {
            "id": existing_page.id,
            "slug": existing_page.slug,
            "title": existing_page.title,
            "category": existing_page.category,
            "author": existing_page.author,
            "project_id": existing_page.project_id,
            "content": existing_page.content,
            "summary": existing_page.summary,
            "status": existing_page.status,
            "tags": [tag.name for tag in existing_page.tags],
            "created_at": existing_page.created_at,
            "updated_at": existing_page.updated_at,
            "view_count": existing_page.view_count,
            "github_sha": existing_page.github_sha,
        }
        return PageResponse.model_validate(page_dict)

    except GithubException as e:
        if e.status == 409:
            # GitHub에서도 충돌 감지
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "CONFLICT",
                    "message": "GitHub에서 충돌이 감지되었습니다"
                }
            )
        logger.error("github_error", slug=slug, status=e.status, error=str(e))
        raise HTTPException(
            status_code=502,
            detail={
                "code": "GITHUB_ERROR",
                "message": "GitHub 저장에 실패했습니다"
            }
        )
    except Exception as e:
        logger.error("page_update_failed", slug=slug, error=str(e))
        await db.rollback()
        raise


@router.delete("/{slug:path}", status_code=200)
async def delete_page(
    slug: str,
    soft: bool = Query(True, description="소프트 삭제 (archived로 이동)"),
    db: AsyncSession = Depends(get_db)
):
    """
    문서 삭제

    - soft=True: archived 폴더로 이동 (기본값)
    - soft=False: 완전 삭제
    """

    # 1. 문서 조회
    query = select(Page).where(Page.slug == slug)
    result = await db.execute(query)
    page = result.scalar_one_or_none()

    if not page:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAGE_NOT_FOUND",
                "message": f"문서를 찾을 수 없습니다: {slug}"
            }
        )

    try:
        if soft:
            # 소프트 삭제: archived 폴더로 이동
            archived_slug = f"archived/{slug}"

            github_client.move_file(
                old_path=slug,
                new_path=archived_slug,
                message=f"Archive {page.title}",
                sha=page.github_sha
            )

            # DB에서는 status만 변경
            page.status = "archived"
            page.slug = archived_slug
            await db.commit()

            logger.info("page_archived", old_slug=slug, new_slug=archived_slug)

            return {
                "message": "문서가 보관되었습니다",
                "new_slug": archived_slug
            }
        else:
            # 하드 삭제
            github_client.delete_file(
                path=slug,
                message=f"Delete {page.title}",
                sha=page.github_sha
            )

            # DB에서 삭제
            await db.delete(page)
            await db.commit()

            logger.info("page_deleted", slug=slug)

            return {"message": "문서가 삭제되었습니다"}

    except GithubException as e:
        logger.error("github_delete_failed", slug=slug, status=e.status, error=str(e))
        raise HTTPException(
            status_code=502,
            detail={
                "code": "GITHUB_ERROR",
                "message": "GitHub 삭제에 실패했습니다"
            }
        )
    except Exception as e:
        logger.error("page_delete_failed", slug=slug, error=str(e))
        await db.rollback()
        raise
