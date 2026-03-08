from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, require_roles, get_current_user
from app.models.user import User
from app.models.sla import SLAPolicy, SLARecord
from app.models.ticket import Ticket
from app.schemas.sla import SLAPolicyCreate, SLAPolicyUpdate, SLAPolicyResponse, SLARecordResponse

router = APIRouter()


@router.get("/policies", response_model=list[SLAPolicyResponse])
async def list_sla_policies(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(SLAPolicy).where(SLAPolicy.is_active.is_(True))
    if project_id:
        query = query.where(SLAPolicy.project_id == project_id)

    result = await db.execute(query)
    policies = result.scalars().all()

    return [
        SLAPolicyResponse(
            id=p.id, name=p.name, priority=p.priority.value,
            project_id=p.project_id,
            response_time_minutes=p.response_time_minutes,
            resolution_time_minutes=p.resolution_time_minutes,
            is_default=p.is_default, is_active=p.is_active,
            created_at=p.created_at, updated_at=p.updated_at,
        ) for p in policies
    ]


@router.post("/policies", response_model=SLAPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_sla_policy(
    data: SLAPolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    policy = SLAPolicy(
        name=data.name,
        priority=data.priority,
        project_id=data.project_id,
        response_time_minutes=data.response_time_minutes,
        resolution_time_minutes=data.resolution_time_minutes,
        is_default=data.is_default or False,
    )
    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    return SLAPolicyResponse(
        id=policy.id, name=policy.name, priority=policy.priority.value,
        project_id=policy.project_id,
        response_time_minutes=policy.response_time_minutes,
        resolution_time_minutes=policy.resolution_time_minutes,
        is_default=policy.is_default, is_active=policy.is_active,
        created_at=policy.created_at, updated_at=policy.updated_at,
    )


@router.get("/policies/{policy_id}", response_model=SLAPolicyResponse)
async def get_sla_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(SLAPolicy).where(SLAPolicy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="SLA Policy not found")

    return SLAPolicyResponse(
        id=policy.id, name=policy.name, priority=policy.priority.value,
        project_id=policy.project_id,
        response_time_minutes=policy.response_time_minutes,
        resolution_time_minutes=policy.resolution_time_minutes,
        is_default=policy.is_default, is_active=policy.is_active,
        created_at=policy.created_at, updated_at=policy.updated_at,
    )


@router.put("/policies/{policy_id}", response_model=SLAPolicyResponse)
async def update_sla_policy(
    policy_id: int,
    data: SLAPolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(select(SLAPolicy).where(SLAPolicy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="SLA Policy not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)

    await db.commit()
    await db.refresh(policy)

    return SLAPolicyResponse(
        id=policy.id, name=policy.name, priority=policy.priority.value,
        project_id=policy.project_id,
        response_time_minutes=policy.response_time_minutes,
        resolution_time_minutes=policy.resolution_time_minutes,
        is_default=policy.is_default, is_active=policy.is_active,
        created_at=policy.created_at, updated_at=policy.updated_at,
    )


@router.delete("/policies/{policy_id}")
async def deactivate_sla_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    result = await db.execute(select(SLAPolicy).where(SLAPolicy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="SLA Policy not found")

    policy.is_active = False
    await db.commit()
    return {"message": "SLA Policy deactivated"}


@router.get("/records", response_model=list[SLARecordResponse])
async def list_sla_records(
    breached: Optional[bool] = None,
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(SLARecord).options(
        selectinload(SLARecord.ticket).selectinload(Ticket.project),
        selectinload(SLARecord.sla_policy),
    )

    if breached is True:
        query = query.where(
            (SLARecord.response_met.is_(False)) | (SLARecord.resolution_met.is_(False))
        )
    elif breached is False:
        query = query.where(
            (SLARecord.response_met.is_(True)) & (SLARecord.resolution_met.is_(True))
        )

    result = await db.execute(query.order_by(SLARecord.created_at.desc()).limit(100))
    records = result.scalars().all()

    return [
        SLARecordResponse(
            id=r.id,
            ticket_id=r.ticket_id,
            ticket_number=r.ticket.ticket_number if r.ticket else None,
            sla_policy_id=r.sla_policy_id,
            response_deadline=r.response_deadline,
            resolution_deadline=r.resolution_deadline,
            response_met=r.response_met,
            resolution_met=r.resolution_met,
            actual_response_minutes=r.actual_response_minutes,
            actual_resolution_minutes=r.actual_resolution_minutes,
            created_at=r.created_at,
        ) for r in records
    ]


@router.get("/breaches", response_model=list[SLARecordResponse])
async def list_breached_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SLARecord).where(
            (SLARecord.response_met.is_(False)) | (SLARecord.resolution_met.is_(False))
        ).options(
            selectinload(SLARecord.ticket),
            selectinload(SLARecord.sla_policy),
        ).order_by(SLARecord.created_at.desc())
    )
    records = result.scalars().all()

    return [
        SLARecordResponse(
            id=r.id,
            ticket_id=r.ticket_id,
            ticket_number=r.ticket.ticket_number if r.ticket else None,
            sla_policy_id=r.sla_policy_id,
            response_deadline=r.response_deadline,
            resolution_deadline=r.resolution_deadline,
            response_met=r.response_met,
            resolution_met=r.resolution_met,
            actual_response_minutes=r.actual_response_minutes,
            actual_resolution_minutes=r.actual_resolution_minutes,
            created_at=r.created_at,
        ) for r in records
    ]
