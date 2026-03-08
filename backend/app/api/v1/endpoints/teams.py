from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.models.team import Team, TeamMembership
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamMemberAdd

router = APIRouter()


@router.get("", response_model=list[TeamResponse])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer", "viewer")),
):
    result = await db.execute(
        select(Team).options(selectinload(Team.memberships).selectinload(TeamMembership.user))
    )
    teams = result.scalars().all()
    return [
        TeamResponse(
            id=t.id, name=t.name, description=t.description, lead_id=t.lead_id,
            member_count=len(t.memberships),
            created_at=t.created_at, updated_at=t.updated_at,
        ) for t in teams
    ]


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    team = Team(name=data.name, description=data.description, lead_id=data.lead_id)
    db.add(team)
    await db.commit()
    await db.refresh(team)

    return TeamResponse(
        id=team.id, name=team.name, description=team.description,
        lead_id=team.lead_id, member_count=0,
        created_at=team.created_at, updated_at=team.updated_at,
    )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer", "viewer")),
):
    result = await db.execute(
        select(Team).where(Team.id == team_id)
        .options(selectinload(Team.memberships).selectinload(TeamMembership.user))
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return TeamResponse(
        id=team.id, name=team.name, description=team.description,
        lead_id=team.lead_id, member_count=len(team.memberships),
        members=[
            {"user_id": m.user_id, "name": m.user.full_name, "email": m.user.email}
            for m in team.memberships
        ],
        created_at=team.created_at, updated_at=team.updated_at,
    )


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(team, field, value)

    await db.commit()
    await db.refresh(team)

    return TeamResponse(
        id=team.id, name=team.name, description=team.description,
        lead_id=team.lead_id, member_count=0,
        created_at=team.created_at, updated_at=team.updated_at,
    )


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    await db.delete(team)
    await db.commit()
    return {"message": "Team deleted successfully"}


@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    team_id: int,
    data: TeamMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    # Verify team exists
    team = (await db.execute(select(Team).where(Team.id == team_id))).scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if already a member
    existing = await db.execute(
        select(TeamMembership).where(
            TeamMembership.team_id == team_id, TeamMembership.user_id == data.user_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member of this team")

    membership = TeamMembership(
        team_id=team_id, user_id=data.user_id,
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.commit()
    return {"message": "Member added successfully"}


@router.delete("/{team_id}/members/{user_id}")
async def remove_member(
    team_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(
        select(TeamMembership).where(
            TeamMembership.team_id == team_id, TeamMembership.user_id == user_id
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    await db.delete(membership)
    await db.commit()
    return {"message": "Member removed successfully"}
