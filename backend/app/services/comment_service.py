from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.comment import Comment
from app.models.ticket import Ticket


class CommentService:
    """Manages ticket comments and triggers first-response SLA checks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_comments(self, ticket_id: int) -> list[Comment]:
        """
        Retrieve all comments for a ticket, ordered by creation time ascending.
        """
        stmt = (
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.ticket_id == ticket_id)
            .order_by(Comment.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def create_comment(
        self, ticket_id: int, author_id: int, data
    ) -> Comment:
        """
        Create a new comment on a ticket.

        If this is the first comment on the ticket and the author is the
        current assignee, the ticket's first_response_at is set and the
        response SLA is checked.
        """
        from app.services.sla_service import SLAService

        # Verify ticket exists
        ticket_stmt = (
            select(Ticket)
            .options(joinedload(Ticket.sla_record))
            .where(Ticket.id == ticket_id)
        )
        ticket_result = await self.db.execute(ticket_stmt)
        ticket = ticket_result.scalar_one_or_none()

        if ticket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket with id {ticket_id} not found",
            )

        comment = Comment(
            ticket_id=ticket_id,
            author_id=author_id,
            body=data.body,
            is_internal=getattr(data, "is_internal", False),
        )
        self.db.add(comment)
        await self.db.flush()

        # Check if this is the first comment by the assignee
        if ticket.first_response_at is None and author_id == ticket.assignee_id:
            now = datetime.now(timezone.utc)
            ticket.first_response_at = now

            # Check response SLA
            sla_service = SLAService(self.db)
            await sla_service.check_response_sla(ticket)

        await self.db.commit()
        await self.db.refresh(comment)
        return comment
