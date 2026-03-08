from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, require_roles, get_current_user
from app.core.constants import TicketStatus, TicketPriority, VALID_TRANSITIONS, AuditAction
from app.models.user import User
from app.models.project import Project
from app.models.ticket import Ticket
from app.models.sla import SLAPolicy, SLARecord
from app.models.audit import AuditLog
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, StatusTransition
from app.schemas.common import PaginatedResponse

router = APIRouter()


async def _generate_ticket_number(db: AsyncSession, project_id: int) -> str:
    project = (await db.execute(select(Project).where(Project.id == project_id))).scalar_one()
    count = (await db.execute(
        select(func.count(Ticket.id)).where(Ticket.project_id == project_id)
    )).scalar()
    return f"{project.key}-{(count or 0) + 1:03d}"


async def _create_sla_record(db: AsyncSession, ticket: Ticket):
    # Find matching SLA policy: project-specific first, then default
    result = await db.execute(
        select(SLAPolicy).where(
            SLAPolicy.priority == ticket.priority,
            SLAPolicy.project_id == ticket.project_id,
            SLAPolicy.is_active.is_(True),
        )
    )
    policy = result.scalar_one_or_none()

    if not policy:
        result = await db.execute(
            select(SLAPolicy).where(
                SLAPolicy.priority == ticket.priority,
                SLAPolicy.is_default.is_(True),
                SLAPolicy.is_active.is_(True),
            )
        )
        policy = result.scalar_one_or_none()

    if policy:
        now = datetime.now(timezone.utc)
        record = SLARecord(
            ticket_id=ticket.id,
            sla_policy_id=policy.id,
            response_deadline=now + timedelta(minutes=policy.response_time_minutes),
            resolution_deadline=now + timedelta(minutes=policy.resolution_time_minutes),
        )
        db.add(record)


def _ticket_to_response(ticket: Ticket) -> TicketResponse:
    sla_info = None
    if ticket.sla_record:
        sla_info = {
            "response_deadline": ticket.sla_record.response_deadline.isoformat() if ticket.sla_record.response_deadline else None,
            "resolution_deadline": ticket.sla_record.resolution_deadline.isoformat() if ticket.sla_record.resolution_deadline else None,
            "response_met": ticket.sla_record.response_met,
            "resolution_met": ticket.sla_record.resolution_met,
        }

    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        project_id=ticket.project_id,
        project_key=ticket.project.key if ticket.project else None,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value if hasattr(ticket.priority, 'value') else ticket.priority,
        status=ticket.status.value if hasattr(ticket.status, 'value') else ticket.status,
        reporter_id=ticket.reporter_id,
        reporter_name=ticket.reporter.full_name if ticket.reporter else None,
        assignee_id=ticket.assignee_id,
        assignee_name=ticket.assignee.full_name if ticket.assignee else None,
        team_id=ticket.team_id,
        tags=ticket.tags,
        first_response_at=ticket.first_response_at,
        resolved_at=ticket.resolved_at,
        closed_at=ticket.closed_at,
        sla=sla_info,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


