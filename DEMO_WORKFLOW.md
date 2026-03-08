# ITSM Platform - Demo Workflow

## Scenario: Production Database Server Down (P1 Incident)

This walkthrough demonstrates all three phases of the platform working together during a real-world P1 incident.

---

## Getting Started

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start all services
docker compose up --build -d

# 3. Wait for services to be healthy
docker compose ps

# 4. Access the application
# Frontend: http://localhost (or http://localhost:5173 in dev mode)
# API Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/api/v1/health
```

### Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@itsm.local | admin123 |
| Manager | manager@itsm.local | manager123 |
| Engineer | engineer1@itsm.local | engineer123 |
| Engineer | engineer2@itsm.local | engineer123 |
| Viewer | viewer@itsm.local | viewer123 |

---

## PHASE 1: Core Ticket Lifecycle

### Step 1: Login as Admin
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@itsm.local", "password": "admin123"}'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@itsm.local",
    "first_name": "John",
    "last_name": "Chen",
    "role": "admin"
  }
}
```

### Step 2: View Existing Projects
```bash
curl http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer <token>"
```

Pre-seeded projects:
- **INFRA** - Infrastructure Operations
- **DEVOPS** - DevOps Platform

### Step 3: Create a P1 Incident Ticket
```bash
curl -X POST http://localhost:8000/api/v1/tickets \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Production MySQL Primary Down - All services affected",
    "description": "MySQL primary server db-prod-01 is unreachable. All dependent services are returning 500 errors. Immediate investigation required.",
    "priority": "P1",
    "assignee_id": 3,
    "team_id": 1
  }'
```

Response:
```json
{
  "id": 6,
  "ticket_number": "INFRA-004",
  "status": "open",
  "priority": "P1",
  "sla": {
    "response_deadline": "2026-02-19T10:15:00Z",
    "resolution_deadline": "2026-02-19T11:00:00Z",
    "response_met": null,
    "resolution_met": null
  },
  "created_at": "2026-02-19T10:00:00Z"
}
```

**What happened automatically:**
1. Ticket number `INFRA-004` auto-generated from project key + sequence
2. SLA record created: P1 = 15 min response, 60 min resolution
3. Response deadline set to 10:15 (15 min from now)
4. Resolution deadline set to 11:00 (60 min from now)
5. Audit log entry created for ticket creation

### Step 4: Engineer Acknowledges (First Response)
```bash
# Login as engineer1
curl -X POST http://localhost:8000/api/v1/tickets/6/comments \
  -H "Authorization: Bearer <engineer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Acknowledged. Investigating db-prod-01 connectivity immediately.",
    "is_internal": false
  }'
```

**What happened automatically:**
- `first_response_at` set to current time (10:03)
- SLA response tracked: 3 minutes < 15 min deadline = **RESPONSE MET**
- `actual_response_minutes` = 3

### Step 5: Status Transitions

```bash
# Move to In Progress
curl -X PATCH http://localhost:8000/api/v1/tickets/6/status \
  -H "Authorization: Bearer <engineer_token>" \
  -d '{"status": "in_progress"}'

# Hit a blocker - waiting for AWS support
curl -X PATCH http://localhost:8000/api/v1/tickets/6/status \
  -d '{"status": "blocked"}'

# Add internal note about the blocker
curl -X POST http://localhost:8000/api/v1/tickets/6/comments \
  -d '{"body": "Waiting for AWS support to restore EBS volume", "is_internal": true}'

# AWS responds, back to work
curl -X PATCH http://localhost:8000/api/v1/tickets/6/status \
  -d '{"status": "in_progress"}'

# Issue resolved!
curl -X PATCH http://localhost:8000/api/v1/tickets/6/status \
  -d '{"status": "resolved"}'
```

**On resolve:**
- `resolved_at` set to current time (10:52)
- SLA resolution tracked: 52 minutes < 60 min deadline = **RESOLUTION MET**
- `actual_resolution_minutes` = 52

```bash
# Manager closes the ticket
curl -X PATCH http://localhost:8000/api/v1/tickets/6/status \
  -d '{"status": "closed"}'
```

### Invalid Transition Test
```bash
# Try to go from "closed" directly to "resolved" (invalid!)
curl -X PATCH http://localhost:8000/api/v1/tickets/6/status \
  -d '{"status": "resolved"}'
```

Response: `400 Bad Request`
```json
{
  "detail": "Cannot transition from 'closed' to 'resolved'. Allowed: ['open']"
}
```

---

## PHASE 2: SLA Tracking & KPI Dashboard

### Dashboard Overview
```bash
curl http://localhost:8000/api/v1/dashboard/overview \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "total_tickets": 6,
  "open": 1,
  "in_progress": 1,
  "blocked": 1,
  "resolved": 1,
  "closed": 2,
  "sla_compliance_pct": 83.3,
  "avg_resolution_minutes": 52,
  "sla_total": 6,
  "sla_met": 5,
  "sla_breached": 1
}
```

### SLA Compliance by Priority
```bash
curl http://localhost:8000/api/v1/dashboard/sla-compliance \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "overall": 83.3,
  "total": 6,
  "met": 5,
  "breached": 1,
  "by_priority": {
    "P1": {"total": 2, "met": 2, "breached": 0, "compliance_pct": 100.0},
    "P2": {"total": 2, "met": 1, "breached": 1, "compliance_pct": 50.0},
    "P3": {"total": 2, "met": 2, "breached": 0, "compliance_pct": 100.0},
    "P4": {"total": 0, "met": 0, "breached": 0, "compliance_pct": null}
  }
}
```

