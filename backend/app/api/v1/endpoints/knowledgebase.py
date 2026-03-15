from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, get_current_user, require_roles
from app.models.knowledgebase import KnowledgeBaseArticle
from app.models.user import User
from app.schemas.knowledgebase import KBArticleCreate, KBArticleUpdate, KBArticleResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


def _article_response(a: KnowledgeBaseArticle) -> KBArticleResponse:
    return KBArticleResponse(
        id=a.id,
        title=a.title,
        category=a.category,
        subcategory=a.subcategory,
        keywords=a.keywords,
        problem=a.problem,
        description=a.description,
        solution=a.solution,
        author_id=a.author_id,
        author_name=(
            f"{a.author.first_name} {a.author.last_name}" if a.author else None
        ),
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


@router.get("", response_model=PaginatedResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(KnowledgeBaseArticle).options(selectinload(KnowledgeBaseArticle.author))

    if category:
        query = query.where(KnowledgeBaseArticle.category == category)

    if search:
        term = f"%{search}%"
        query = query.where(
            (KnowledgeBaseArticle.title.ilike(term))
            | (KnowledgeBaseArticle.problem.ilike(term))
            | (KnowledgeBaseArticle.keywords.ilike(term))
            | (KnowledgeBaseArticle.solution.ilike(term))
        )

    query = query.order_by(KnowledgeBaseArticle.updated_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    articles = result.scalars().all()

    return PaginatedResponse(
        items=[_article_response(a) for a in articles],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page if total else 0,
    )


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(KnowledgeBaseArticle.category)
        .distinct()
        .order_by(KnowledgeBaseArticle.category)
    )
    return [row[0] for row in result.all()]


@router.get("/{article_id}", response_model=KBArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(KnowledgeBaseArticle)
        .where(KnowledgeBaseArticle.id == article_id)
        .options(selectinload(KnowledgeBaseArticle.author))
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return _article_response(article)


@router.post("", response_model=KBArticleResponse, status_code=201)
async def create_article(
    data: KBArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    article = KnowledgeBaseArticle(
        title=data.title,
        category=data.category,
        subcategory=data.subcategory,
        keywords=data.keywords,
        problem=data.problem,
        description=data.description,
        solution=data.solution,
        author_id=current_user.id,
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)

    return KBArticleResponse(
        id=article.id,
        title=article.title,
        category=article.category,
        subcategory=article.subcategory,
        keywords=article.keywords,
        problem=article.problem,
        description=article.description,
        solution=article.solution,
        author_id=article.author_id,
        author_name=f"{current_user.first_name} {current_user.last_name}",
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


@router.put("/{article_id}", response_model=KBArticleResponse)
async def update_article(
    article_id: int,
    data: KBArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    result = await db.execute(
        select(KnowledgeBaseArticle)
        .where(KnowledgeBaseArticle.id == article_id)
        .options(selectinload(KnowledgeBaseArticle.author))
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    await db.commit()
    await db.refresh(article)
    return _article_response(article)


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(
        select(KnowledgeBaseArticle).where(KnowledgeBaseArticle.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.delete(article)
    await db.commit()
    return {"message": "Article deleted successfully"}
