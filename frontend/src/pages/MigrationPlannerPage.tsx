import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card, Button, Input, Typography, Table, Tag, Modal, Space, Select,
  DatePicker, Progress, message, Empty,
} from 'antd';
import {
  PlusOutlined, SearchOutlined, RocketOutlined, DeleteOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getMigrationProjects, createMigrationProject, deleteMigrationProject,
} from '../api/migration';
import { getAssignees } from '../api/users';
import { useAuth } from '../context/AuthContext';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const STATUS_COLORS: Record<string, string> = {
  draft: 'default',
  active: 'processing',
  completed: 'success',
  on_hold: 'warning',
};

const MigrationPlannerPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canWrite = hasRole('admin', 'manager', 'engineer');
  const canCreate = hasRole('admin', 'manager');

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({
    name: '',
    description: '',
    owner_id: undefined as number | undefined,
    start_date: '',
    end_date: '',
  });

  const { data, isLoading } = useQuery({
    queryKey: ['migration-projects', search, statusFilter],
    queryFn: () =>
      getMigrationProjects({
        per_page: 50,
        search: search || undefined,
        status: statusFilter,
      }),
  });

  const { data: assignees } = useQuery({
    queryKey: ['assignees'],
    queryFn: getAssignees,
  });

  const managers = (assignees || []).filter(
    (_a: any) => true // All users listed; backend validates owner must be manager
  );

  const createMutation = useMutation({
    mutationFn: () =>
      createMigrationProject({
        name: form.name,
        description: form.description || undefined,
        owner_id: form.owner_id,
        start_date: form.start_date || undefined,
        end_date: form.end_date || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migration-projects'] });
      setModalOpen(false);
      setForm({ name: '', description: '', owner_id: undefined, start_date: '', end_date: '' });
      message.success('Migration project created');
    },
    onError: () => message.error('Failed to create project'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteMigrationProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migration-projects'] });
      message.success('Project deleted');
    },
  });

  const handleDelete = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    Modal.confirm({
      title: 'Delete this migration project?',
      content: 'This will also delete all services, phases and dependencies.',
      okText: 'Delete',
      okButtonProps: { danger: true },
      onOk: () => deleteMutation.mutate(id),
    });
  };

  const columns = [
    {
      title: 'Project Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: any) => (
        <Space>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'rgba(99, 102, 241, 0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <RocketOutlined style={{ fontSize: 16, color: '#818cf8' }} />
          </div>
          <div>
            <Text strong>{name}</Text>
            {record.description && (
              <div>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {record.description.substring(0, 60)}{record.description.length > 60 ? '...' : ''}
                </Text>
              </div>
            )}
          </div>
        </Space>
      ),
    },
    {
      title: 'Owner',
      dataIndex: 'owner_name',
      key: 'owner_name',
      render: (name: string) => name || <Text type="secondary">Unassigned</Text>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={STATUS_COLORS[status] || 'default'}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Services',
      dataIndex: 'service_count',
      key: 'service_count',
      align: 'center' as const,
    },
    {
      title: 'Progress',
      dataIndex: 'overall_progress',
      key: 'overall_progress',
      width: 180,
      render: (val: number) => (
        <Progress
          percent={val}
          size="small"
          strokeColor={{
            '0%': '#6366f1',
            '100%': '#a855f7',
          }}
        />
      ),
    },
    {
      title: 'Timeline',
      key: 'timeline',
      render: (_: any, record: any) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {record.start_date ? dayjs(record.start_date).format('MMM DD') : 'TBD'}
          {' - '}
          {record.end_date ? dayjs(record.end_date).format('MMM DD, YYYY') : 'TBD'}
        </Text>
      ),
    },
    ...(canWrite
      ? [
          {
            title: '',
            key: 'actions',
            width: 50,
            render: (_: any, record: any) =>
              canCreate ? (
                <DeleteOutlined
                  style={{ color: '#f5222d', cursor: 'pointer' }}
                  onClick={(e: React.MouseEvent) => handleDelete(record.id, e)}
                />
              ) : null,
          },
        ]
      : []),
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Migration Timeline Planner</Title>
        {canCreate && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            New Migration Project
          </Button>
        )}
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Input
            placeholder="Search projects..."
            prefix={<SearchOutlined />}
            style={{ width: 280 }}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
          <Select
            placeholder="Filter by status"
            allowClear
            style={{ width: 160 }}
            onChange={(val) => setStatusFilter(val)}
            options={[
              { label: 'Draft', value: 'draft' },
              { label: 'Active', value: 'active' },
              { label: 'Completed', value: 'completed' },
              { label: 'On Hold', value: 'on_hold' },
            ]}
          />
        </Space>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
          loading={isLoading}
          onRow={(record) => ({
            onClick: () => navigate(`/migration/${record.id}`),
            style: { cursor: 'pointer' },
          })}
          locale={{ emptyText: <Empty description="No migration projects yet" /> }}
          pagination={false}
        />
      </Card>

      {/* Create Modal */}
      <Modal
        title="New Migration Project"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => {
          if (!form.name.trim()) {
            message.warning('Project name is required');
            return;
          }
          createMutation.mutate();
        }}
        okText="Create"
        confirmLoading={createMutation.isPending}
        width={560}
      >
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Project Name *</Text>
            <Input
              placeholder="e.g. Platform Migration to EKS"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Description</Text>
            <Input.TextArea
              placeholder="Describe the migration project..."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Project Owner (Manager)</Text>
            <Select
              placeholder="Select owner"
              allowClear
              style={{ width: '100%' }}
              value={form.owner_id}
              onChange={(val) => setForm({ ...form, owner_id: val })}
              options={(managers || []).map((u: any) => ({
                label: `${u.first_name} ${u.last_name}`,
                value: u.id,
              }))}
            />
          </div>
          <Space size={12}>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Start Date</Text>
              <DatePicker
                onChange={(_d, ds) => setForm({ ...form, start_date: ds as string })}
                style={{ width: 180 }}
              />
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>End Date</Text>
              <DatePicker
                onChange={(_d, ds) => setForm({ ...form, end_date: ds as string })}
                style={{ width: 180 }}
              />
            </div>
          </Space>
        </Space>
      </Modal>
    </div>
  );
};

export default MigrationPlannerPage;
