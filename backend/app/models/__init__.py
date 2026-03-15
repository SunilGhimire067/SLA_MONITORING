# Import all models so Alembic can discover them
from app.models.user import User, Role
from app.models.team import Team, TeamMembership
from app.models.project import Project
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.sla import SLAPolicy, SLARecord
from app.models.notification import Notification, EscalationRule
from app.models.audit import AuditLog
from app.models.permission import Permission, RolePermission
from app.models.memo import Memo
from app.models.migration import (
    MigrationProject,
    MigrationService,
    MigrationPhase,
    MigrationDependency,
)
from app.models.knowledgebase import KnowledgeBaseArticle

__all__ = [
    "User", "Role",
    "Permission", "RolePermission",
    "Team", "TeamMembership",
    "Project",
    "Ticket",
    "Comment",
    "SLAPolicy", "SLARecord",
    "Notification", "EscalationRule",
    "AuditLog",
    "Memo",
    "MigrationProject", "MigrationService", "MigrationPhase", "MigrationDependency",
    "KnowledgeBaseArticle",
]
