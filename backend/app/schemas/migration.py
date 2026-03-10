from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


# ---------- Phase ----------
class MigrationPhaseCreate(BaseModel):
    phase_type: str
    status: str = "not_started"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    progress: float = 0.0
    notes: Optional[str] = None


class MigrationPhaseUpdate(BaseModel):
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    progress: Optional[float] = None
    notes: Optional[str] = None


class MigrationPhaseResponse(BaseModel):
    id: int
    service_id: int
    phase_type: str
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    progress: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Dependency ----------
class MigrationDependencyCreate(BaseModel):
    depends_on_id: int


class MigrationDependencyResponse(BaseModel):
    id: int
    service_id: int
    depends_on_id: int
    depends_on_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------- Service ----------
class MigrationServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    expected_duration_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    order: int = 0


class MigrationServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    expected_duration_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    order: Optional[int] = None


class MigrationServiceResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    status: str
    expected_duration_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    order: int
    phases: List[MigrationPhaseResponse] = []
    dependencies: List[MigrationDependencyResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Project ----------
class MigrationProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class MigrationProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class MigrationProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    services: List[MigrationServiceResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MigrationProjectListItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    service_count: int = 0
    overall_progress: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
