from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    teams,
    projects,
    tickets,
    comments,
    sla,
    dashboard,
    notifications,
    escalation_rules,
    audit,
    health,
    permissions,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_v1_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_v1_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_v1_router.include_router(comments.router, prefix="/tickets", tags=["Comments"])
api_v1_router.include_router(sla.router, prefix="/sla", tags=["SLA"])
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_v1_router.include_router(escalation_rules.router, prefix="/escalation-rules", tags=["Escalation Rules"])
api_v1_router.include_router(audit.router, prefix="/audit", tags=["Audit & Compliance"])
api_v1_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
