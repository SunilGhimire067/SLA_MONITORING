from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum, Float
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin
from app.core.constants import (
    MigrationProjectStatus,
    MigrationServiceStatus,
    MigrationPhaseType,
    MigrationPhaseStatus,
)


class MigrationProject(Base, TimestampMixin):
    __tablename__ = "migration_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    status = Column(
        Enum(MigrationProjectStatus),
        default=MigrationProjectStatus.DRAFT,
        nullable=False,
    )
    start_date = Column(Date)
    end_date = Column(Date)

    owner = relationship("User", foreign_keys=[owner_id])
    services = relationship(
        "MigrationService", back_populates="project", cascade="all, delete-orphan"
    )


class MigrationService(Base, TimestampMixin):
    __tablename__ = "migration_services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        Integer,
        ForeignKey("migration_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    status = Column(
        Enum(MigrationServiceStatus),
        default=MigrationServiceStatus.PENDING,
        nullable=False,
    )
    expected_duration_days = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    order = Column(Integer, default=0)

    project = relationship("MigrationProject", back_populates="services")
    assignee = relationship("User", foreign_keys=[assignee_id])
    phases = relationship(
        "MigrationPhase", back_populates="service", cascade="all, delete-orphan"
    )
    dependencies = relationship(
        "MigrationDependency",
        foreign_keys="MigrationDependency.service_id",
        back_populates="service",
        cascade="all, delete-orphan",
    )


class MigrationPhase(Base, TimestampMixin):
    __tablename__ = "migration_phases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(
        Integer,
        ForeignKey("migration_services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phase_type = Column(Enum(MigrationPhaseType), nullable=False)
    status = Column(
        Enum(MigrationPhaseStatus),
        default=MigrationPhaseStatus.NOT_STARTED,
        nullable=False,
    )
    start_date = Column(Date)
    end_date = Column(Date)
    progress = Column(Float, default=0.0)
    notes = Column(Text)

    service = relationship("MigrationService", back_populates="phases")


class MigrationDependency(Base):
    __tablename__ = "migration_dependencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(
        Integer,
        ForeignKey("migration_services.id", ondelete="CASCADE"),
        nullable=False,
    )
    depends_on_id = Column(
        Integer,
        ForeignKey("migration_services.id", ondelete="CASCADE"),
        nullable=False,
    )

    service = relationship(
        "MigrationService",
        foreign_keys=[service_id],
        back_populates="dependencies",
    )
    depends_on = relationship("MigrationService", foreign_keys=[depends_on_id])
