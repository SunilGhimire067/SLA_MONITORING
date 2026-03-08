import client from './client';
import type { DashboardOverview, EngineerPerformance } from '../types';

export const getOverview = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<DashboardOverview>('/dashboard/overview', { params });
  return data;
};

export const getTicketsByStatus = async (params?: Record<string, unknown>) => {
  const { data } = await client.get('/dashboard/tickets-by-status', { params });
  return data;
};

export const getTicketsByPriority = async (params?: Record<string, unknown>) => {
  const { data } = await client.get('/dashboard/tickets-by-priority', { params });
  return data;
};

export const getSLACompliance = async (params?: Record<string, unknown>) => {
  const { data } = await client.get('/dashboard/sla-compliance', { params });
  return data;
};

export const getMTTR = async (params?: Record<string, unknown>) => {
  const { data } = await client.get('/dashboard/mttr', { params });
  return data;
};

export const getEngineerPerformance = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<EngineerPerformance[]>('/dashboard/engineer-performance', { params });
  return data;
};

export const getTeamPerformance = async (params?: Record<string, unknown>) => {
  const { data } = await client.get('/dashboard/team-performance', { params });
  return data;
};
