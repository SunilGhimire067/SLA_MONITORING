import client from './client';
import type { Ticket, Comment, PaginatedResponse } from '../types';

export const getTickets = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<PaginatedResponse<Ticket>>('/tickets', { params });
  return data;
};

export const getTicket = async (id: number) => {
  const { data } = await client.get<Ticket>(`/tickets/${id}`);
  return data;
};

export const createTicket = async (ticket: Partial<Ticket>) => {
  const { data } = await client.post<Ticket>('/tickets', ticket);
  return data;
};

export const updateTicket = async (id: number, updates: Partial<Ticket>) => {
  const { data } = await client.put<Ticket>(`/tickets/${id}`, updates);
  return data;
};

export const transitionStatus = async (id: number, status: string) => {
  const { data } = await client.patch<Ticket>(`/tickets/${id}/status`, { status });
  return data;
};

export const assignTicket = async (id: number, assigneeId: number) => {
  const { data } = await client.patch<Ticket>(`/tickets/${id}/assign`, null, {
    params: { assignee_id: assigneeId },
  });
  return data;
};

export const getComments = async (ticketId: number) => {
  const { data } = await client.get<Comment[]>(`/tickets/${ticketId}/comments`);
  return data;
};

export const addComment = async (ticketId: number, body: string, isInternal = false) => {
  const { data } = await client.post<Comment>(`/tickets/${ticketId}/comments`, {
    body,
    is_internal: isInternal,
  });
  return data;
};
