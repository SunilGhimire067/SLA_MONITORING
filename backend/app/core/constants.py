import enum


class RoleName(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ENGINEER = "engineer"
    VIEWER = "viewer"


class TicketPriority(str, enum.Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    RESOLVED = "resolved"
    CLOSED = "closed"


# Valid status transitions enforced server-side
VALID_TRANSITIONS = {
    TicketStatus.OPEN: [TicketStatus.IN_PROGRESS],
    TicketStatus.IN_PROGRESS: [TicketStatus.BLOCKED, TicketStatus.RESOLVED],
    TicketStatus.BLOCKED: [TicketStatus.IN_PROGRESS],
    TicketStatus.RESOLVED: [TicketStatus.IN_PROGRESS, TicketStatus.CLOSED],
    TicketStatus.CLOSED: [TicketStatus.OPEN],
}


class TriggerType(str, enum.Enum):
    RESPONSE_BREACH = "response_breach"
    RESOLUTION_BREACH = "resolution_breach"
    APPROACHING_BREACH = "approaching_breach"


class NotificationType(str, enum.Enum):
    SLA_WARNING = "sla_warning"
    SLA_BREACH = "sla_breach"
    ASSIGNMENT = "assignment"
    STATUS_CHANGE = "status_change"
    COMMENT = "comment"
    ESCALATION = "escalation"
    SYSTEM = "system"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    TEAMS = "teams"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    STATUS_CHANGE = "status_change"
    ASSIGN = "assign"
    SLA_BREACH = "sla_breach"
    ESCALATION = "escalation"
    LOGIN = "login"
    LOGOUT = "logout"
