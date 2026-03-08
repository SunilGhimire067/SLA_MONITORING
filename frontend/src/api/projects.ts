import client from './client';
import type { Project } from '../types';

export const getProjects = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<Project[]>('/projects', { params });
  return data;
};

export const createProject = async (project: Record<string, unknown>) => {
  const { data } = await client.post<Project>('/projects', project);
  return data;
};

export const updateProject = async (id: number, updates: Record<string, unknown>) => {
  const { data } = await client.put<Project>(`/projects/${id}`, updates);
  return data;
};
