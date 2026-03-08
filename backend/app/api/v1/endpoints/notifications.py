from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse

router = APIRouter()


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    notifications = result.scalars().all()

    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            ticket_id=n.ticket_id,
            type=n.type.value,
            channel=n.channel.value,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at,
        ) for n in notifications
    ]


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
    )).scalar() or 0

    return {"unread_count": count}


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Marked as read"}


@router.patch("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import update

    await db.execute(
        update(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        ).values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"message": "All notifications marked as read"}