@router.get("", response_model=PaginatedResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Ticket).options(
        selectinload(Ticket.project),
        selectinload(Ticket.reporter),
        selectinload(Ticket.assignee),
        selectinload(Ticket.sla_record),
    )

    if project_id:
        query = query.where(Ticket.project_id == project_id)
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    if priority:
        query = query.where(Ticket.priority == priority)
    if assignee_id:
        query = query.where(Ticket.assignee_id == assignee_id)
    if search:
        query = query.where(
            (Ticket.title.ilike(f"%{search}%"))
            | (Ticket.ticket_number.ilike(f"%{search}%"))
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Order and paginate
    query = query.order_by(Ticket.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    tickets = result.scalars().all()

    return PaginatedResponse(
        items=[_ticket_to_response(t) for t in tickets],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page if total else 0,
    )


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    # Verify project exists
    project = (await db.execute(select(Project).where(Project.id == data.project_id))).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ticket_number = await _generate_ticket_number(db, data.project_id)

    ticket = Ticket(
        ticket_number=ticket_number,
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        reporter_id=current_user.id,
        assignee_id=data.assignee_id,
        team_id=data.team_id,
        tags=data.tags,
    )
    db.add(ticket)
    await db.flush()

    # Auto-create SLA record
    await _create_sla_record(db, ticket)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        entity_type="ticket",
        entity_id=ticket.id,
        action=AuditAction.CREATE,
        new_values={"title": data.title, "priority": data.priority, "status": "open"},
        created_at=datetime.now(timezone.utc),
    )
    db.add(audit)

    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket.id).options(
            selectinload(Ticket.project),
            selectinload(Ticket.reporter),
            selectinload(Ticket.assignee),
            selectinload(Ticket.sla_record),
        )
    )
    ticket = result.scalar_one()

    return _ticket_to_response(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id).options(
            selectinload(Ticket.project),
            selectinload(Ticket.reporter),
            selectinload(Ticket.assignee),
            selectinload(Ticket.sla_record),
        )
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return _ticket_to_response(ticket)


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id).options(
            selectinload(Ticket.project),
            selectinload(Ticket.reporter),
            selectinload(Ticket.assignee),
            selectinload(Ticket.sla_record),
        )
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    old_values = {}
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        old_values[field] = getattr(ticket, field)
        setattr(ticket, field, value)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        entity_type="ticket",
        entity_id=ticket.id,
        action=AuditAction.UPDATE,
        old_values=old_values,
        new_values=update_data,
        created_at=datetime.now(timezone.utc),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(ticket)

    return _ticket_to_response(ticket)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def transition_status(
    ticket_id: int,
    data: StatusTransition,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id).options(
            selectinload(Ticket.project),
            selectinload(Ticket.reporter),
            selectinload(Ticket.assignee),
            selectinload(Ticket.sla_record),
        )
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    old_status = ticket.status
    new_status = TicketStatus(data.status)

    # Enforce state machine
    if new_status not in VALID_TRANSITIONS.get(old_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{old_status.value}' to '{new_status.value}'. "
                   f"Allowed: {[s.value for s in VALID_TRANSITIONS.get(old_status, [])]}",
        )

    ticket.status = new_status
    now = datetime.now(timezone.utc)

    if new_status == TicketStatus.RESOLVED:
        ticket.resolved_at = now
        # Check resolution SLA
        if ticket.sla_record and ticket.sla_record.resolution_met is None:
            created_at = ticket.created_at.replace(tzinfo=timezone.utc) if ticket.created_at.tzinfo is None else ticket.created_at
            minutes = int((now - created_at).total_seconds() / 60)
            ticket.sla_record.actual_resolution_minutes = minutes
            resolution_deadline = ticket.sla_record.resolution_deadline.replace(tzinfo=timezone.utc) if ticket.sla_record.resolution_deadline.tzinfo is None else ticket.sla_record.resolution_deadline
            ticket.sla_record.resolution_met = now <= resolution_deadline
    elif new_status == TicketStatus.CLOSED:
        ticket.closed_at = now

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        entity_type="ticket",
        entity_id=ticket.id,
        action=AuditAction.STATUS_CHANGE,
        old_values={"status": old_status.value},
        new_values={"status": new_status.value},
        created_at=now,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(ticket)

    return _ticket_to_response(ticket)


@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    ticket_id: int,
    assignee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id).options(
            selectinload(Ticket.project),
            selectinload(Ticket.reporter),
            selectinload(Ticket.assignee),
            selectinload(Ticket.sla_record),
        )
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    old_assignee = ticket.assignee_id
    ticket.assignee_id = assignee_id

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        entity_type="ticket",
        entity_id=ticket.id,
        action=AuditAction.ASSIGN,
        old_values={"assignee_id": old_assignee},
        new_values={"assignee_id": assignee_id},
        created_at=datetime.now(timezone.utc),
    )
    db.add(audit)

    await db.commit()
    await db.refresh(ticket)

    return _ticket_to_response(ticket)
