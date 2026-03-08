import client from './client';
import type { SLAPolicy, SLARecord } from '../types';

export const getSLAPolicies = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<SLAPolicy[]>('/sla/policies', { params });
  return data;
};

export const createSLAPolicy = async (policy: Record<string, unknown>) => {
  const { data } = await client.post<SLAPolicy>('/sla/policies', policy);
  return data;
};

export const updateSLAPolicy = async (id: number, updates: Record<string, unknown>) => {
  const { data } = await client.put<SLAPolicy>(`/sla/policies/${id}`, updates);
  return data;
};

export const getSLARecords = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<SLARecord[]>('/sla/records', { params });
  return data;
};

export const getSLABreaches = async () => {
  const { data } = await client.get<SLARecord[]>('/sla/breaches');
  return data;
};
