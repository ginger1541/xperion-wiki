"""
Projects API - 프로젝트(세계관) 관리
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.project import Project
from app.models.page import Page
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def get_projects(db: AsyncSession = Depends(get_db)):
    """모든 프로젝트 조회"""
    # Get all projects with doc count
    result = await db.execute(
        select(
            Project,
            func.count(Page.id).label("doc_count")
        )
        .outerjoin(Page, Project.id == Page.project_id)
        .group_by(Project.id)
        .order_by(Project.created_at)
    )

    projects_with_count = result.all()

    # Update doc_count in database
    for project, count in projects_with_count:
        project.doc_count = count

    await db.commit()

    projects = [project for project, _ in projects_with_count]

    return ProjectListResponse(
        total=len(projects),
        projects=projects
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """단일 프로젝트 조회"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """새 프로젝트 생성"""
    # Check if project ID already exists
    result = await db.execute(
        select(Project).where(Project.id == project_data.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Project ID already exists")

    # Create new project
    new_project = Project(**project_data.model_dump())
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return new_project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """프로젝트 업데이트"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """프로젝트 삭제 (모든 하위 페이지도 삭제됨)"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()

    return None
