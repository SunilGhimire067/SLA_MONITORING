from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Manages project CRUD operations and archival."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_projects(self, is_active: Optional[bool] = None) -> list[Project]:
        """Retrieve all projects with optional active-status filtering."""
        stmt = select(Project).options(joinedload(Project.lead)).order_by(Project.name)
        if is_active is not None:
            stmt = stmt.where(Project.is_active == is_active)

        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_project(self, project_id: int) -> Project:
        """
        Retrieve a single project by ID.

        Raises HTTP 404 if the project does not exist.
        """
        stmt = (
            select(Project)
            .options(joinedload(Project.lead))
            .where(Project.id == project_id)
        )
        result = await self.db.execute(stmt)
        project = result.scalar_one_or_none()

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found",
            )
        return project

    async def create_project(self, data: ProjectCreate) -> Project:
        """
        Create a new project.

        Raises HTTP 409 if the project key already exists.
        """
        # Check for duplicate key
        existing_stmt = select(Project).where(Project.key == data.key)
        existing_result = await self.db.execute(existing_stmt)
        if existing_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project key '{data.key}' already exists",
            )

        project = Project(
            name=data.name,
            key=data.key,
            description=data.description,
            lead_id=data.lead_id,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_project(self, project_id: int, data: ProjectUpdate) -> Project:
        """Update an existing project's attributes."""
        project = await self.get_project(project_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def archive_project(self, project_id: int) -> Project:
        """Soft-archive a project by setting is_active to False."""
        project = await self.get_project(project_id)
        project.is_active = False
        await self.db.commit()
        await self.db.refresh(project)
        return project
