"""Seed database with demo data for development."""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.core.security import get_password_hash
from app.core.constants import TicketPriority, TicketStatus
from app.models.user import User, Role
from app.models.team import Team, TeamMembership
from app.models.project import Project
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.sla import SLAPolicy, SLARecord
from app.models.permission import Permission, RolePermission

logger = logging.getLogger(__name__)


async def seed_roles(db: AsyncSession):
    existing = (await db.execute(select(Role))).scalars().all()
    if existing:
        logger.info("Roles already exist, skipping.")
        return

    roles = [
        Role(name="admin", description="Full system access, user management, configuration"),
        Role(name="manager", description="Team management, reporting, SLA configuration"),
        Role(name="engineer", description="Ticket assignment, status updates, comments"),
        Role(name="viewer", description="Read-only access to tickets and dashboards"),
    ]
    db.add_all(roles)
    await db.commit()
    logger.info("Seeded 4 roles.")


async def seed_sla_policies(db: AsyncSession):
    existing = (await db.execute(select(SLAPolicy))).scalars().all()
    if existing:
        logger.info("SLA policies already exist, skipping.")
        return

    policies = [
        SLAPolicy(name="Default P1 SLA", priority=TicketPriority.P1,
                   response_time_minutes=15, resolution_time_minutes=60, is_default=True),
        SLAPolicy(name="Default P2 SLA", priority=TicketPriority.P2,
                   response_time_minutes=60, resolution_time_minutes=240, is_default=True),
        SLAPolicy(name="Default P3 SLA", priority=TicketPriority.P3,
                   response_time_minutes=480, resolution_time_minutes=1440, is_default=True),
        SLAPolicy(name="Default P4 SLA", priority=TicketPriority.P4,
                   response_time_minutes=1440, resolution_time_minutes=4320, is_default=True),
    ]
    db.add_all(policies)
    await db.commit()
    logger.info("Seeded 4 default SLA policies.")


async def seed_demo_data(db: AsyncSession):
    existing = (await db.execute(select(User))).scalars().all()
    if existing:
        logger.info("Demo data already exists, skipping.")
        return

    roles = {r.name: r for r in (await db.execute(select(Role))).scalars().all()}

    # Demo users
    users = [
        User(email="admin@company.com", password_hash=get_password_hash("admin123"),
             first_name="John", last_name="Chen", role_id=roles["admin"].id),
        User(email="manager@company.com", password_hash=get_password_hash("manager123"),
             first_name="Lisa", last_name="Park", role_id=roles["manager"].id),
        User(email="engineer1@company.com", password_hash=get_password_hash("engineer123"),
             first_name="Sarah", last_name="Miller", role_id=roles["engineer"].id),
        User(email="engineer2@company.com", password_hash=get_password_hash("engineer123"),
             first_name="Mike", last_name="Johnson", role_id=roles["engineer"].id),
        User(email="viewer@company.com", password_hash=get_password_hash("viewer123"),
             first_name="Alex", last_name="Wong", role_id=roles["viewer"].id),
    ]
    db.add_all(users)
    await db.flush()

    # Teams
    team_db = Team(name="Database Operations", description="Database infrastructure and operations", lead_id=users[2].id)
    team_devops = Team(name="DevOps Engineering", description="CI/CD, infrastructure automation", lead_id=users[3].id)
    db.add_all([team_db, team_devops])
    await db.flush()

    db.add_all([
        TeamMembership(team_id=team_db.id, user_id=users[2].id, joined_at=datetime.now(timezone.utc)),
        TeamMembership(team_id=team_db.id, user_id=users[3].id, joined_at=datetime.now(timezone.utc)),
        TeamMembership(team_id=team_devops.id, user_id=users[3].id, joined_at=datetime.now(timezone.utc)),
    ])

    # Projects
    proj_infra = Project(name="Infrastructure Operations", key="INFRA",
                         description="Production infrastructure incidents and tasks", lead_id=users[0].id)
    proj_devops = Project(name="DevOps Platform", key="DEVOPS",
                          description="CI/CD pipeline and automation", lead_id=users[1].id)
    db.add_all([proj_infra, proj_devops])
    await db.flush()

    sla_policies = {
        p.priority: p for p in (await db.execute(
            select(SLAPolicy).where(SLAPolicy.is_default.is_(True))
        )).scalars().all()
    }

    now = datetime.now(timezone.utc)
    tickets_data = [
        {"ticket_number": "INFRA-001", "project_id": proj_infra.id,
         "title": "Production MySQL Primary Down", "priority": TicketPriority.P1,
         "status": TicketStatus.CLOSED, "reporter_id": users[2].id,
         "assignee_id": users[2].id, "team_id": team_db.id,
         "first_response_at": now - timedelta(hours=3), "resolved_at": now - timedelta(hours=2, minutes=10),
         "closed_at": now - timedelta(hours=2)},
        {"ticket_number": "INFRA-002", "project_id": proj_infra.id,
         "title": "Redis cluster node failing health checks", "priority": TicketPriority.P2,
         "status": TicketStatus.IN_PROGRESS, "reporter_id": users[1].id,
         "assignee_id": users[3].id, "team_id": team_db.id,
         "first_response_at": now - timedelta(minutes=30)},
        {"ticket_number": "INFRA-003", "project_id": proj_infra.id,
         "title": "Increase disk space on staging servers", "priority": TicketPriority.P3,
         "status": TicketStatus.OPEN, "reporter_id": users[3].id,
         "assignee_id": users[2].id, "team_id": team_devops.id},
        {"ticket_number": "DEVOPS-001", "project_id": proj_devops.id,
         "title": "Set up GitHub Actions for backend CI/CD", "priority": TicketPriority.P3,
         "status": TicketStatus.RESOLVED, "reporter_id": users[1].id,
         "assignee_id": users[3].id, "team_id": team_devops.id,
         "first_response_at": now - timedelta(days=1), "resolved_at": now - timedelta(hours=6)},
        {"ticket_number": "DEVOPS-002", "project_id": proj_devops.id,
         "title": "Implement Terraform modules for AWS", "priority": TicketPriority.P2,
         "status": TicketStatus.BLOCKED, "reporter_id": users[0].id,
         "assignee_id": users[3].id, "team_id": team_devops.id,
         "first_response_at": now - timedelta(days=2)},
    ]

    for td in tickets_data:
        ticket = Ticket(**{k: v for k, v in td.items()})
        db.add(ticket)
        await db.flush()

        policy = sla_policies.get(td["priority"])
        if policy:
            created = ticket.created_at or now
            record = SLARecord(
                ticket_id=ticket.id, sla_policy_id=policy.id,
                response_deadline=created + timedelta(minutes=policy.response_time_minutes),
                resolution_deadline=created + timedelta(minutes=policy.resolution_time_minutes),
            )
            if ticket.first_response_at:
                mins = int((ticket.first_response_at - created).total_seconds() / 60)
                record.actual_response_minutes = max(mins, 0)
                record.response_met = ticket.first_response_at <= record.response_deadline
            if ticket.resolved_at:
                mins = int((ticket.resolved_at - created).total_seconds() / 60)
                record.actual_resolution_minutes = max(mins, 0)
                record.resolution_met = ticket.resolved_at <= record.resolution_deadline
            db.add(record)

    await db.commit()
    logger.info(f"Seeded {len(tickets_data)} demo tickets.")


