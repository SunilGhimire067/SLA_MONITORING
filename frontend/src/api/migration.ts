import client from './client';

export const getMigrationProjects = async (params?: {
  page?: number;
  per_page?: number;
  search?: string;
  status?: string;
}) => {
  const { data } = await client.get('/migration/projects', { params });
  return data;
};

export const getMigrationProject = async (id: number) => {
  const { data } = await client.get(`/migration/projects/${id}`);
  return data;
};

export const createMigrationProject = async (payload: {
  name: string;
  description?: string;
  owner_id?: number;
  start_date?: string;
  end_date?: string;
}) => {
  const { data } = await client.post('/migration/projects', payload);
  return data;
};

export const updateMigrationProject = async (
  id: number,
  payload: {
    name?: string;
    description?: string;
    owner_id?: number;
    status?: string;
    start_date?: string;
    end_date?: string;
  }
) => {
  const { data } = await client.put(`/migration/projects/${id}`, payload);
  return data;
};

export const deleteMigrationProject = async (id: number) => {
  const { data } = await client.delete(`/migration/projects/${id}`);
  return data;
};

// Services
export const createMigrationService = async (
  projectId: number,
  payload: {
    name: string;
    description?: string;
    assignee_id?: number;
    expected_duration_days?: number;
    start_date?: string;
    end_date?: string;
    order?: number;
  }
) => {
  const { data } = await client.post(
    `/migration/projects/${projectId}/services`,
    payload
  );
  return data;
};

export const updateMigrationService = async (
  serviceId: number,
  payload: {
    name?: string;
    description?: string;
    assignee_id?: number;
    status?: string;
    expected_duration_days?: number;
    start_date?: string;
    end_date?: string;
    order?: number;
  }
) => {
  const { data } = await client.put(
    `/migration/services/${serviceId}`,
    payload
  );
  return data;
};

export const deleteMigrationService = async (serviceId: number) => {
  const { data } = await client.delete(`/migration/services/${serviceId}`);
  return data;
};

// Phases
export const updateMigrationPhase = async (
  phaseId: number,
  payload: {
    status?: string;
    start_date?: string;
    end_date?: string;
    progress?: number;
    notes?: string;
  }
) => {
  const { data } = await client.put(`/migration/phases/${phaseId}`, payload);
  return data;
};

// Dependencies
export const addDependency = async (
  serviceId: number,
  depends_on_id: number
) => {
  const { data } = await client.post(
    `/migration/services/${serviceId}/dependencies`,
    { depends_on_id }
  );
  return data;
};

export const removeDependency = async (depId: number) => {
  const { data } = await client.delete(`/migration/dependencies/${depId}`);
  return data;
};

// PDF Export
export const exportMigrationPDF = async (projectId: number) => {
  const response = await client.get(
    `/migration/projects/${projectId}/export-pdf`,
    { responseType: 'blob' }
  );
  return response;
};
