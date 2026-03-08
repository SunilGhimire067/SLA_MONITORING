import { useState } from 'react';
import { Table, Button, Tag, Card, Typography, Modal, Form, Input, Select, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getUsers, createUser } from '../api/users';

const { Title } = Typography;
const ROLE_COLORS: Record<string, string> = { admin: 'red', manager: 'orange', engineer: 'blue', viewer: 'green' };

const UsersPage = () => {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [form] = Form.useForm();

  const { data, isLoading } = useQuery({ queryKey: ['users'], queryFn: () => getUsers({ per_page: 100 }) });

  const createMutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['users'] }); setShowModal(false); form.resetFields(); message.success('User created'); },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Failed to create user'),
  });

  const columns = [
    { title: 'Name', key: 'name', render: (_: unknown, r: any) => `${r.first_name} ${r.last_name}` },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Role', dataIndex: 'role', key: 'role', render: (r: string) => <Tag color={ROLE_COLORS[r]}>{r.toUpperCase()}</Tag> },
    { title: 'Status', dataIndex: 'is_active', key: 'status', render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? 'Active' : 'Inactive'}</Tag> },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3} style={{ margin: 0 }}>Users</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setShowModal(true)}>Add User</Button>
      </div>
      <Card>
        <Table dataSource={data?.items || []} columns={columns} rowKey="id" loading={isLoading} pagination={false} />
      </Card>

      <Modal title="Create User" open={showModal} onCancel={() => setShowModal(false)} onOk={() => form.submit()} confirmLoading={createMutation.isPending}>
        <Form form={form} layout="vertical" onFinish={(values) => createMutation.mutate(values)}>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}><Input /></Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true, min: 6 }]}><Input.Password /></Form.Item>
          <Form.Item name="first_name" label="First Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="last_name" label="Last Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="role" label="Role" rules={[{ required: true }]}>
            <Select options={[{ value: 'admin', label: 'Admin' }, { value: 'manager', label: 'Manager' }, { value: 'engineer', label: 'Engineer' }, { value: 'viewer', label: 'Viewer' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UsersPage;
