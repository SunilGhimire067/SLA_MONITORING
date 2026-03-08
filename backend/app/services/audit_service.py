import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AuditAction
from app.models.audit import AuditLog


class AuditService:
    """
    Immutable audit trail service for recording and querying all entity
    changes, user actions, and system events.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Write
    # ------------------------------------------------------------------ #

    async def log(
        self,
        user_id: Optional[int],
        entity_type: str,
        entity_id: int,
        action: AuditAction,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.

        Parameters:
            user_id:     ID of the acting user (None for system-initiated actions).
            entity_type: Logical entity name, e.g. 'ticket', 'user', 'project'.
            entity_id:   Primary key of the affected entity.
            action:      The type of action performed.
            old_values:  JSON-serializable dict of previous field values.
            new_values:  JSON-serializable dict of updated field values.
            ip_address:  Client IP address (optional).
            user_agent:  Client User-Agent header (optional).
        """
        entry = AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    # ------------------------------------------------------------------ #
    #  Read (paginated)
    # ------------------------------------------------------------------ #

    async def get_logs(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: Optional[AuditAction] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """
        Retrieve paginated audit logs with optional filtering.

        Returns (log_list, total_count).
        """
        conditions = []
        if entity_type is not None:
            conditions.append(AuditLog.entity_type == entity_type)
        if entity_id is not None:
            conditions.append(AuditLog.entity_id == entity_id)
        if user_id is not None:
            conditions.append(AuditLog.user_id == user_id)
        if action is not None:
            conditions.append(AuditLog.action == action)
        if date_from is not None:
            conditions.append(AuditLog.created_at >= date_from)
        if date_to is not None:
            conditions.append(AuditLog.created_at <= date_to)

        # Count
        count_stmt = select(func.count(AuditLog.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()

        # Data
        stmt = select(AuditLog)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        logs = result.scalars().all()

        return list(logs), total

    # ------------------------------------------------------------------ #
    #  Entity history
    # ------------------------------------------------------------------ #

    async def get_entity_history(
        self, entity_type: str, entity_id: int
    ) -> list[AuditLog]:
        """
        Retrieve the full audit history for a specific entity,
        ordered from oldest to newest.
        """
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------ #
    #  Export
    # ------------------------------------------------------------------ #

    async def export_report(
        self,
        report_type: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        format: str = "json",
    ) -> dict:
        """
        Generate an audit report export.

        Returns a dict with an export_id and metadata. The actual file
        generation is intended to be handled asynchronously (e.g. via Celery).

        Parameters:
            report_type: Type of report, e.g. 'full', 'ticket_changes', 'login_activity'.
            date_from:   Start of the reporting period.
            date_to:     End of the reporting period.
            format:      Output format -- 'json' or 'csv'.
        """
        conditions = []
        if date_from is not None:
            conditions.append(AuditLog.created_at >= date_from)
        if date_to is not None:
            conditions.append(AuditLog.created_at <= date_to)

        # Apply report-type-specific filters
        if report_type == "ticket_changes":
            conditions.append(AuditLog.entity_type == "ticket")
        elif report_type == "login_activity":
            conditions.append(AuditLog.action.in_([AuditAction.LOGIN, AuditAction.LOGOUT]))

        # Count records for the report
        count_stmt = select(func.count(AuditLog.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        record_count = count_result.scalar()

        export_id = str(uuid.uuid4())

        return {
            "export_id": export_id,
            "report_type": report_type,
            "format": format,
            "record_count": record_count,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "status": "pending",
        }
