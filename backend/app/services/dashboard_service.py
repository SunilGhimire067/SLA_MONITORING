from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, and_, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import TicketStatus, TicketPriority
from app.models.ticket import Ticket
from app.models.sla import SLARecord
from app.models.user import User
from app.models.team import Team


class DashboardService:
    """
    Aggregation and analytics service for the dashboard.

    Produces KPIs, distribution breakdowns, SLA compliance metrics,
    mean-time-to-resolve trends, and per-engineer / per-team performance.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Shared helpers
    # ------------------------------------------------------------------ #

    def _base_conditions(
        self,
        project_id: Optional[int],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> list:
        """Build common filter conditions for ticket queries."""
        conditions = []
        if project_id is not None:
            conditions.append(Ticket.project_id == project_id)
        if date_from is not None:
            conditions.append(Ticket.created_at >= date_from)
        if date_to is not None:
            conditions.append(Ticket.created_at <= date_to)
        return conditions

    # ------------------------------------------------------------------ #
    #  Overview KPI
    # ------------------------------------------------------------------ #

    async def get_overview(
        self,
        project_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        """
        Return high-level KPIs:
          - Total tickets, open, in_progress, resolved, closed counts
          - SLA compliance percentage
          - Average resolution time in minutes
        """
        conditions = self._base_conditions(project_id, date_from, date_to)

        # Ticket counts by status
        status_counts_stmt = select(
            Ticket.status,
            func.count(Ticket.id).label("count"),
        )
        if conditions:
            status_counts_stmt = status_counts_stmt.where(and_(*conditions))
        status_counts_stmt = status_counts_stmt.group_by(Ticket.status)

        result = await self.db.execute(status_counts_stmt)
        status_map = {row.status: row.count for row in result.all()}

        total = sum(status_map.values())
        open_count = status_map.get(TicketStatus.OPEN, 0)
        in_progress_count = status_map.get(TicketStatus.IN_PROGRESS, 0)
        resolved_count = status_map.get(TicketStatus.RESOLVED, 0)
        closed_count = status_map.get(TicketStatus.CLOSED, 0)
        blocked_count = status_map.get(TicketStatus.BLOCKED, 0)

        # SLA compliance: percentage of SLA records where both response and resolution were met
        sla_stmt = select(
            func.count(SLARecord.id).label("total_sla"),
            func.sum(
                case(
                    (
                        and_(
                            SLARecord.response_met == True,
                            SLARecord.resolution_met == True,
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("met_count"),
        ).join(SLARecord.ticket)
        if conditions:
            sla_stmt = sla_stmt.where(and_(*conditions))
        sla_result = await self.db.execute(sla_stmt)
        sla_row = sla_result.one()
        total_sla = sla_row.total_sla or 0
        met_count = sla_row.met_count or 0
        sla_compliance = round((met_count / total_sla * 100), 2) if total_sla > 0 else 100.0

        # Average resolution time (only for tickets that have been resolved)
        avg_stmt = select(
            func.avg(SLARecord.actual_resolution_minutes).label("avg_resolution")
        ).join(SLARecord.ticket)
        avg_conditions = list(conditions) + [SLARecord.actual_resolution_minutes.isnot(None)]
        if avg_conditions:
            avg_stmt = avg_stmt.where(and_(*avg_conditions))
        avg_result = await self.db.execute(avg_stmt)
        avg_resolution = avg_result.scalar() or 0

        return {
            "total_tickets": total,
            "open": open_count,
            "in_progress": in_progress_count,
            "blocked": blocked_count,
            "resolved": resolved_count,
            "closed": closed_count,
            "sla_compliance_percent": sla_compliance,
            "avg_resolution_minutes": round(float(avg_resolution), 2),
        }

    # ------------------------------------------------------------------ #
    #  Tickets by status
    # ------------------------------------------------------------------ #

    async def get_tickets_by_status(
        self,
        project_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        """Return ticket counts grouped by status."""
        conditions = self._base_conditions(project_id, date_from, date_to)

        stmt = select(
            Ticket.status,
            func.count(Ticket.id).label("count"),
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.group_by(Ticket.status)

        result = await self.db.execute(stmt)
        return [
            {"status": row.status.value, "count": row.count}
            for row in result.all()
        ]

    # ------------------------------------------------------------------ #
    #  SLA compliance per priority
    # ------------------------------------------------------------------ #

    async def get_sla_compliance(
        self,
        project_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        """
        Return SLA compliance metrics broken down by ticket priority.
        """
        conditions = self._base_conditions(project_id, date_from, date_to)

        stmt = (
            select(
                Ticket.priority,
                func.count(SLARecord.id).label("total"),
                func.sum(
                    case((SLARecord.response_met == True, 1), else_=0)
                ).label("response_met"),
                func.sum(
                    case((SLARecord.resolution_met == True, 1), else_=0)
                ).label("resolution_met"),
                func.sum(
                    case((SLARecord.response_met == False, 1), else_=0)
                ).label("response_breached"),
                func.sum(
                    case((SLARecord.resolution_met == False, 1), else_=0)
                ).label("resolution_breached"),
            )
            .join(SLARecord.ticket)
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.group_by(Ticket.priority)

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "priority": row.priority.value,
                "total": row.total,
                "response_met": row.response_met or 0,
                "resolution_met": row.resolution_met or 0,
                "response_breached": row.response_breached or 0,
                "resolution_breached": row.resolution_breached or 0,
                "compliance_percent": round(
                    ((row.resolution_met or 0) / row.total * 100), 2
                )
                if row.total > 0
                else 100.0,
            }
            for row in rows
        ]

    # ------------------------------------------------------------------ #
    #  Mean Time to Resolve (MTTR)
    # ------------------------------------------------------------------ #

    async def get_mttr(
        self,
        project_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        granularity: str = "day",
    ) -> list[dict]:
        """
        Return mean time to resolve grouped by day, week, or month.

        granularity: 'day' | 'week' | 'month'
        """
        conditions = self._base_conditions(project_id, date_from, date_to)
        conditions.append(Ticket.resolved_at.isnot(None))

        # Determine the grouping expression
        if granularity == "week":
            period_expr = func.yearweek(Ticket.resolved_at)
        elif granularity == "month":
            period_expr = func.date_format(Ticket.resolved_at, "%Y-%m")
        else:  # day
            period_expr = func.date(Ticket.resolved_at)

        stmt = (
            select(
                period_expr.label("period"),
                func.avg(SLARecord.actual_resolution_minutes).label("avg_minutes"),
                func.count(Ticket.id).label("ticket_count"),
            )
            .join(SLARecord, SLARecord.ticket_id == Ticket.id)
            .where(and_(*conditions))
            .group_by(period_expr)
            .order_by(period_expr)
        )

        result = await self.db.execute(stmt)
        return [
            {
                "period": str(row.period),
                "avg_resolution_minutes": round(float(row.avg_minutes or 0), 2),
                "ticket_count": row.ticket_count,
            }
            for row in result.all()
        ]

    # ------------------------------------------------------------------ #
    #  Engineer performance
    # ------------------------------------------------------------------ #

    async def get_engineer_performance(
        self,
        project_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        """
        Return per-engineer metrics: assigned count, resolved count,
        avg resolution time, SLA compliance.
        """
        conditions = self._base_conditions(project_id, date_from, date_to)
        conditions.append(Ticket.assignee_id.isnot(None))

        stmt = (
            select(
                Ticket.assignee_id,
                User.first_name,
                User.last_name,
                User.email,
                func.count(Ticket.id).label("assigned_count"),
                func.sum(
                    case(
                        (Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED]), 1),
                        else_=0,
                    )
                ).label("resolved_count"),
                func.avg(SLARecord.actual_resolution_minutes).label("avg_resolution_minutes"),
                func.sum(
                    case((SLARecord.resolution_met == True, 1), else_=0)
                ).label("sla_met"),
            )
            .join(User, User.id == Ticket.assignee_id)
            .outerjoin(SLARecord, SLARecord.ticket_id == Ticket.id)
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.group_by(
            Ticket.assignee_id, User.first_name, User.last_name, User.email
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "user_id": row.assignee_id,
                "name": f"{row.first_name} {row.last_name}",
                "email": row.email,
                "assigned_count": row.assigned_count,
                "resolved_count": row.resolved_count or 0,
                "avg_resolution_minutes": round(float(row.avg_resolution_minutes or 0), 2),
                "sla_compliance_percent": round(
                    ((row.sla_met or 0) / row.assigned_count * 100), 2
                )
                if row.assigned_count > 0
                else 100.0,
            }
            for row in rows
        ]

    # ------------------------------------------------------------------ #
    #  Team performance
    # ------------------------------------------------------------------ #

    async def get_team_performance(
        self,
        project_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[dict]:
        """
        Return per-team metrics: assigned count, resolved count,
        avg resolution time, SLA compliance.
        """
        conditions = self._base_conditions(project_id, date_from, date_to)
        conditions.append(Ticket.team_id.isnot(None))

        stmt = (
            select(
                Ticket.team_id,
                Team.name.label("team_name"),
                func.count(Ticket.id).label("assigned_count"),
                func.sum(
                    case(
                        (Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED]), 1),
                        else_=0,
                    )
                ).label("resolved_count"),
                func.avg(SLARecord.actual_resolution_minutes).label("avg_resolution_minutes"),
                func.sum(
                    case((SLARecord.resolution_met == True, 1), else_=0)
                ).label("sla_met"),
            )
            .join(Team, Team.id == Ticket.team_id)
            .outerjoin(SLARecord, SLARecord.ticket_id == Ticket.id)
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.group_by(Ticket.team_id, Team.name)

        result = await self.db.execute(stmt)
        rows = result.all()

        return [
            {
                "team_id": row.team_id,
                "team_name": row.team_name,
                "assigned_count": row.assigned_count,
                "resolved_count": row.resolved_count or 0,
                "avg_resolution_minutes": round(float(row.avg_resolution_minutes or 0), 2),
                "sla_compliance_percent": round(
                    ((row.sla_met or 0) / row.assigned_count * 100), 2
                )
                if row.assigned_count > 0
                else 100.0,
            }
            for row in rows
        ]
