import client from './client';
import type { Team } from '../types';

export const getTeams = async () => {
  const { data } = await client.get<Team[]>('/teams');
  return data;
};

export const createTeam = async (team: Record<string, unknown>) => {
  const { data } = await client.post<Team>('/teams', team);
  return data;
};

export const addTeamMember = async (teamId: number, userId: number) => {
  const { data } = await client.post(`/teams/${teamId}/members`, { user_id: userId });
  return data;
};

export const removeTeamMember = async (teamId: number, userId: number) => {
  const { data } = await client.delete(`/teams/${teamId}/members/${userId}`);
  return data;
};
