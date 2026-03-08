from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user import User


class AuthService:
    """Handles authentication operations: credential verification and login tracking."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Returns the User object if credentials are valid, None otherwise.
        Updates last_login_at on successful authentication.
        """
        stmt = select(User).where(User.email == email, User.is_active == True)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(user)

        return user
