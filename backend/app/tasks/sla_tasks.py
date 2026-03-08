import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.tasks.celery_app import celery_app
from app.models.sla import SLARecord
from app.models.ticket import Ticket
from app.core.constants import TicketStatus

logger = logging.getLogger(__name__)

# Sync engine for Celery tasks
sync_url = settings.DATABASE_URL.replace("+aiomysql", "+mysqldb")
sync_engine = create_engine(sync_url)
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task(name="app.tasks.sla_tasks.scan_sla_breaches")
def scan_sla_breaches():
    """Runs every minute. Checks all open tickets for SLA breaches."""
    now = datetime.now(timezone.utc)
    breached_count = 0

    with SyncSession() as db:
        # Find response breaches (no first response and past deadline)
        response_breaches = db.execute(
            select(SLARecord).join(Ticket).where(
                and_(
                    SLARecord.response_met.is_(None),
                    SLARecord.response_deadline < now,
                    Ticket.status.notin_([TicketStatus.CLOSED, TicketStatus.RESOLVED]),
                )
            )
        ).scalars().all()

        for record in response_breaches:
            record.response_met = False
            record.response_breached_at = now
            breached_count += 1
            logger.warning(f"SLA Response BREACH: ticket_id={record.ticket_id}")

            # Trigger escalation
            from app.tasks.escalation_tasks import process_escalation
            process_escalation.delay(record.ticket_id, "response_breach")

        # Find resolution breaches
        resolution_breaches = db.execute(
            select(SLARecord).join(Ticket).where(
                and_(
                    SLARecord.resolution_met.is_(None),
                    SLARecord.resolution_deadline < now,
                    Ticket.status.notin_([TicketStatus.CLOSED, TicketStatus.RESOLVED]),
                )
            )
        ).scalars().all()

        for record in resolution_breaches:
            record.resolution_met = False
            record.resolution_breached_at = now
            breached_count += 1
            logger.warning(f"SLA Resolution BREACH: ticket_id={record.ticket_id}")

            from app.tasks.escalation_tasks import process_escalation
            process_escalation.delay(record.ticket_id, "resolution_breach")

        db.commit()

    return f"Scanned. Found {breached_count} new breaches."


@celery_app.task(name="app.tasks.sla_tasks.send_sla_warnings")
def send_sla_warnings():
    """Runs every 5 minutes. Warns about tickets approaching SLA deadline."""
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    warning_window = now + timedelta(minutes=15)  # 15-minute warning
    warning_count = 0

    with SyncSession() as db:
        # Find tickets approaching response deadline
        approaching = db.execute(
            select(SLARecord).join(Ticket).where(
                and_(
                    SLARecord.response_met.is_(None),
                    SLARecord.response_deadline > now,
                    SLARecord.response_deadline <= warning_window,
                    Ticket.status.notin_([TicketStatus.CLOSED, TicketStatus.RESOLVED]),
                )
            )
        ).scalars().all()

        for record in approaching:
            warning_count += 1
            logger.info(f"SLA Warning: ticket_id={record.ticket_id} approaching response deadline")

            from app.tasks.notification_tasks import send_sla_warning_notification
            send_sla_warning_notification.delay(record.ticket_id, "response")

    return f"Sent {warning_count} SLA warnings."
