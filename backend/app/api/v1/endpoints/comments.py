from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, get_current_user, require_roles
from app.models.user import User
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse

router = APIRouter()


@router.get("/{ticket_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ticket exists
    ticket = (await db.execute(select(Ticket).where(Ticket.id == ticket_id))).scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    result = await db.execute(
        select(Comment)
        .where(Comment.ticket_id == ticket_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc())
    )
    comments = result.scalars().all()

    return [
        CommentResponse(
            id=c.id,
            ticket_id=c.ticket_id,
            author_id=c.author_id,
            author_name=c.author.full_name,
            body=c.body,
            is_internal=c.is_internal,
            created_at=c.created_at,
            updated_at=c.updated_at,
        ) for c in comments
    ]


@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    ticket_id: int,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    # Verify ticket exists
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.sla_record))
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    comment = Comment(
        ticket_id=ticket_id,
        author_id=current_user.id,
        body=data.body,
        is_internal=data.is_internal or False,
    )
    db.add(comment)

    # Track first response (if assignee responds and no first_response_at yet)
    now = datetime.now(timezone.utc)
    if ticket.first_response_at is None and ticket.assignee_id == current_user.id:
        ticket.first_response_at = now

        # Update SLA response tracking
        if ticket.sla_record and ticket.sla_record.response_met is None:
            created_at = ticket.created_at.replace(tzinfo=timezone.utc) if ticket.created_at.tzinfo is None else ticket.created_at
            minutes = int((now - created_at).total_seconds() / 60)
            ticket.sla_record.actual_response_minutes = minutes
            response_deadline = ticket.sla_record.response_deadline.replace(tzinfo=timezone.utc) if ticket.sla_record.response_deadline.tzinfo is None else ticket.sla_record.response_deadline
            ticket.sla_record.response_met = now <= response_deadline

    await db.commit()
    await db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        ticket_id=comment.ticket_id,
        author_id=comment.author_id,
        author_name=current_user.full_name,
        body=comment.body,
        is_internal=comment.is_internal,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )
