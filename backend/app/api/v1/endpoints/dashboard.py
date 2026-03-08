from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case

from app.core.dependencies import get_db, get_current_user, require_roles
from app.core.constants import TicketStatus
from app.models.user import User
from app.models.ticket import Ticket
from app.models.sla import SLARecord

router = APIRouter()


def _apply_filters(query, project_id, team_id, date_from, date_to):
    if project_id:
        query = query.where(Ticket.project_id == project_id)
    if team_id:
        query = query.where(Ticket.team_id == team_id)
    if date_from:
        query = query.where(Ticket.created_at >= date_from)
    if date_to:
        query = query.where(Ticket.created_at <= date_to)
    return query


@router.get("/overview")
async def dashboard_overview(
    project_id: Optional[int] = None,
    team_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base = select(Ticket)
    base = _apply_filters(base, project_id, team_id, date_from, date_to)

    # Total tickets
    total = (await db.execute(
        select(func.count()).select_from(base.subquery())
    )).scalar() or 0

    # By status
    status_counts = {}
    for s in TicketStatus:
        count = (await db.execute(
            select(func.count()).select_from(
                _apply_filters(
                    select(Ticket).where(Ticket.status == s),
                    project_id, team_id, date_from, date_to
                ).subquery()
            )
        )).scalar() or 0
        status_counts[s.value] = count

    # SLA compliance
    sla_query = select(SLARecord).join(Ticket)
    sla_query = _apply_filters(sla_query, project_id, team_id, date_from, date_to)

    total_sla = (await db.execute(
        select(func.count()).select_from(sla_query.subquery())
    )).scalar() or 0

    met_query = sla_query.where(
        SLARecord.resolution_met.is_(True)
    )
    sla_met = (await db.execute(
        select(func.count()).select_from(met_query.subquery())
    )).scalar() or 0

    sla_compliance = round((sla_met / total_sla * 100), 1) if total_sla > 0 else 100.0

    # Average resolution time
    avg_resolution = (await db.execute(
        select(func.avg(SLARecord.actual_resolution_minutes)).select_from(
            sla_query.where(SLARecord.actual_resolution_minutes.isnot(None)).subquery()
        )
    )).scalar()

    return {
        "total_tickets": total,
        "open": status_counts.get("open", 0),
        "in_progress": status_counts.get("in_progress", 0),
        "blocked": status_counts.get("blocked", 0),
        "resolved": status_counts.get("resolved", 0),
        "closed": status_counts.get("closed", 0),
        "sla_compliance_pct": sla_compliance,
        "avg_resolution_minutes": round(avg_resolution, 1) if avg_resolution else None,
        "sla_total": total_sla,
        "sla_met": sla_met,
        "sla_breached": total_sla - sla_met,
    }


@router.get("/tickets-by-status")
async def tickets_by_status(
    project_id: Optional[int] = None,
    team_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Ticket.status, func.count(Ticket.id).label("count")).group_by(Ticket.status)
    if project_id:
        query = query.where(Ticket.project_id == project_id)
    if team_id:
        query = query.where(Ticket.team_id == team_id)
    if date_from:
        query = query.where(Ticket.created_at >= date_from)
    if date_to:
        query = query.where(Ticket.created_at <= date_to)

    result = await db.execute(query)
    rows = result.all()

    return [{"status": row[0].value if hasattr(row[0], 'value') else row[0], "count": row[1]} for row in rows]


@router.get("/tickets-by-priority")
async def tickets_by_priority(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Ticket.priority, func.count(Ticket.id).label("count")).group_by(Ticket.priority)
    if project_id:
        query = query.where(Ticket.project_id == project_id)

    result = await db.execute(query)
    rows = result.all()

    return [{"priority": row[0].value if hasattr(row[0], 'value') else row[0], "count": row[1]} for row in rows]


@router.get("/sla-compliance")
async def sla_compliance(
    project_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = select(SLARecord).join(Ticket)
    if project_id:
        base_query = base_query.where(Ticket.project_id == project_id)
    if date_from:
        base_query = base_query.where(Ticket.created_at >= date_from)
    if date_to:
        base_query = base_query.where(Ticket.created_at <= date_to)

    # Overall
    total = (await db.execute(select(func.count()).select_from(base_query.subquery()))).scalar() or 0
    met = (await db.execute(
        select(func.count()).select_from(
            base_query.where(SLARecord.resolution_met.is_(True)).subquery()
        )
    )).scalar() or 0

    # By priority
    by_priority = {}
    for priority in ["P1", "P2", "P3", "P4"]:
        pq = base_query.where(Ticket.priority == priority)
        p_total = (await db.execute(select(func.count()).select_from(pq.subquery()))).scalar() or 0
        p_met = (await db.execute(
            select(func.count()).select_from(
                pq.where(SLARecord.resolution_met.is_(True)).subquery()
            )
        )).scalar() or 0
        by_priority[priority] = {
            "total": p_total,
            "met": p_met,
            "breached": p_total - p_met,
            "compliance_pct": round((p_met / p_total * 100), 1) if p_total > 0 else None,
        }

    return {
        "overall": round((met / total * 100), 1) if total > 0 else 100.0,
        "total": total,
        "met": met,
        "breached": total - met,
        "by_priority": by_priority,
    }


@router.get("/mttr")
async def mean_time_to_resolve(
    project_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(
        func.avg(SLARecord.actual_resolution_minutes).label("avg_mttr"),
        func.min(SLARecord.actual_resolution_minutes).label("min_mttr"),
        func.max(SLARecord.actual_resolution_minutes).label("max_mttr"),
        func.count(SLARecord.id).label("total"),
    ).join(Ticket).where(SLARecord.actual_resolution_minutes.isnot(None))

    if project_id:
        query = query.where(Ticket.project_id == project_id)
    if date_from:
        query = query.where(Ticket.created_at >= date_from)
    if date_to:
        query = query.where(Ticket.created_at <= date_to)

    result = (await db.execute(query)).one()

    # By priority
    by_priority = {}
    for priority in ["P1", "P2", "P3", "P4"]:
        pq = select(
            func.avg(SLARecord.actual_resolution_minutes)
        ).join(Ticket).where(
            SLARecord.actual_resolution_minutes.isnot(None),
            Ticket.priority == priority,
        )
        if project_id:
            pq = pq.where(Ticket.project_id == project_id)
        p_avg = (await db.execute(pq)).scalar()
        by_priority[priority] = round(p_avg, 1) if p_avg else None

    return {
        "avg_mttr_minutes": round(result.avg_mttr, 1) if result.avg_mttr else None,
        "min_mttr_minutes": result.min_mttr,
        "max_mttr_minutes": result.max_mttr,
        "total_resolved": result.total,
        "by_priority": by_priority,
    }


@router.get("/engineer-performance")
async def engineer_performance(
    project_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    query = select(
        Ticket.assignee_id,
        User.first_name,
        User.last_name,
        User.email,
        func.count(Ticket.id).label("total_tickets"),
        func.sum(case((Ticket.status.in_(["resolved", "closed"]), 1), else_=0)).label("resolved"),
    ).join(User, Ticket.assignee_id == User.id).group_by(
        Ticket.assignee_id, User.first_name, User.last_name, User.email
    )

    if project_id:
        query = query.where(Ticket.project_id == project_id)
    if date_from:
        query = query.where(Ticket.created_at >= date_from)
    if date_to:
        query = query.where(Ticket.created_at <= date_to)

    result = await db.execute(query)
    rows = result.all()

    engineers = []
    for row in rows:
        # Get SLA compliance for this engineer
        sla_total = (await db.execute(
            select(func.count()).select_from(
                select(SLARecord).join(Ticket).where(Ticket.assignee_id == row[0]).subquery()
            )
        )).scalar() or 0
        sla_met = (await db.execute(
            select(func.count()).select_from(
                select(SLARecord).join(Ticket).where(
                    Ticket.assignee_id == row[0],
                    SLARecord.resolution_met.is_(True),
                ).subquery()
            )
        )).scalar() or 0

        # Get avg resolution time
        avg_res = (await db.execute(
            select(func.avg(SLARecord.actual_resolution_minutes)).join(Ticket).where(
                Ticket.assignee_id == row[0],
                SLARecord.actual_resolution_minutes.isnot(None),
            )
        )).scalar()

        engineers.append({
            "engineer_id": row[0],
            "engineer_name": f"{row[1]} {row[2]}",
            "email": row[3],
            "total_tickets": row[4],
            "resolved": row[5],
            "avg_resolution_minutes": round(avg_res, 1) if avg_res else None,
            "sla_compliance_pct": round((sla_met / sla_total * 100), 1) if sla_total > 0 else None,
        })

    return engineers


@router.get("/team-performance")
async def team_performance(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    from app.models.team import Team

    query = select(
        Ticket.team_id,
        Team.name,
        func.count(Ticket.id).label("total_tickets"),
        func.sum(case((Ticket.status.in_(["resolved", "closed"]), 1), else_=0)).label("resolved"),
    ).join(Team, Ticket.team_id == Team.id).group_by(Ticket.team_id, Team.name)

    if date_from:
        query = query.where(Ticket.created_at >= date_from)
    if date_to:
        query = query.where(Ticket.created_at <= date_to)

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "team_id": row[0],
            "team_name": row[1],
            "total_tickets": row[2],
            "resolved": row[3],
        } for row in rows
    ]
