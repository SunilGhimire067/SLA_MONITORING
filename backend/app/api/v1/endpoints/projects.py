from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer", "viewer")),
):
    query = select(Project)
    if is_active is not None:
        query = query.where(Project.is_active == is_active)

    result = await db.execute(query)
    projects = result.scalars().all()

    return [
        ProjectResponse(
            id=p.id, name=p.name, key=p.key, description=p.description,
            lead_id=p.lead_id, is_active=p.is_active,
            created_at=p.created_at, updated_at=p.updated_at,
        ) for p in projects
    ]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    # Check duplicate key
    existing = await db.execute(select(Project).where(Project.key == data.key.upper()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Project key '{data.key}' already exists")

    project = Project(
        name=data.name, key=data.key.upper(),
        description=data.description, lead_id=data.lead_id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectResponse(
        id=project.id, name=project.name, key=project.key,
        description=project.description, lead_id=project.lead_id,
        is_active=project.is_active,
        created_at=project.created_at, updated_at=project.updated_at,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer", "viewer")),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=project.id, name=project.name, key=project.key,
        description=project.description, lead_id=project.lead_id,
        is_active=project.is_active,
        created_at=project.created_at, updated_at=project.updated_at,
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    return ProjectResponse(
        id=project.id, name=project.name, key=project.key,
        description=project.description, lead_id=project.lead_id,
        is_active=project.is_active,
        created_at=project.created_at, updated_at=project.updated_at,
    )


@router.delete("/{project_id}")
async def archive_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.is_active = False
    await db.commit()
    return {"message": "Project archived successfully"}