async def seed_permissions(db: AsyncSession):
    existing = (await db.execute(select(Permission))).scalars().all()
    if existing:
        logger.info("Permissions already exist, skipping.")
        return

    perms = [
        Permission(name="manage_users", description="Create, edit, delete users", category="users"),
        Permission(name="manage_projects", description="Create, edit, delete projects", category="projects"),
        Permission(name="manage_teams", description="Create, edit, delete teams", category="teams"),
        Permission(name="create_tickets", description="Create new tickets", category="tickets"),
        Permission(name="view_tickets", description="View tickets and details", category="tickets"),
        Permission(name="manage_sla", description="Configure SLA policies", category="sla"),
        Permission(name="view_sla", description="View SLA dashboard", category="sla"),
        Permission(name="view_audit", description="View audit logs", category="audit"),
        Permission(name="manage_roles", description="Manage role permissions", category="roles"),
    ]
    db.add_all(perms)
    await db.flush()

    perm_map = {p.name: p.id for p in perms}
    roles = {r.name: r for r in (await db.execute(select(Role))).scalars().all()}

    # Default role-permission mappings
    role_perms = {
        "admin": list(perm_map.keys()),
        "manager": ["manage_projects", "manage_teams", "create_tickets", "view_tickets", "manage_sla", "view_sla", "view_audit"],
        "engineer": ["create_tickets", "view_tickets", "view_sla"],
        "viewer": ["view_tickets", "view_sla"],
    }

    for role_name, perm_names in role_perms.items():
        if role_name in roles:
            for perm_name in perm_names:
                db.add(RolePermission(role_id=roles[role_name].id, permission_id=perm_map[perm_name]))

    await db.commit()
    logger.info("Seeded permissions and role-permission mappings.")


async def run_seed():
    async with async_session_factory() as db:
        await seed_roles(db)
        await seed_permissions(db)
        await seed_sla_policies(db)
        await seed_demo_data(db)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())
