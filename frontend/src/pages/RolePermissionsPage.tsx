import { Card, Table, Checkbox, Typography, Tag, message, Spin } from 'antd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getPermissions, getRolesWithPermissions, updateRolePermissions } from '../api/permissions';
import type { PermissionItem, RoleWithPermissions } from '../types';

const { Title } = Typography;

const CATEGORY_COLORS: Record<string, string> = {
  users: 'blue', projects: 'purple', teams: 'cyan', tickets: 'orange',
  sla: 'green', audit: 'gold', roles: 'red',
};

const RolePermissionsPage = () => {
  const queryClient = useQueryClient();

  const { data: permissions, isLoading: loadingPerms } = useQuery({
    queryKey: ['permissions'],
    queryFn: getPermissions,
  });

  const { data: roles, isLoading: loadingRoles } = useQuery({
    queryKey: ['roles-permissions'],
    queryFn: getRolesWithPermissions,
  });

  const mutation = useMutation({
    mutationFn: ({ roleId, permissionIds }: { roleId: number; permissionIds: number[] }) =>
      updateRolePermissions(roleId, permissionIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles-permissions'] });
      message.success('Permissions updated');
    },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Failed to update permissions'),
  });

  const handleToggle = (role: RoleWithPermissions, perm: PermissionItem, checked: boolean) => {
    const currentIds = role.permissions.map((p) => p.id);
    const newIds = checked
      ? [...currentIds, perm.id]
      : currentIds.filter((id) => id !== perm.id);
    mutation.mutate({ roleId: role.id, permissionIds: newIds });
  };

  const roleHasPerm = (role: RoleWithPermissions, permId: number) =>
    role.permissions.some((p) => p.id === permId);

  if (loadingPerms || loadingRoles) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const columns = [
    {
      title: 'Permission',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string) => <code style={{ fontSize: 13 }}>{name}</code>,
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (cat: string) => <Tag color={CATEGORY_COLORS[cat] || 'default'}>{cat}</Tag>,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    ...(roles || []).map((role) => ({
      title: <Tag color={role.name === 'admin' ? 'red' : role.name === 'manager' ? 'blue' : role.name === 'engineer' ? 'green' : 'default'}>{role.name}</Tag>,
      key: `role-${role.id}`,
      width: 100,
      align: 'center' as const,
      render: (_: unknown, perm: PermissionItem) => (
        <Checkbox
          checked={roleHasPerm(role, perm.id)}
          onChange={(e) => handleToggle(role, perm, e.target.checked)}
          disabled={role.name === 'admin' && perm.name === 'manage_roles'}
        />
      ),
    })),
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={3}>Role Permissions</Title>
      </div>
      <Card>
        <Table
          dataSource={permissions || []}
          columns={columns}
          rowKey="id"
          pagination={false}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default RolePermissionsPage;
