import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.tasks.celery_app import celery_app
from app.models.ticket import Ticket
from app.models.notification import EscalationRule, Notification
from app.models.audit import AuditLog
from app.core.constants import TriggerType, NotificationType, NotificationChannel, AuditAction

logger = logging.getLogger(__name__)

sync_url = settings.DATABASE_URL.replace("+aiomysql", "+mysqldb")
sync_engine = create_engine(sync_url)
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task(name="app.tasks.escalation_tasks.process_escalation")
def process_escalation(ticket_id: int, breach_type: str):
    """Process escalation rules for a breached ticket."""
    with SyncSession() as db:
        ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()
        if not ticket:
            return

        # Map breach type to trigger type
        trigger_map = {
            "response_breach": TriggerType.RESPONSE_BREACH,
            "resolution_breach": TriggerType.RESOLUTION_BREACH,
        }
        trigger = trigger_map.get(breach_type)
        if not trigger:
            return

        # Find matching escalation rules
        rules = db.execute(
            select(EscalationRule).where(
                and_(
                    EscalationRule.is_active.is_(True),
                    EscalationRule.trigger_type == trigger,
                    (EscalationRule.project_id == ticket.project_id) | (EscalationRule.project_id.is_(None)),
                    (EscalationRule.priority == ticket.priority) | (EscalationRule.priority.is_(None)),
                )
            )
        ).scalars().all()

        for rule in rules:
            logger.info(f"Executing escalation rule '{rule.name}' for ticket {ticket.ticket_number}")

            # Auto-reassign if configured
            old_assignee = ticket.assignee_id
            if rule.escalate_to_user_id:
                ticket.assignee_id = rule.escalate_to_user_id

                # Audit log for reassignment
                audit = AuditLog(
                    entity_type="ticket",
                    entity_id=ticket.id,
                    action=AuditAction.ESCALATION,
                    old_values={"assignee_id": old_assignee},
                    new_values={"assignee_id": rule.escalate_to_user_id, "reason": f"Escalation: {rule.name}"},
                    created_at=datetime.now(timezone.utc),
                )
                db.add(audit)

            # Create in-app notification for escalation target
            target_user_id = rule.escalate_to_user_id or (old_assignee if old_assignee else None)
            if target_user_id:
                notification = Notification(
                    user_id=target_user_id,
                    ticket_id=ticket_id,
                    type=NotificationType.ESCALATION,
                    channel=NotificationChannel.IN_APP,
                    title=f"Escalation - {ticket.ticket_number}",
                    message=f"Ticket {ticket.ticket_number} has been escalated due to {breach_type.replace('_', ' ')}. "
                            f"Rule: {rule.name}",
                    created_at=datetime.now(timezone.utc),
                )
                db.add(notification)

            # Send notifications via configured channels
            if rule.notify_channels:
                from app.tasks.notification_tasks import send_breach_notification
                send_breach_notification.delay(ticket_id, breach_type)

        db.commit()

    return f"Processed {len(rules)} escalation rules for ticket {ticket_id}"
