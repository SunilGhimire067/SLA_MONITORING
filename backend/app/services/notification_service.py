import json
import logging
from datetime import datetime, timezone
from typing import Optional

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import NotificationType, NotificationChannel
from app.models.notification import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Manages in-app notifications and dispatches external notifications
    via email (SMTP) and Microsoft Teams (webhook).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------ #
    #  In-app notifications
    # ------------------------------------------------------------------ #

    async def create_notification(
        self,
        user_id: int,
        ticket_id: Optional[int],
        type: NotificationType,
        channel: NotificationChannel,
        title: str,
        message: Optional[str] = None,
    ) -> Notification:
        """Create and persist an in-app notification."""
        notification = Notification(
            user_id=user_id,
            ticket_id=ticket_id,
            type=type,
            channel=channel,
            title=title,
            message=message,
            is_read=False,
            sent_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Notification], int]:
        """
        Retrieve paginated notifications for a user, newest first.

        Returns (notification_list, total_count).
        """
        # Count
        count_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()

        # Data
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        notifications = result.scalars().all()

        return list(notifications), total

    async def get_unread_count(self, user_id: int) -> int:
        """Return the number of unread notifications for a user."""
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def mark_read(self, notification_id: int, user_id: int) -> None:
        """
        Mark a single notification as read.

        Raises HTTP 404 if the notification does not exist or does not belong to the user.
        """
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        notification = result.scalar_one_or_none()

        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id {notification_id} not found",
            )

        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def mark_all_read(self, user_id: int) -> None:
        """Mark all unread notifications for a user as read."""
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        result = await self.db.execute(stmt)
        notifications = result.scalars().all()

        now = datetime.now(timezone.utc)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now

        await self.db.commit()

    # ------------------------------------------------------------------ #
    #  Email dispatch (SMTP via aiosmtplib)
    # ------------------------------------------------------------------ #

    async def send_email_notification(
        self, to_email: str, subject: str, body: str
    ) -> None:
        """
        Send an email notification using the configured SMTP settings.

        Silently logs errors rather than raising -- notification failures
        should not block the caller's business logic.
        """
        if not settings.SMTP_HOST:
            logger.warning("SMTP not configured; skipping email to %s", to_email)
            return

        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            logger.info("Email sent to %s: %s", to_email, subject)
        except Exception:
            logger.exception("Failed to send email to %s", to_email)

    # ------------------------------------------------------------------ #
    #  Microsoft Teams dispatch (webhook)
    # ------------------------------------------------------------------ #

    async def send_teams_notification(
        self, title: str, message: str, ticket_url: Optional[str] = None
    ) -> None:
        """
        Post a notification to the configured Microsoft Teams webhook.

        Uses an Adaptive Card payload for rich formatting.
        Silently logs errors rather than raising.
        """
        webhook_url = settings.TEAMS_WEBHOOK_URL
        if not webhook_url:
            logger.warning("Teams webhook not configured; skipping notification")
            return

        card_body = [
            {"type": "TextBlock", "size": "Medium", "weight": "Bolder", "text": title},
            {"type": "TextBlock", "text": message, "wrap": True},
        ]

        if ticket_url:
            card_body.append(
                {
                    "type": "ActionSet",
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "View Ticket",
                            "url": ticket_url,
                        }
                    ],
                }
            )

        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": card_body,
                    },
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
            logger.info("Teams notification sent: %s", title)
        except Exception:
            logger.exception("Failed to send Teams notification: %s", title)
