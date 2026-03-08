from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.constants import TicketStatus, VALID_TRANSITIONS, AuditAction
from app.models.project import Project
from app.models.ticket import Ticket
from app.models.audit import AuditLog


class TicketService:
    """
    Core ticket management service handling CRUD, status transitions,
    assignment, and integration with SLA and audit subsystems.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Ticket number generation
    # ------------------------------------------------------------------ #

    async def _generate_ticket_number(self, project_id: int) -> str:
        """
        Generate the next sequential ticket number for a project.

        Format: PROJKEY-001, PROJKEY-002, etc.
        """
        # Fetch the project key
        project_stmt = select(Project.key).where(Project.id == project_id)
        project_result = await self.db.execute(project_stmt)
        project_key = project_result.scalar_one_or_none()

        if project_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found",
            )

        # Count existing tickets for this project
        count_stmt = select(func.count(Ticket.id)).where(
            Ticket.project_id == project_id
        )
        count_result = await self.db.execute(count_stmt)
        count = count_result.scalar()

        next_number = (count or 0) + 1
        return f"{project_key}-{next_number:03d}"

    # ------------------------------------------------------------------ #
    #  Create
    # ------------------------------------------------------------------ #

    async def create_ticket(self, data, reporter_id: int) -> Ticket:
        """
        Create a new ticket.

        Steps:
          1. Generate a sequential ticket number from the project key.
          2. Persist the ticket.
          3. Auto-create an SLA record via SLAService.
          4. Write an audit log entry.
        """
        from app.services.sla_service import SLAService
        from app.services.audit_service import AuditService

        ticket_number = await self._generate_ticket_number(data.project_id)

        ticket = Ticket(
            ticket_number=ticket_number,
            project_id=data.project_id,
            title=data.title,
            description=getattr(data, "description", None),
            priority=data.priority,
            status=TicketStatus.OPEN,
            reporter_id=reporter_id,
            assignee_id=getattr(data, "assignee_id", None),
            team_id=getattr(data, "team_id", None),
            tags=getattr(data, "tags", None),
        )
        self.db.add(ticket)
        await self.db.flush()  # Get the ticket.id without committing

        # Auto-create SLA record
        sla_service = SLAService(self.db)
        await sla_service.create_sla_record(ticket)

        # Audit log
        audit_service = AuditService(self.db)
        await audit_service.log(
            user_id=reporter_id,
            entity_type="ticket",
            entity_id=ticket.id,
            action=AuditAction.CREATE,
            new_values={
                "ticket_number": ticket_number,
                "title": ticket.title,
                "priority": ticket.priority.value if ticket.priority else None,
                "status": ticket.status.value,
            },
        )

        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    # ------------------------------------------------------------------ #
    #  Read (list + detail)
    # ------------------------------------------------------------------ #

    async def get_tickets(
        self,
        project_id: Optional[int] = None,
        status_filter: Optional[TicketStatus] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[int] = None,
        team_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Ticket], int]:
        """
        Retrieve a paginated, filtered list of tickets.

        Returns (ticket_list, total_count).
        """
        conditions = []
        if project_id is not None:
            conditions.append(Ticket.project_id == project_id)
        if status_filter is not None:
            conditions.append(Ticket.status == status_filter)
        if priority is not None:
            conditions.append(Ticket.priority == priority)
        if assignee_id is not None:
            conditions.append(Ticket.assignee_id == assignee_id)
        if team_id is not None:
            conditions.append(Ticket.team_id == team_id)

        # Total count
        count_stmt = select(func.count(Ticket.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # Data query with eager-loaded relationships
        stmt = (
            select(Ticket)
            .options(
                joinedload(Ticket.project),
                joinedload(Ticket.reporter),
                joinedload(Ticket.assignee),
                joinedload(Ticket.team),
            )
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Ticket.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        tickets = result.scalars().unique().all()

        return list(tickets), total

    async def get_ticket(self, ticket_id: int) -> Ticket:
        """
        Retrieve a single ticket by ID with all related entities eagerly loaded.

        Raises HTTP 404 if the ticket does not exist.
        """
        stmt = (
            select(Ticket)
            .options(
                joinedload(Ticket.project),
                joinedload(Ticket.reporter),
                joinedload(Ticket.assignee),
                joinedload(Ticket.team),
                joinedload(Ticket.sla_record),
                selectinload(Ticket.comments),
            )
            .where(Ticket.id == ticket_id)
        )
        result = await self.db.execute(stmt)
        ticket = result.scalar_one_or_none()

        if ticket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with id {ticket_id} not found",
            )
        return ticket

    # ------------------------------------------------------------------ #
    #  Update
    # ------------------------------------------------------------------ #

    async def update_ticket(self, ticket_id: int, data, user_id: int) -> Ticket:
        """
        Update a ticket's mutable fields and record the change in the audit log.
        """
        from app.services.audit_service import AuditService

        ticket = await self.get_ticket(ticket_id)

        update_data = data.model_dump(exclude_unset=True)
        old_values = {}
        new_values = {}

        for field, value in update_data.items():
            old_val = getattr(ticket, field, None)
            if old_val != value:
                # Store serializable representation
                old_values[field] = old_val.value if hasattr(old_val, "value") else old_val
                new_values[field] = value.value if hasattr(value, "value") else value
                setattr(ticket, field, value)

        if new_values:
            audit_service = AuditService(self.db)
            await audit_service.log(
                user_id=user_id,
                entity_type="ticket",
                entity_id=ticket.id,
                action=AuditAction.UPDATE,
                old_values=old_values,
                new_values=new_values,
            )

        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    # ------------------------------------------------------------------ #
    #  Status transitions
    # ------------------------------------------------------------------ #

    async def transition_status(
        self, ticket_id: int, new_status: TicketStatus, user_id: int
    ) -> Ticket:
        """
        Transition a ticket to a new status while enforcing the state machine.

        Side-effects:
          - Sets resolved_at when transitioning to RESOLVED.
          - Sets closed_at when transitioning to CLOSED.
          - Clears resolved_at when reopening from RESOLVED.
          - Checks resolution SLA when resolving.
          - Creates an audit log entry.
        """
        from app.services.sla_service import SLAService
        from app.services.audit_service import AuditService

        ticket = await self.get_ticket(ticket_id)
        old_status = ticket.status

        # Enforce valid transitions
        allowed = VALID_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid transition from '{old_status.value}' to '{new_status.value}'. "
                    f"Allowed transitions: {[s.value for s in allowed]}"
                ),
            )

        now = datetime.now(timezone.utc)
        ticket.status = new_status

        # Side-effects based on target status
        if new_status == TicketStatus.RESOLVED:
            ticket.resolved_at = now
            # Check resolution SLA
            sla_service = SLAService(self.db)
            await sla_service.check_resolution_sla(ticket)

        elif new_status == TicketStatus.CLOSED:
            ticket.closed_at = now

        # If reopening from resolved, clear resolution timestamp
        if old_status == TicketStatus.RESOLVED and new_status in (
            TicketStatus.IN_PROGRESS,
            TicketStatus.OPEN,
        ):
            ticket.resolved_at = None

        # Audit log
        audit_service = AuditService(self.db)
        await audit_service.log(
            user_id=user_id,
            entity_type="ticket",
            entity_id=ticket.id,
            action=AuditAction.STATUS_CHANGE,
            old_values={"status": old_status.value},
            new_values={"status": new_status.value},
        )

        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    # ------------------------------------------------------------------ #
    #  Assignment
    # ------------------------------------------------------------------ #

    async def assign_ticket(
        self, ticket_id: int, assignee_id: Optional[int], user_id: int
    ) -> Ticket:
        """
        Assign (or unassign) a ticket and create an audit log entry.
        """
        from app.services.audit_service import AuditService

        ticket = await self.get_ticket(ticket_id)
        old_assignee_id = ticket.assignee_id
        ticket.assignee_id = assignee_id

        audit_service = AuditService(self.db)
        await audit_service.log(
            user_id=user_id,
            entity_type="ticket",
            entity_id=ticket.id,
            action=AuditAction.ASSIGN,
            old_values={"assignee_id": old_assignee_id},
            new_values={"assignee_id": assignee_id},
        )

        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket
