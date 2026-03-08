import client from './client';
import type { Notification } from '../types';

export const getNotifications = async (params?: Record<string, unknown>) => {
  const { data } = await client.get<Notification[]>('/notifications', { params });
  return data;
};

export const getUnreadCount = async () => {
  const { data } = await client.get<{ unread_count: number }>('/notifications/unread-count');
  return data;
};

export const markRead = async (id: number) => {
  const { data } = await client.patch(`/notifications/${id}/read`);
  return data;
};

export const markAllRead = async () => {
  const { data } = await client.patch('/notifications/read-all');
  return data;
};
