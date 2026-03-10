from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.dependencies import get_db, get_current_user
from app.models.memo import Memo
from app.models.user import User
from app.schemas.memo import MemoCreate, MemoUpdate, MemoResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_memos(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Memo)

    if search:
        query = query.where(
            (Memo.title.ilike(f"%{search}%"))
            | (Memo.content.ilike(f"%{search}%"))
        )

    query = query.order_by(Memo.updated_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    memos = result.scalars().all()

    return PaginatedResponse(
        items=[
            MemoResponse(
                id=m.id, title=m.title, content=m.content,
                author_id=m.author_id,
                author_name=f"{m.author.first_name} {m.author.last_name}" if m.author else None,
                created_at=m.created_at, updated_at=m.updated_at,
            ) for m in memos
        ],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page if total else 0,
    )


@router.post("", response_model=MemoResponse, status_code=201)
async def create_memo(
    data: MemoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memo = Memo(
        title=data.title,
        content=data.content,
        author_id=current_user.id,
    )
    db.add(memo)
    await db.commit()
    await db.refresh(memo)

    return MemoResponse(
        id=memo.id, title=memo.title, content=memo.content,
        author_id=memo.author_id,
        author_name=f"{current_user.first_name} {current_user.last_name}",
        created_at=memo.created_at, updated_at=memo.updated_at,
    )


@router.get("/{memo_id}", response_model=MemoResponse)
async def get_memo(
    memo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Memo).where(Memo.id == memo_id))
    memo = result.scalar_one_or_none()
    if not memo:
        raise HTTPException(status_code=404, detail="Memo not found")

    return MemoResponse(
        id=memo.id, title=memo.title, content=memo.content,
        author_id=memo.author_id,
        author_name=f"{memo.author.first_name} {memo.author.last_name}" if memo.author else None,
        created_at=memo.created_at, updated_at=memo.updated_at,
    )


@router.put("/{memo_id}", response_model=MemoResponse)
async def update_memo(
    memo_id: int,
    data: MemoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Memo).where(Memo.id == memo_id))
    memo = result.scalar_one_or_none()
    if not memo:
        raise HTTPException(status_code=404, detail="Memo not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(memo, field, value)

    await db.commit()
    await db.refresh(memo)

    return MemoResponse(
        id=memo.id, title=memo.title, content=memo.content,
        author_id=memo.author_id,
        author_name=f"{memo.author.first_name} {memo.author.last_name}" if memo.author else None,
        created_at=memo.created_at, updated_at=memo.updated_at,
    )


@router.delete("/{memo_id}")
async def delete_memo(
    memo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Memo).where(Memo.id == memo_id))
    memo = result.scalar_one_or_none()
    if not memo:
        raise HTTPException(status_code=404, detail="Memo not found")

    await db.delete(memo)
    await db.commit()
    return {"message": "Memo deleted successfully"}
