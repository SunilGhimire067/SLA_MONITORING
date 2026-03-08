export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  timezone?: string;
  permissions?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface PermissionItem {
  id: number;
  name: string;
  description?: string;
  category?: string;
}

export interface RoleWithPermissions {
  id: number;
  name: string;
  description?: string;
  permissions: PermissionItem[];
}

export interface Team {
  id: number;
  name: string;
  description?: string;
  lead_id?: number;
  member_count: number;
  members?: TeamMember[];
  created_at?: string;
  updated_at?: string;
}

export interface TeamMember {
  user_id: number;
  name: string;
  email: string;
}

export interface Project {
  id: number;
  name: string;
  key: string;
  description?: string;
  lead_id?: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface SLAInfo {
  response_deadline?: string;
  resolution_deadline?: string;
  response_met?: boolean;
  resolution_met?: boolean;
}

export interface Ticket {
  id: number;
  ticket_number: string;
  project_id: number;
  project_key?: string;
  title: string;
  description?: string;
  priority: string;
  status: string;
  reporter_id: number;
  reporter_name?: string;
  assignee_id?: number;
  assignee_name?: string;
  team_id?: number;
  tags?: string[];
  first_response_at?: string;
  resolved_at?: string;
  closed_at?: string;
  sla?: SLAInfo;
  created_at?: string;
  updated_at?: string;
}

export interface Comment {
  id: number;
  ticket_id: number;
  author_id: number;
  author_name?: string;
  body: string;
  is_internal: boolean;
  created_at?: string;
}

export interface SLAPolicy {
  id: number;
  name: string;
  priority: string;
  project_id?: number;
  response_time_minutes: number;
  resolution_time_minutes: number;
  is_default: boolean;
  is_active: boolean;
  created_at?: string;
}

export interface SLARecord {
  id: number;
  ticket_id: number;
  ticket_number?: string;
  sla_policy_id: number;
  response_deadline?: string;
  resolution_deadline?: string;
  response_met?: boolean;
  resolution_met?: boolean;
  actual_response_minutes?: number;
  actual_resolution_minutes?: number;
  created_at?: string;
}

export interface Notification {
  id: number;
  user_id: number;
  ticket_id?: number;
  type: string;
  channel: string;
  title: string;
  message?: string;
  is_read: boolean;
  created_at?: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  user_email?: string;
  entity_type: string;
  entity_id: number;
  action: string;
  old_values?: Record<string, unknown>;
  new_values?: Record<string, unknown>;
  ip_address?: string;
  created_at?: string;
}

export interface EscalationRule {
  id: number;
  name: string;
  project_id?: number;
  priority?: string;
  trigger_type: string;
  trigger_threshold_minutes: number;
  escalate_to_user_id?: number;
  escalate_to_team_id?: number;
  notify_channels?: string[];
  is_active: boolean;
  created_at?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface DashboardOverview {
  total_tickets: number;
  open: number;
  in_progress: number;
  blocked: number;
  resolved: number;
  closed: number;
  sla_compliance_pct: number;
  avg_resolution_minutes?: number;
  sla_total: number;
  sla_met: number;
  sla_breached: number;
}

export interface EngineerPerformance {
  engineer_id: number;
  engineer_name: string;
  email: string;
  total_tickets: number;
  resolved: number;
  avg_resolution_minutes?: number;
  sla_compliance_pct?: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}
