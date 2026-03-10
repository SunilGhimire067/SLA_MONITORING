import client from './client';
import type { User, PaginatedResponse } from '../types';

export const getUsers = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<PaginatedResponse<User>>('/users', { params });
  return data;
};

export const getUser = async (id: number) => {
  const { data } = await client.get<User>(`/users/${id}`);
  return data;
};

export const createUser = async (user: Record<string, unknown>) => {
  const { data } = await client.post<User>('/users', user);
  return data;
};

export const updateUser = async (id: number, updates: Record<string, unknown>) => {
  const { data } = await client.put<User>(`/users/${id}`, updates);
  return data;
};

export const deactivateUser = async (id: number) => {
  const { data } = await client.delete(`/users/${id}`);
  return data;
};

export const getAssignees = async () => {
  const { data } = await client.get<{ id: number; first_name: string; last_name: string }[]>('/users/assignees');
  return data;
};
