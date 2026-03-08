import client from './client';
import type { PermissionItem, RoleWithPermissions } from '../types';

export const getPermissions = async () => {
  const { data } = await client.get<PermissionItem[]>('/permissions');
  return data;
};

export const getRolesWithPermissions = async () => {
  const { data } = await client.get<RoleWithPermissions[]>('/permissions/roles');
  return data;
};

export const updateRolePermissions = async (roleId: number, permissionIds: number[]) => {
  const { data } = await client.put<RoleWithPermissions>(`/permissions/roles/${roleId}`, {
    permission_ids: permissionIds,
  });
  return data;
};
