from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.dependencies import get_db, require_roles, get_current_user
from app.models.user import User, Role
from app.models.permission import Permission, RolePermission
from app.schemas.permission import PermissionResponse, RoleResponse, RolePermissionsUpdate

router = APIRouter()


@router.get("", response_model=list[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Permission).order_by(Permission.category, Permission.name))
    return [
        PermissionResponse(id=p.id, name=p.name, description=p.description, category=p.category)
        for p in result.scalars().all()
    ]


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles_with_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    roles = (await db.execute(select(Role).order_by(Role.id))).scalars().all()
    result = []
    for role in roles:
        perms = await db.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role.id)
        )
        result.append(RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=[
                PermissionResponse(id=p.id, name=p.name, description=p.description, category=p.category)
                for p in perms.scalars().all()
            ],
        ))
    return result


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role_permissions(
    role_id: int,
    data: RolePermissionsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    role = (await db.execute(select(Role).where(Role.id == role_id))).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Prevent removing manage_roles from admin
    if role.name == "admin":
        manage_roles_perm = (await db.execute(
            select(Permission).where(Permission.name == "manage_roles")
        )).scalar_one_or_none()
        if manage_roles_perm and manage_roles_perm.id not in data.permission_ids:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove 'manage_roles' from admin role",
            )

    # Delete existing and insert new
    await db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
    for perm_id in data.permission_ids:
        db.add(RolePermission(role_id=role_id, permission_id=perm_id))
    await db.commit()

    # Return updated
    perms = await db.execute(
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == role_id)
    )
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=[
            PermissionResponse(id=p.id, name=p.name, description=p.description, category=p.category)
            for p in perms.scalars().all()
        ],
    )
