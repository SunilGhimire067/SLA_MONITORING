import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.constants import (
    NotificationType,
    NotificationChannel,
    AuditAction,
)
from app.models.notification import EscalationRule
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)


class EscalationService:
    """
    Manages escalation rules and executes escalation logic --
    reassigning tickets and dispatching notifications when SLA thresholds
    are breached.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    #  Rule CRUD
    # ------------------------------------------------------------------ #

    async def get_rules(self) -> list[EscalationRule]:
        """Retrieve all escalation rules with related entities."""
        stmt = (
            select(EscalationRule)
            .options(
                joinedload(EscalationRule.project),
                joinedload(EscalationRule.escalate_to_user),
                joinedload(EscalationRule.escalate_to_team),
            )
            .order_by(EscalationRule.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def create_rule(self, data) -> EscalationRule:
        """Create a new escalation rule."""
        rule = EscalationRule(
            name=data.name,
            project_id=getattr(data, "project_id", None),
            priority=getattr(data, "priority", None),
            trigger_type=data.trigger_type,
            trigger_threshold_minutes=getattr(data, "trigger_threshold_minutes", 0),
            escalate_to_user_id=getattr(data, "escalate_to_user_id", None),
            escalate_to_team_id=getattr(data, "escalate_to_team_id", None),
            notify_channels=getattr(data, "notify_channels", None),
            is_active=getattr(data, "is_active", True),
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def update_rule(self, rule_id: int, data) -> EscalationRule:
        """Update an existing escalation rule."""
        rule = await self._get_rule(rule_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: int) -> None:
        """
        Delete an escalation rule.

        Raises HTTP 404 if the rule does not exist.
        """
        rule = await self._get_rule(rule_id)
        await self.db.delete(rule)
        await self.db.commit()

    async def _get_rule(self, rule_id: int) -> EscalationRule:
        """Internal helper to fetch a rule or raise 404."""
        stmt = select(EscalationRule).where(EscalationRule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        if rule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Escalation rule with id {rule_id} not found",
            )
        return rule

    # ------------------------------------------------------------------ #
    #  Escalation execution
    # ------------------------------------------------------------------ #

    async def process_escalation(self, ticket_id: int) -> None:
        """
        Process escalation for a ticket.

        1. Load the ticket.
        2. Find all active escalation rules matching the ticket's
           priority and project.
        3. For each matching rule:
           a. Reassign the ticket if the rule specifies a user or team.
           b. Send notifications through the channels defined in the rule.
        """
        from app.services.notification_service import NotificationService
        from app.services.audit_service import AuditService

        # Load ticket
        ticket_stmt = (
            select(Ticket)
            .options(joinedload(Ticket.project))
            .where(Ticket.id == ticket_id)
        )
        ticket_result = await self.db.execute(ticket_stmt)
        ticket = ticket_result.scalar_one_or_none()

        if ticket is None:
            logger.warning("Escalation: ticket %d not found", ticket_id)
            return

        # Find matching rules
        conditions = [
            EscalationRule.is_active == True,
        ]
        # Rules can be project-specific or global (project_id IS NULL)
        if ticket.project_id is not None:
            conditions.append(
                EscalationRule.project_id.in_([ticket.project_id, None])
            )

        # Rules can target a specific priority or any (priority IS NULL)
        if ticket.priority is not None:
            conditions.append(
                EscalationRule.priority.in_([ticket.priority, None])
            )

        rules_stmt = (
            select(EscalationRule)
            .options(
                joinedload(EscalationRule.escalate_to_user),
                joinedload(EscalationRule.escalate_to_team),
            )
            .where(and_(*conditions))
        )
        rules_result = await self.db.execute(rules_stmt)
        rules = rules_result.scalars().unique().all()

        if not rules:
            logger.info("No escalation rules matched for ticket %s", ticket.ticket_number)
            return

        notification_service = NotificationService(self.db)
        audit_service = AuditService(self.db)

        for rule in rules:
            old_assignee_id = ticket.assignee_id
            old_team_id = ticket.team_id

            # Reassign ticket
            if rule.escalate_to_user_id is not None:
                ticket.assignee_id = rule.escalate_to_user_id
            if rule.escalate_to_team_id is not None:
                ticket.team_id = rule.escalate_to_team_id

            # Audit the escalation
            await audit_service.log(
                user_id=None,  # System-initiated
                entity_type="ticket",
                entity_id=ticket.id,
                action=AuditAction.ESCALATION,
                old_values={
                    "assignee_id": old_assignee_id,
                    "team_id": old_team_id,
                },
                new_values={
                    "assignee_id": ticket.assignee_id,
                    "team_id": ticket.team_id,
                    "escalation_rule": rule.name,
                },
            )

            # Send notifications through configured channels
            channels = rule.notify_channels or []
            notification_title = f"Escalation: {ticket.ticket_number} - {ticket.title}"
            notification_message = (
                f"Ticket {ticket.ticket_number} has been escalated "
                f"per rule '{rule.name}'."
            )

            for channel_name in channels:
                if channel_name == NotificationChannel.EMAIL.value:
                    # Send email to the escalation target user
                    if rule.escalate_to_user and rule.escalate_to_user.email:
                        await notification_service.send_email_notification(
                            to_email=rule.escalate_to_user.email,
                            subject=notification_title,
                            body=notification_message,
                        )

                elif channel_name == NotificationChannel.TEAMS.value:
                    await notification_service.send_teams_notification(
                        title=notification_title,
                        message=notification_message,
                    )

                # Always create an in-app notification for the target user
                if rule.escalate_to_user_id is not None:
                    await notification_service.create_notification(
                        user_id=rule.escalate_to_user_id,
                        ticket_id=ticket.id,
                        type=NotificationType.ESCALATION,
                        channel=NotificationChannel.IN_APP,
                        title=notification_title,
                        message=notification_message,
                    )

        await self.db.commit()
        logger.info(
            "Escalation processed for ticket %s: %d rules applied",
            ticket.ticket_number,
            len(rules),
        )
