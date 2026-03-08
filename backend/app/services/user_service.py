from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Manages user CRUD operations including creation, updates, and deactivation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role_filter: Optional[int] = None,
        is_active_filter: Optional[bool] = None,
    ) -> tuple[list[User], int]:
        """
        Retrieve a paginated list of users with optional filtering by role and active status.

        Returns a tuple of (user_list, total_count).
        """
        conditions = []
        if role_filter is not None:
            conditions.append(User.role_id == role_filter)
        if is_active_filter is not None:
            conditions.append(User.is_active == is_active_filter)

        # Count query
        count_stmt = select(func.count(User.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # Data query
        stmt = select(User).options(joinedload(User.role))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        users = result.scalars().unique().all()

        return list(users), total

    async def get_user(self, user_id: int) -> User:
        """
        Retrieve a single user by ID.

        Raises HTTP 404 if the user does not exist.
        """
        stmt = select(User).options(joinedload(User.role)).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return user

    async def create_user(self, data: UserCreate) -> User:
        """
        Create a new user.

        Hashes the plain-text password before storing.
        Raises HTTP 409 if the email is already registered.
        """
        # Check for duplicate email
        existing_stmt = select(User).where(User.email == data.email)
        existing_result = await self.db.execute(existing_stmt)
        if existing_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {data.email} is already registered",
            )

        user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role_id=data.role_id,
            phone=data.phone,
            timezone=data.timezone,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        """
        Update an existing user's attributes.

        Only non-None fields in the update payload are applied.
        """
        user = await self.get_user(user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def deactivate_user(self, user_id: int) -> User:
        """Soft-delete a user by setting is_active to False."""
        user = await self.get_user(user_id)
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        return user
