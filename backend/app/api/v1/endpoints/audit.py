import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("/logs", response_model=PaginatedResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    query = select(AuditLog).options(selectinload(AuditLog.user))

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if date_from:
        query = query.where(AuditLog.created_at >= date_from)
    if date_to:
        query = query.where(AuditLog.created_at <= date_to)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    logs = result.scalars().all()

    return PaginatedResponse(
        items=[
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                user_email=log.user.email if log.user else None,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                action=log.action.value,
                old_values=log.old_values,
                new_values=log.new_values,
                ip_address=log.ip_address,
                created_at=log.created_at,
            ) for log in logs
        ],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page if total else 0,
    )


@router.get("/logs/{entity_type}/{entity_id}", response_model=list[AuditLogResponse])
async def get_entity_audit_trail(
    entity_type: str,
    entity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .options(selectinload(AuditLog.user))
        .order_by(AuditLog.created_at.asc())
    )
    logs = result.scalars().all()

    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_email=log.user.email if log.user else None,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            action=log.action.value,
            old_values=log.old_values,
            new_values=log.new_values,
            ip_address=log.ip_address,
            created_at=log.created_at,
        ) for log in logs
    ]


@router.post("/export")
async def export_audit_report(
    report_type: str = Query(..., description="Report type: PCI, ISO, SOC2"),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    format: str = Query("csv", description="Export format: csv"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    query = select(AuditLog).options(selectinload(AuditLog.user))

    if date_from:
        query = query.where(AuditLog.created_at >= date_from)
    if date_to:
        query = query.where(AuditLog.created_at <= date_to)

    query = query.order_by(AuditLog.created_at.asc())
    result = await db.execute(query)
    logs = result.scalars().all()

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Timestamp", "User", "Entity Type", "Entity ID",
        "Action", "Old Values", "New Values", "IP Address",
    ])

    for log in logs:
        writer.writerow([
            log.created_at.isoformat() if log.created_at else "",
            log.user.email if log.user else "system",
            log.entity_type,
            log.entity_id,
            log.action.value,
            str(log.old_values) if log.old_values else "",
            str(log.new_values) if log.new_values else "",
            log.ip_address or "",
        ])

    output.seek(0)
    filename = f"{report_type}_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
