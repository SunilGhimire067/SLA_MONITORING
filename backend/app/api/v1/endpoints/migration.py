from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_db, get_current_user, require_roles
from app.models.migration import (
    MigrationProject,
    MigrationService,
    MigrationPhase,
    MigrationDependency,
)
from app.models.user import User
from app.core.constants import (
    MigrationProjectStatus,
    MigrationServiceStatus,
    MigrationPhaseType,
    MigrationPhaseStatus,
)
from app.schemas.migration import (
    MigrationProjectCreate,
    MigrationProjectUpdate,
    MigrationProjectResponse,
    MigrationProjectListItem,
    MigrationServiceCreate,
    MigrationServiceUpdate,
    MigrationServiceResponse,
    MigrationPhaseCreate,
    MigrationPhaseUpdate,
    MigrationPhaseResponse,
    MigrationDependencyCreate,
    MigrationDependencyResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


# ── helpers ──────────────────────────────────────────────────────────

def _phase_response(p: MigrationPhase) -> MigrationPhaseResponse:
    return MigrationPhaseResponse(
        id=p.id,
        service_id=p.service_id,
        phase_type=p.phase_type.value if hasattr(p.phase_type, "value") else p.phase_type,
        status=p.status.value if hasattr(p.status, "value") else p.status,
        start_date=p.start_date,
        end_date=p.end_date,
        progress=p.progress or 0.0,
        notes=p.notes,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


def _dep_response(d: MigrationDependency) -> MigrationDependencyResponse:
    return MigrationDependencyResponse(
        id=d.id,
        service_id=d.service_id,
        depends_on_id=d.depends_on_id,
        depends_on_name=d.depends_on.name if d.depends_on else None,
    )


def _service_response(s: MigrationService) -> MigrationServiceResponse:
    return MigrationServiceResponse(
        id=s.id,
        project_id=s.project_id,
        name=s.name,
        description=s.description,
        assignee_id=s.assignee_id,
        assignee_name=(
            f"{s.assignee.first_name} {s.assignee.last_name}" if s.assignee else None
        ),
        status=s.status.value if hasattr(s.status, "value") else s.status,
        expected_duration_days=s.expected_duration_days,
        start_date=s.start_date,
        end_date=s.end_date,
        order=s.order or 0,
        phases=[_phase_response(p) for p in (s.phases or [])],
        dependencies=[_dep_response(d) for d in (s.dependencies or [])],
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


def _project_response(proj: MigrationProject) -> MigrationProjectResponse:
    return MigrationProjectResponse(
        id=proj.id,
        name=proj.name,
        description=proj.description,
        owner_id=proj.owner_id,
        owner_name=(
            f"{proj.owner.first_name} {proj.owner.last_name}" if proj.owner else None
        ),
        status=proj.status.value if hasattr(proj.status, "value") else proj.status,
        start_date=proj.start_date,
        end_date=proj.end_date,
        services=[_service_response(s) for s in (proj.services or [])],
        created_at=proj.created_at,
        updated_at=proj.updated_at,
    )


def _calc_service_progress(svc) -> float:
    """Calculate service progress based on completed phases (each phase = 25%)."""
    phases = svc.phases or []
    if not phases:
        return 0.0
    completed = sum(
        1 for p in phases
        if (p.status.value if hasattr(p.status, "value") else p.status) == "completed"
    )
    return round((completed / len(phases)) * 100, 1)


def _calc_progress(services) -> float:
    if not services:
        return 0.0
    total = sum(_calc_service_progress(s) for s in services)
    return round(total / len(services), 1)


def _project_opts():
    return [
        selectinload(MigrationProject.owner),
        selectinload(MigrationProject.services).selectinload(MigrationService.assignee),
        selectinload(MigrationProject.services).selectinload(MigrationService.phases),
        selectinload(MigrationProject.services)
        .selectinload(MigrationService.dependencies)
        .selectinload(MigrationDependency.depends_on),
    ]


# ── Migration Projects ──────────────────────────────────────────────

@router.get("/projects", response_model=PaginatedResponse)
async def list_migration_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """All authenticated users can view migration projects."""
    query = select(MigrationProject).options(*_project_opts())

    if search:
        query = query.where(MigrationProject.name.ilike(f"%{search}%"))
    if status:
        query = query.where(MigrationProject.status == status)

    query = query.order_by(MigrationProject.created_at.desc())

    count_q = select(func.count()).select_from(
        select(MigrationProject.id).where(
            *([MigrationProject.name.ilike(f"%{search}%")] if search else []),
            *([MigrationProject.status == status] if status else []),
        ).subquery()
    )
    total = (await db.execute(count_q)).scalar()

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    projects = result.scalars().unique().all()

    items = []
    for proj in projects:
        items.append(
            MigrationProjectListItem(
                id=proj.id,
                name=proj.name,
                description=proj.description,
                owner_id=proj.owner_id,
                owner_name=(
                    f"{proj.owner.first_name} {proj.owner.last_name}"
                    if proj.owner
                    else None
                ),
                status=proj.status.value if hasattr(proj.status, "value") else proj.status,
                start_date=proj.start_date,
                end_date=proj.end_date,
                service_count=len(proj.services or []),
                overall_progress=_calc_progress(proj.services),
                created_at=proj.created_at,
                updated_at=proj.updated_at,
            )
        )

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page if total else 0,
    )


@router.post("/projects", response_model=MigrationProjectResponse, status_code=201)
async def create_migration_project(
    data: MigrationProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    proj = MigrationProject(
        name=data.name,
        description=data.description,
        owner_id=data.owner_id or current_user.id,
        status=MigrationProjectStatus.DRAFT,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(proj)
    await db.commit()

    result = await db.execute(
        select(MigrationProject).where(MigrationProject.id == proj.id).options(*_project_opts())
    )
    proj = result.scalar_one()
    return _project_response(proj)


@router.get("/projects/{project_id}", response_model=MigrationProjectResponse)
async def get_migration_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MigrationProject)
        .where(MigrationProject.id == project_id)
        .options(*_project_opts())
    )
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Migration project not found")
    return _project_response(proj)


@router.put("/projects/{project_id}", response_model=MigrationProjectResponse)
async def update_migration_project(
    project_id: int,
    data: MigrationProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(
        select(MigrationProject)
        .where(MigrationProject.id == project_id)
        .options(*_project_opts())
    )
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Migration project not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(proj, field, value)

    await db.commit()
    await db.refresh(proj)

    result = await db.execute(
        select(MigrationProject)
        .where(MigrationProject.id == project_id)
        .options(*_project_opts())
    )
    proj = result.scalar_one()
    return _project_response(proj)


@router.delete("/projects/{project_id}")
async def delete_migration_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
):
    result = await db.execute(
        select(MigrationProject).where(MigrationProject.id == project_id)
    )
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Migration project not found")

    await db.delete(proj)
    await db.commit()
    return {"message": "Migration project deleted successfully"}


# ── Migration Services ──────────────────────────────────────────────

@router.post(
    "/projects/{project_id}/services",
    response_model=MigrationServiceResponse,
    status_code=201,
)
async def create_migration_service(
    project_id: int,
    data: MigrationServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    result = await db.execute(
        select(MigrationProject).where(MigrationProject.id == project_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Migration project not found")

    svc = MigrationService(
        project_id=project_id,
        name=data.name,
        description=data.description,
        assignee_id=data.assignee_id,
        expected_duration_days=data.expected_duration_days,
        start_date=data.start_date,
        end_date=data.end_date,
        order=data.order,
    )
    db.add(svc)
    await db.flush()

    # Auto-create the 4 migration phases
    for phase_type in MigrationPhaseType:
        phase = MigrationPhase(
            service_id=svc.id,
            phase_type=phase_type,
            status=MigrationPhaseStatus.NOT_STARTED,
        )
        db.add(phase)

    await db.commit()

    result = await db.execute(
        select(MigrationService)
        .where(MigrationService.id == svc.id)
        .options(
            selectinload(MigrationService.assignee),
            selectinload(MigrationService.phases),
            selectinload(MigrationService.dependencies).selectinload(
                MigrationDependency.depends_on
            ),
        )
    )
    svc = result.scalar_one()
    return _service_response(svc)


@router.put(
    "/services/{service_id}",
    response_model=MigrationServiceResponse,
)
async def update_migration_service(
    service_id: int,
    data: MigrationServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    result = await db.execute(
        select(MigrationService)
        .where(MigrationService.id == service_id)
        .options(
            selectinload(MigrationService.assignee),
            selectinload(MigrationService.phases),
            selectinload(MigrationService.dependencies).selectinload(
                MigrationDependency.depends_on
            ),
        )
    )
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Migration service not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(svc, field, value)

    await db.commit()

    result = await db.execute(
        select(MigrationService)
        .where(MigrationService.id == service_id)
        .options(
            selectinload(MigrationService.assignee),
            selectinload(MigrationService.phases),
            selectinload(MigrationService.dependencies).selectinload(
                MigrationDependency.depends_on
            ),
        )
    )
    svc = result.scalar_one()
    return _service_response(svc)


@router.delete("/services/{service_id}")
async def delete_migration_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    result = await db.execute(
        select(MigrationService).where(MigrationService.id == service_id)
    )
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Migration service not found")

    await db.delete(svc)
    await db.commit()
    return {"message": "Migration service deleted successfully"}


# ── Migration Phases ────────────────────────────────────────────────

@router.put(
    "/phases/{phase_id}",
    response_model=MigrationPhaseResponse,
)
async def update_migration_phase(
    phase_id: int,
    data: MigrationPhaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    result = await db.execute(
        select(MigrationPhase).where(MigrationPhase.id == phase_id)
    )
    phase = result.scalar_one_or_none()
    if not phase:
        raise HTTPException(status_code=404, detail="Migration phase not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(phase, field, value)

    await db.commit()
    await db.refresh(phase)
    return _phase_response(phase)


# ── Dependencies ────────────────────────────────────────────────────

@router.post(
    "/services/{service_id}/dependencies",
    response_model=MigrationDependencyResponse,
    status_code=201,
)
async def add_dependency(
    service_id: int,
    data: MigrationDependencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    if service_id == data.depends_on_id:
        raise HTTPException(status_code=400, detail="A service cannot depend on itself")

    result = await db.execute(
        select(MigrationService).where(MigrationService.id == service_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Service not found")

    result = await db.execute(
        select(MigrationService).where(MigrationService.id == data.depends_on_id)
    )
    dep_svc = result.scalar_one_or_none()
    if not dep_svc:
        raise HTTPException(status_code=404, detail="Dependency service not found")

    existing = await db.execute(
        select(MigrationDependency).where(
            MigrationDependency.service_id == service_id,
            MigrationDependency.depends_on_id == data.depends_on_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Dependency already exists")

    dep = MigrationDependency(
        service_id=service_id,
        depends_on_id=data.depends_on_id,
    )
    db.add(dep)
    await db.commit()
    await db.refresh(dep)

    return MigrationDependencyResponse(
        id=dep.id,
        service_id=dep.service_id,
        depends_on_id=dep.depends_on_id,
        depends_on_name=dep_svc.name,
    )


@router.delete("/dependencies/{dep_id}")
async def remove_dependency(
    dep_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager", "engineer")),
):
    result = await db.execute(
        select(MigrationDependency).where(MigrationDependency.id == dep_id)
    )
    dep = result.scalar_one_or_none()
    if not dep:
        raise HTTPException(status_code=404, detail="Dependency not found")

    await db.delete(dep)
    await db.commit()
    return {"message": "Dependency removed successfully"}


# ── PDF Export ──────────────────────────────────────────────────────

@router.get("/projects/{project_id}/export-pdf")
async def export_migration_pdf(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from fastapi.responses import StreamingResponse
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import io

    result = await db.execute(
        select(MigrationProject)
        .where(MigrationProject.id == project_id)
        .options(*_project_opts())
    )
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Migration project not found")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.grey,
        spaceAfter=16,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=14,
        spaceAfter=8,
    )
    cell_style = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
    )

    elements = []

    # Title
    elements.append(Paragraph(f"Migration Timeline: {proj.name}", title_style))
    owner_name = (
        f"{proj.owner.first_name} {proj.owner.last_name}" if proj.owner else "N/A"
    )
    status_val = proj.status.value if hasattr(proj.status, "value") else proj.status
    elements.append(
        Paragraph(
            f"Owner: {owner_name} &nbsp;|&nbsp; Status: {status_val.upper()} &nbsp;|&nbsp; "
            f"Period: {proj.start_date or 'TBD'} to {proj.end_date or 'TBD'}",
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 12))

    # Services table
    if proj.services:
        elements.append(Paragraph("Services Overview", heading_style))

        header = ["#", "Service", "Assignee", "Status", "Duration", "Start", "End", "Progress"]
        data = [header]

        for idx, svc in enumerate(sorted(proj.services, key=lambda s: s.order or 0), 1):
            assignee = (
                f"{svc.assignee.first_name} {svc.assignee.last_name}"
                if svc.assignee
                else "Unassigned"
            )
            svc_status = svc.status.value if hasattr(svc.status, "value") else svc.status
            svc_progress = _calc_service_progress(svc)
            data.append([
                str(idx),
                Paragraph(svc.name, cell_style),
                Paragraph(assignee, cell_style),
                svc_status.replace("_", " ").title(),
                f"{svc.expected_duration_days or '-'} days",
                str(svc.start_date or "TBD"),
                str(svc.end_date or "TBD"),
                f"{svc_progress}%",
            ])

        col_widths = [0.4 * inch, 2.0 * inch, 1.4 * inch, 1.0 * inch, 0.9 * inch, 1.0 * inch, 1.0 * inch, 0.8 * inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4338ca")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Phase details per service
        elements.append(Paragraph("Phase Details", heading_style))
        for svc in sorted(proj.services, key=lambda s: s.order or 0):
            elements.append(
                Paragraph(f"<b>{svc.name}</b>", styles["Normal"])
            )
            elements.append(Spacer(1, 4))

            phase_header = ["Phase", "Status", "Start", "End", "Notes"]
            phase_data = [phase_header]
            for p in (svc.phases or []):
                pt = p.phase_type.value if hasattr(p.phase_type, "value") else p.phase_type
                ps = p.status.value if hasattr(p.status, "value") else p.status
                phase_data.append([
                    pt.replace("_", " ").title(),
                    ps.replace("_", " ").title(),
                    str(p.start_date or "TBD"),
                    str(p.end_date or "TBD"),
                    Paragraph(p.notes or "-", cell_style),
                ])

            phase_col_widths = [1.2 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 4.3 * inch]
            phase_table = Table(phase_data, colWidths=phase_col_widths, repeatRows=1)
            phase_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(phase_table)
            elements.append(Spacer(1, 12))

        # Dependencies
        has_deps = any(svc.dependencies for svc in proj.services)
        if has_deps:
            elements.append(Paragraph("Dependencies", heading_style))
            dep_header = ["Service", "Depends On"]
            dep_data = [dep_header]
            for svc in proj.services:
                for d in (svc.dependencies or []):
                    dep_data.append([
                        svc.name,
                        d.depends_on.name if d.depends_on else str(d.depends_on_id),
                    ])
            dep_table = Table(dep_data, colWidths=[3.5 * inch, 3.5 * inch], repeatRows=1)
            dep_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(dep_table)
    else:
        elements.append(Paragraph("No services added to this project yet.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    filename = f"migration_timeline_{proj.name.replace(' ', '_').lower()}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
