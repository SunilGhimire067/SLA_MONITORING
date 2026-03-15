import client from './client';
import type { PaginatedResponse } from '../types';
import type { KBArticle } from '../types';

export const getArticles = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<PaginatedResponse<KBArticle>>('/knowledge-base', { params });
  return data;
};

export const getArticle = async (id: number) => {
  const { data } = await client.get<KBArticle>(`/knowledge-base/${id}`);
  return data;
};

export const getCategories = async () => {
  const { data } = await client.get<string[]>('/knowledge-base/categories');
  return data;
};

export const createArticle = async (payload: Partial<KBArticle>) => {
  const { data } = await client.post<KBArticle>('/knowledge-base', payload);
  return data;
};

export const updateArticle = async (id: number, payload: Partial<KBArticle>) => {
  const { data } = await client.put<KBArticle>(`/knowledge-base/${id}`, payload);
  return data;
};

export const deleteArticle = async (id: number) => {
  const { data } = await client.delete(`/knowledge-base/${id}`);
  return data;
};
