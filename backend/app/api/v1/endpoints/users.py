from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.dependencies import get_db, get_current_user, require_roles
from app.core.security import get_password_hash
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    query = select(User)

    if role:
        query = query.join(Role).where(Role.name == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        query = query.where(
            (User.first_name.ilike(f"%{search}%"))
            | (User.last_name.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    users = result.scalars().all()

    return PaginatedResponse(
        items=[
            UserResponse(
                id=u.id, email=u.email, first_name=u.first_name,
                last_name=u.last_name, role=u.role.name, is_active=u.is_active,
                timezone=u.timezone, created_at=u.created_at, updated_at=u.updated_at,
            ) for u in users
        ],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page if total else 0,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Find role
    role_result = await db.execute(select(Role).where(Role.name == data.role))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{data.role}' not found")

    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role_id=role.id,
        phone=data.phone,
        timezone=data.timezone or "UTC",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=role.name, is_active=user.is_active,
        timezone=user.timezone, created_at=user.created_at, updated_at=user.updated_at,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role.name, is_active=user.is_active,
        timezone=user.timezone, created_at=user.created_at, updated_at=user.updated_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)

    if "role" in update_data:
        role_result = await db.execute(select(Role).where(Role.name == update_data.pop("role")))
        role = role_result.scalar_one_or_none()
        if role:
            user.role_id = role.id

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role.name, is_active=user.is_active,
        timezone=user.timezone, created_at=user.created_at, updated_at=user.updated_at,
    )


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    return {"message": "User deactivated successfully"}
