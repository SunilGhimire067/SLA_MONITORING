from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_db, get_current_user
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token,
)
from app.models.user import User
from app.models.permission import Permission, RolePermission
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


async def _get_user_permissions(db: AsyncSession, role_id: int) -> list[str]:
    result = await db.execute(
        select(Permission.name)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == role_id)
    )
    return [row[0] for row in result.all()]


def _user_response(user: User, permissions: list[str]) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.name,
        is_active=user.is_active,
        timezone=user.timezone,
        permissions=permissions,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == data.email, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    permissions = await _get_user_permissions(db, user.role_id)
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=_user_response(user, permissions),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    result = await db.execute(
        select(User).where(User.id == int(user_id), User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    permissions = await _get_user_permissions(db, user.role_id)
    new_access = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        user=_user_response(user, permissions),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    permissions = await _get_user_permissions(db, current_user.role_id)
    return _user_response(current_user, permissions)


@router.put("/me/password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password_hash = get_password_hash(new_password)
    await db.commit()
    return {"message": "Password updated successfully"}