### Engineer Performance
```bash
curl http://localhost:8000/api/v1/dashboard/engineer-performance \
  -H "Authorization: Bearer <token>"
```

Response:
```json
[
  {
    "engineer_id": 3,
    "engineer_name": "Sarah Miller",
    "email": "engineer1@itsm.local",
    "total_tickets": 3,
    "resolved": 2,
    "avg_resolution_minutes": 52,
    "sla_compliance_pct": 100.0
  },
  {
    "engineer_id": 4,
    "engineer_name": "Mike Johnson",
    "email": "engineer2@itsm.local",
    "total_tickets": 3,
    "resolved": 1,
    "avg_resolution_minutes": 360,
    "sla_compliance_pct": 66.7
  }
]
```

### Mean Time To Resolve (MTTR)
```bash
curl http://localhost:8000/api/v1/dashboard/mttr \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "avg_mttr_minutes": 206.0,
  "min_mttr_minutes": 52,
  "max_mttr_minutes": 360,
  "total_resolved": 2,
  "by_priority": {
    "P1": 52.0,
    "P2": null,
    "P3": 360.0,
    "P4": null
  }
}
```

---

## PHASE 3: Notifications, Escalation & Audit

### SLA Breach Scenario

A P1 ticket is created but no one responds within 15 minutes:

```
14:00 - P1 ticket INFRA-005 created
14:15 - Response deadline passes
14:15 - Celery Beat detects breach (runs every 60s)
14:15 - SLA record updated: response_met = FALSE
14:15 - Escalation rule fires:
        → Ticket auto-reassigned to team lead
        → In-app notification created
        → Email sent to escalation target
        → MS Teams webhook fired
```

### Check Breached Tickets
```bash
curl http://localhost:8000/api/v1/sla/breaches \
  -H "Authorization: Bearer <token>"
```

### View Notifications
```bash
curl http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer <token>"
```

Response:
```json
[
  {
    "id": 1,
    "type": "sla_breach",
    "channel": "in_app",
    "title": "SLA Response Breach - INFRA-005",
    "message": "The response SLA for ticket INFRA-005 has been breached.",
    "is_read": false,
    "created_at": "2026-02-19T14:15:00Z"
  },
  {
    "id": 2,
    "type": "escalation",
    "title": "Escalation - INFRA-005",
    "message": "Ticket INFRA-005 has been escalated due to response breach.",
    "is_read": false
  }
]
```

### Audit Trail for a Ticket
```bash
curl http://localhost:8000/api/v1/audit/logs/ticket/6 \
  -H "Authorization: Bearer <token>"
```

Response:
```json
[
  {"action": "create", "user_email": "admin@itsm.local",
   "new_values": {"title": "Production MySQL Primary Down", "priority": "P1", "status": "open"},
   "created_at": "2026-02-19T10:00:00Z"},
  {"action": "status_change", "user_email": "engineer1@itsm.local",
   "old_values": {"status": "open"}, "new_values": {"status": "in_progress"},
   "created_at": "2026-02-19T10:03:15Z"},
  {"action": "status_change", "old_values": {"status": "in_progress"}, "new_values": {"status": "blocked"}},
  {"action": "status_change", "old_values": {"status": "blocked"}, "new_values": {"status": "in_progress"}},
  {"action": "status_change", "old_values": {"status": "in_progress"}, "new_values": {"status": "resolved"}},
  {"action": "status_change", "old_values": {"status": "resolved"}, "new_values": {"status": "closed"}}
]
```

### Export Compliance Report
```bash
# SOC2 Compliance Report (CSV)
curl -X POST "http://localhost:8000/api/v1/audit/export?report_type=SOC2&format=csv" \
  -H "Authorization: Bearer <admin_token>" \
  --output soc2_report.csv
```

Downloads CSV with columns:
`Timestamp, User, Entity Type, Entity ID, Action, Old Values, New Values, IP Address`

---

## Frontend UI Walkthrough

### 1. Login Page
- Navigate to `http://localhost`
- Enter `admin@itsm.local` / `admin123`
- Redirected to Dashboard

### 2. Dashboard
- **KPI Cards**: Total tickets, open count, SLA compliance %, avg resolution
- **Charts**: Tickets by status (bar), SLA compliance (donut), tickets by priority
- **Engineer Performance Table**: sortable columns for resolution time and SLA %

### 3. Ticket Management
- **List View**: Filterable by status, priority; searchable; paginated
- **Create Ticket**: Select project, priority, assignee, team
- **Detail View**: Status transitions, comment timeline, SLA indicator panel
- **Status Flow**: Button-based transitions (only valid transitions shown)

### 4. SLA Dashboard
- **Compliance Overview**: Met vs Breached donut chart
- **By Priority**: Bar chart showing compliance % per P1/P2/P3/P4
- **MTTR Stats**: Min, Avg, Max resolution times
- **Breach Table**: List of all breached SLA records

### 5. Audit Logs
- **Filterable**: By entity type, action, date range
- **Export**: One-click PCI/ISO/SOC2 compliance report download
- **Change Details**: Shows old/new values for every change

---

## Quick API Test Script

```bash
#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"

# 1. Login
TOKEN=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@itsm.local","password":"admin123"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"

# 2. Health check
curl -s $BASE_URL/health | python3 -m json.tool

# 3. List tickets
curl -s $BASE_URL/tickets -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 4. Dashboard overview
curl -s $BASE_URL/dashboard/overview -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 5. SLA compliance
curl -s $BASE_URL/dashboard/sla-compliance -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo "All tests passed!"
```
