from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_db, require_roles
from app.models.user import User
from app.models.notification import EscalationRule
from app.schemas.notification import EscalationRuleCreate, EscalationRuleUpdate, EscalationRuleResponse

router = APIRouter()


@router.get("", response_model=list[EscalationRuleResponse])
async def list_escalation_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(
        select(EscalationRule).where(EscalationRule.is_active.is_(True))
    )
    rules = result.scalars().all()

    return [
        EscalationRuleResponse(
            id=r.id, name=r.name, project_id=r.project_id,
            priority=r.priority.value if r.priority else None,
            trigger_type=r.trigger_type.value,
            trigger_threshold_minutes=r.trigger_threshold_minutes,
            escalate_to_user_id=r.escalate_to_user_id,
            escalate_to_team_id=r.escalate_to_team_id,
            notify_channels=r.notify_channels,
            is_active=r.is_active,
            created_at=r.created_at, updated_at=r.updated_at,
        ) for r in rules
    ]


@router.post("", response_model=EscalationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_escalation_rule(
    data: EscalationRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    rule = EscalationRule(
        name=data.name,
        project_id=data.project_id,
        priority=data.priority,
        trigger_type=data.trigger_type,
        trigger_threshold_minutes=data.trigger_threshold_minutes or 0,
        escalate_to_user_id=data.escalate_to_user_id,
        escalate_to_team_id=data.escalate_to_team_id,
        notify_channels=data.notify_channels,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)

    return EscalationRuleResponse(
        id=rule.id, name=rule.name, project_id=rule.project_id,
        priority=rule.priority.value if rule.priority else None,
        trigger_type=rule.trigger_type.value,
        trigger_threshold_minutes=rule.trigger_threshold_minutes,
        escalate_to_user_id=rule.escalate_to_user_id,
        escalate_to_team_id=rule.escalate_to_team_id,
        notify_channels=rule.notify_channels,
        is_active=rule.is_active,
        created_at=rule.created_at, updated_at=rule.updated_at,
    )


@router.get("/{rule_id}", response_model=EscalationRuleResponse)
async def get_escalation_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(select(EscalationRule).where(EscalationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Escalation rule not found")

    return EscalationRuleResponse(
        id=rule.id, name=rule.name, project_id=rule.project_id,
        priority=rule.priority.value if rule.priority else None,
        trigger_type=rule.trigger_type.value,
        trigger_threshold_minutes=rule.trigger_threshold_minutes,
        escalate_to_user_id=rule.escalate_to_user_id,
        escalate_to_team_id=rule.escalate_to_team_id,
        notify_channels=rule.notify_channels,
        is_active=rule.is_active,
        created_at=rule.created_at, updated_at=rule.updated_at,
    )


@router.put("/{rule_id}", response_model=EscalationRuleResponse)
async def update_escalation_rule(
    rule_id: int,
    data: EscalationRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(select(EscalationRule).where(EscalationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Escalation rule not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)

    return EscalationRuleResponse(
        id=rule.id, name=rule.name, project_id=rule.project_id,
        priority=rule.priority.value if rule.priority else None,
        trigger_type=rule.trigger_type.value,
        trigger_threshold_minutes=rule.trigger_threshold_minutes,
        escalate_to_user_id=rule.escalate_to_user_id,
        escalate_to_team_id=rule.escalate_to_team_id,
        notify_channels=rule.notify_channels,
        is_active=rule.is_active,
        created_at=rule.created_at, updated_at=rule.updated_at,
    )


@router.delete("/{rule_id}")
async def delete_escalation_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    result = await db.execute(select(EscalationRule).where(EscalationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Escalation rule not found")

    rule.is_active = False
    await db.commit()
    return {"message": "Escalation rule deactivated"}
