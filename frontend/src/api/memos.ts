import client from './client';
import type { PaginatedResponse } from '../types';

export interface Memo {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author_name?: string;
  created_at: string;
  updated_at: string;
}

export const getMemos = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<PaginatedResponse<Memo>>('/memos', { params });
  return data;
};

export const getMemo = async (id: number) => {
  const { data } = await client.get<Memo>(`/memos/${id}`);
  return data;
};

export const createMemo = async (memo: { title: string; content?: string }) => {
  const { data } = await client.post<Memo>('/memos', memo);
  return data;
};

export const updateMemo = async (id: number, updates: { title?: string; content?: string }) => {
  const { data } = await client.put<Memo>(`/memos/${id}`, updates);
  return data;
};

export const deleteMemo = async (id: number) => {
  const { data } = await client.delete(`/memos/${id}`);
  return data;
};
