import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.tasks.celery_app import celery_app
from app.models.notification import Notification
from app.models.ticket import Ticket
from app.core.constants import NotificationType, NotificationChannel

logger = logging.getLogger(__name__)

sync_url = settings.DATABASE_URL.replace("+aiomysql", "+mysqldb")
sync_engine = create_engine(sync_url)
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task(name="app.tasks.notification_tasks.send_breach_notification")
def send_breach_notification(ticket_id: int, breach_type: str):
    """Send notification when SLA is breached."""
    with SyncSession() as db:
        ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()
        if not ticket:
            return

        # Notify assignee
        if ticket.assignee_id:
            notification = Notification(
                user_id=ticket.assignee_id,
                ticket_id=ticket_id,
                type=NotificationType.SLA_BREACH,
                channel=NotificationChannel.IN_APP,
                title=f"SLA {breach_type.replace('_', ' ').title()} - {ticket.ticket_number}",
                message=f"The {breach_type.replace('_', ' ')} SLA for ticket {ticket.ticket_number} "
                        f"'{ticket.title}' has been breached.",
                created_at=datetime.now(timezone.utc),
            )
            db.add(notification)

        # Try to send email if configured
        if settings.SMTP_HOST:
            try:
                _send_email_notification(ticket, breach_type)
            except Exception as e:
                logger.error(f"Failed to send email for ticket {ticket_id}: {e}")

        # Try to send Teams notification if configured
        if settings.TEAMS_WEBHOOK_URL:
            try:
                _send_teams_notification(ticket, breach_type)
            except Exception as e:
                logger.error(f"Failed to send Teams notification for ticket {ticket_id}: {e}")

        db.commit()

    return f"Breach notification sent for ticket {ticket_id}"


@celery_app.task(name="app.tasks.notification_tasks.send_sla_warning_notification")
def send_sla_warning_notification(ticket_id: int, warning_type: str):
    """Send warning notification when ticket is approaching SLA deadline."""
    with SyncSession() as db:
        ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()
        if not ticket:
            return

        if ticket.assignee_id:
            notification = Notification(
                user_id=ticket.assignee_id,
                ticket_id=ticket_id,
                type=NotificationType.SLA_WARNING,
                channel=NotificationChannel.IN_APP,
                title=f"SLA Warning - {ticket.ticket_number}",
                message=f"Ticket {ticket.ticket_number} is approaching its {warning_type} SLA deadline.",
                created_at=datetime.now(timezone.utc),
            )
            db.add(notification)
            db.commit()

    return f"Warning notification sent for ticket {ticket_id}"


@celery_app.task(name="app.tasks.notification_tasks.send_assignment_notification")
def send_assignment_notification(ticket_id: int, assignee_id: int):
    """Send notification when a ticket is assigned."""
    with SyncSession() as db:
        ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()
        if not ticket:
            return

        notification = Notification(
            user_id=assignee_id,
            ticket_id=ticket_id,
            type=NotificationType.ASSIGNMENT,
            channel=NotificationChannel.IN_APP,
            title=f"New Assignment - {ticket.ticket_number}",
            message=f"You have been assigned ticket {ticket.ticket_number}: '{ticket.title}'",
            created_at=datetime.now(timezone.utc),
        )
        db.add(notification)
        db.commit()

    return f"Assignment notification sent for ticket {ticket_id}"


def _send_email_notification(ticket, breach_type: str):
    """Send email notification (placeholder - implement with aiosmtplib)."""
    import smtplib
    from email.mime.text import MIMEText

    if not settings.SMTP_HOST:
        return

    msg = MIMEText(
        f"SLA {breach_type.replace('_', ' ').title()} Alert\n\n"
        f"Ticket: {ticket.ticket_number}\n"
        f"Title: {ticket.title}\n"
        f"Priority: {ticket.priority.value}\n"
        f"Status: {ticket.status.value}\n"
    )
    msg["Subject"] = f"[SLA BREACH] {ticket.ticket_number}: {ticket.title}"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = settings.SMTP_USER

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


def _send_teams_notification(ticket, breach_type: str):
    """Send MS Teams webhook notification."""
    import httpx

    if not settings.TEAMS_WEBHOOK_URL:
        return

    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {"type": "TextBlock", "size": "large", "weight": "bolder",
                     "text": f"SLA {breach_type.replace('_', ' ').title()} Alert"},
                    {"type": "TextBlock",
                     "text": f"**{ticket.ticket_number}**: {ticket.title}"},
                    {"type": "FactSet", "facts": [
                        {"title": "Priority", "value": ticket.priority.value},
                        {"title": "Status", "value": ticket.status.value},
                        {"title": "Breach Type", "value": breach_type.replace("_", " ").title()},
                    ]},
                ],
            },
        }],
    }

    httpx.post(settings.TEAMS_WEBHOOK_URL, json=card, timeout=10)
