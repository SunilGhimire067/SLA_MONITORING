from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.constants import AuditAction
from app.models.sla import SLAPolicy, SLARecord
from app.models.ticket import Ticket


class SLAService:
    """
    Critical SLA management service handling policy CRUD, SLA record
    lifecycle, compliance checking, and breach scanning.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Policy CRUD
    # ------------------------------------------------------------------ #

    async def get_policies(
        self, project_id: Optional[int] = None
    ) -> list[SLAPolicy]:
        """Retrieve SLA policies with optional project filtering."""
        stmt = select(SLAPolicy).options(joinedload(SLAPolicy.project))
        if project_id is not None:
            stmt = stmt.where(SLAPolicy.project_id == project_id)
        stmt = stmt.order_by(SLAPolicy.priority, SLAPolicy.name)

        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_policy(self, policy_id: int) -> SLAPolicy:
        """
        Retrieve a single SLA policy by ID.

        Raises HTTP 404 if not found.
        """
        stmt = (
            select(SLAPolicy)
            .options(joinedload(SLAPolicy.project))
            .where(SLAPolicy.id == policy_id)
        )
        result = await self.db.execute(stmt)
        policy = result.scalar_one_or_none()

        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SLA policy with id {policy_id} not found",
            )
        return policy

    async def create_policy(self, data) -> SLAPolicy:
        """Create a new SLA policy."""
        policy = SLAPolicy(
            name=data.name,
            priority=data.priority,
            project_id=getattr(data, "project_id", None),
            response_time_minutes=data.response_time_minutes,
            resolution_time_minutes=data.resolution_time_minutes,
            is_default=getattr(data, "is_default", False),
            is_active=getattr(data, "is_active", True),
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def update_policy(self, policy_id: int, data) -> SLAPolicy:
        """Update an existing SLA policy."""
        policy = await self.get_policy(policy_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)

        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    # ------------------------------------------------------------------ #
    #  Policy matching
    # ------------------------------------------------------------------ #

    async def find_matching_policy(
        self, priority, project_id: Optional[int] = None
    ) -> Optional[SLAPolicy]:
        """
        Find the best-matching active SLA policy for a given priority.

        Resolution order:
          1. Project-specific policy matching priority.
          2. Default policy matching priority.
          3. None if no policy exists.
        """
        # Try project-specific first
        if project_id is not None:
            stmt = select(SLAPolicy).where(
                SLAPolicy.priority == priority,
                SLAPolicy.project_id == project_id,
                SLAPolicy.is_active == True,
            )
            result = await self.db.execute(stmt)
            policy = result.scalar_one_or_none()
            if policy is not None:
                return policy

        # Fall back to default policy
        stmt = select(SLAPolicy).where(
            SLAPolicy.priority == priority,
            SLAPolicy.is_default == True,
            SLAPolicy.is_active == True,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------ #
    #  SLA record creation
    # ------------------------------------------------------------------ #

    async def create_sla_record(self, ticket: Ticket) -> Optional[SLARecord]:
        """
        Create an SLA record for a newly created ticket.

        Computes response_deadline and resolution_deadline based on the
        matching SLA policy's time allowances from the current time.

        Returns None if no matching policy is found.
        """
        policy = await self.find_matching_policy(
            priority=ticket.priority,
            project_id=ticket.project_id,
        )
        if policy is None:
            return None

        now = datetime.now(timezone.utc)
        record = SLARecord(
            ticket_id=ticket.id,
            sla_policy_id=policy.id,
            response_deadline=now + timedelta(minutes=policy.response_time_minutes),
            resolution_deadline=now + timedelta(minutes=policy.resolution_time_minutes),
            # response_met and resolution_met remain None (pending)
        )
        self.db.add(record)
        await self.db.flush()
        return record

    # ------------------------------------------------------------------ #
    #  SLA compliance checks
    # ------------------------------------------------------------------ #

    async def check_response_sla(self, ticket: Ticket) -> None:
        """
        Evaluate whether the response SLA was met.

        Sets response_met to True/False and records actual_response_minutes
        on the ticket's SLA record.
        """
        if ticket.sla_record is None:
            return
        if ticket.first_response_at is None:
            return

        record = ticket.sla_record
        record.actual_response_minutes = int(
            (ticket.first_response_at - ticket.created_at).total_seconds() / 60
        )
        record.response_met = ticket.first_response_at <= record.response_deadline

    async def check_resolution_sla(self, ticket: Ticket) -> None:
        """
        Evaluate whether the resolution SLA was met.

        Sets resolution_met to True/False and records actual_resolution_minutes
        on the ticket's SLA record.
        """
        if ticket.sla_record is None:
            # Lazy-load SLA record if not already present
            stmt = select(SLARecord).where(SLARecord.ticket_id == ticket.id)
            result = await self.db.execute(stmt)
            sla_record = result.scalar_one_or_none()
            if sla_record is None:
                return
        else:
            sla_record = ticket.sla_record

        if ticket.resolved_at is None:
            return

        sla_record.actual_resolution_minutes = int(
            (ticket.resolved_at - ticket.created_at).total_seconds() / 60
        )
        sla_record.resolution_met = ticket.resolved_at <= sla_record.resolution_deadline

    # ------------------------------------------------------------------ #
    #  Breach scanning (called by scheduled task / Celery beat)
    # ------------------------------------------------------------------ #

    async def scan_for_breaches(self) -> list[SLARecord]:
        """
        Scan for SLA records that have breached their deadlines.

        A record is considered breached if:
          - response_met is None AND response_deadline < now, OR
          - resolution_met is None AND resolution_deadline < now.

        Marks matching records as breached and returns the list.
        """
        now = datetime.now(timezone.utc)

        stmt = (
            select(SLARecord)
            .options(joinedload(SLARecord.ticket))
            .where(
                or_(
                    and_(
                        SLARecord.response_met.is_(None),
                        SLARecord.response_deadline < now,
                    ),
                    and_(
                        SLARecord.resolution_met.is_(None),
                        SLARecord.resolution_deadline < now,
                    ),
                )
            )
        )
        result = await self.db.execute(stmt)
        records = list(result.scalars().unique().all())

        for record in records:
            if record.response_met is None and record.response_deadline < now:
                record.response_met = False
                record.response_breached_at = now

            if record.resolution_met is None and record.resolution_deadline < now:
                record.resolution_met = False
                record.resolution_breached_at = now

        await self.db.commit()
        return records

    # ------------------------------------------------------------------ #
    #  Breached records query
    # ------------------------------------------------------------------ #

    async def get_breached_records(
        self,
        project_id: Optional[int] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SLARecord]:
        """
        Retrieve SLA records that have been breached, with optional filtering.
        """
        stmt = (
            select(SLARecord)
            .join(SLARecord.ticket)
            .options(
                joinedload(SLARecord.ticket).joinedload(Ticket.project),
                joinedload(SLARecord.sla_policy),
            )
            .where(
                or_(
                    SLARecord.response_met == False,
                    SLARecord.resolution_met == False,
                )
            )
        )

        if project_id is not None:
            stmt = stmt.where(Ticket.project_id == project_id)
        if priority is not None:
            stmt = stmt.where(Ticket.priority == priority)

        stmt = (
            stmt.order_by(SLARecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())
