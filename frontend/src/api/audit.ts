import client from './client';
import type { AuditLog, PaginatedResponse } from '../types';

export const getAuditLogs = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<PaginatedResponse<AuditLog>>('/audit/logs', { params });
  return data;
};

export const getEntityAuditTrail = async (entityType: string, entityId: number) => {
  const { data } = await client.get<AuditLog[]>(`/audit/logs/${entityType}/${entityId}`);
  return data;
};

export const exportAuditReport = async (params: Record<string, unknown>) => {
  const response = await client.post('/audit/export', null, { params, responseType: 'blob' });
  return response;
};
