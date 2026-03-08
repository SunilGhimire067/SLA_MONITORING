from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.team import Team, TeamMembership
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate


class TeamService:
    """Manages team CRUD operations and team membership."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_teams(self) -> list[Team]:
        """Retrieve all teams with their memberships eagerly loaded."""
        stmt = (
            select(Team)
            .options(
                selectinload(Team.memberships).joinedload(TeamMembership.user),
                joinedload(Team.lead),
            )
            .order_by(Team.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_team(self, team_id: int) -> Team:
        """
        Retrieve a single team by ID with memberships.

        Raises HTTP 404 if the team does not exist.
        """
        stmt = (
            select(Team)
            .options(
                selectinload(Team.memberships).joinedload(TeamMembership.user),
                joinedload(Team.lead),
            )
            .where(Team.id == team_id)
        )
        result = await self.db.execute(stmt)
        team = result.scalar_one_or_none()

        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with id {team_id} not found",
            )
        return team

    async def create_team(self, data: TeamCreate) -> Team:
        """Create a new team."""
        team = Team(
            name=data.name,
            description=data.description,
            lead_id=data.lead_id,
        )
        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def update_team(self, team_id: int, data: TeamUpdate) -> Team:
        """Update an existing team's attributes."""
        team = await self.get_team(team_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(team, field, value)

        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def delete_team(self, team_id: int) -> None:
        """
        Delete a team and all associated memberships (cascade).

        Raises HTTP 404 if the team does not exist.
        """
        team = await self.get_team(team_id)
        await self.db.delete(team)
        await self.db.commit()

    async def add_member(self, team_id: int, user_id: int) -> TeamMembership:
        """
        Add a user to a team.

        Raises HTTP 404 if the team or user does not exist.
        Raises HTTP 409 if the user is already a member.
        """
        # Verify team exists
        await self.get_team(team_id)

        # Verify user exists
        user_stmt = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_stmt)
        if user_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        # Check for existing membership
        existing_stmt = select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.user_id == user_id,
        )
        existing_result = await self.db.execute(existing_stmt)
        if existing_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {user_id} is already a member of team {team_id}",
            )

        membership = TeamMembership(
            team_id=team_id,
            user_id=user_id,
            joined_at=datetime.now(timezone.utc),
        )
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def remove_member(self, team_id: int, user_id: int) -> None:
        """
        Remove a user from a team.

        Raises HTTP 404 if the membership does not exist.
        """
        stmt = select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        membership = result.scalar_one_or_none()

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a member of team {team_id}",
            )

        await self.db.delete(membership)
        await self.db.commit()
