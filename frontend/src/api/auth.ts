import client from './client';
import type { TokenResponse } from '../types';

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const { data } = await client.post<TokenResponse>('/auth/login', { email, password });
  return data;
};

export const getMe = async () => {
  const { data } = await client.get('/auth/me');
  return data;
};

export const changePassword = async (currentPassword: string, newPassword: string) => {
  const { data } = await client.put('/auth/me/password', null, {
    params: { current_password: currentPassword, new_password: newPassword },
  });
  return data;
};
