import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Tag, Space, Input, Select, Typography, Card } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { getTickets } from '../api/tickets';
import { getAssignees } from '../api/users';
import { useAuth } from '../context/AuthContext';
import dayjs from 'dayjs';

const { Title } = Typography;

const STATUS_COLORS: Record<string, string> = {
  open: 'blue', in_progress: 'orange', blocked: 'red', resolved: 'green', closed: 'purple',
};
const PRIORITY_COLORS: Record<string, string> = {
  P1: 'red', P2: 'orange', P3: 'blue', P4: 'green',
};

const TicketsPage = () => {
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const [filters, setFilters] = useState<Record<string, unknown>>({ page: 1, per_page: 20 });

  const { data, isLoading } = useQuery({
    queryKey: ['tickets', filters],
    queryFn: () => getTickets(filters),
  });

  const { data: assignees } = useQuery({
    queryKey: ['assignees'],
    queryFn: getAssignees,
  });

  const columns = [
    {
      title: 'Ticket', dataIndex: 'ticket_number', key: 'number', width: 120,
      render: (text: string, record: any) => (
        <a onClick={() => navigate(`/tickets/${record.id}`)}>{text}</a>
      ),
    },
    { title: 'Title', dataIndex: 'title', key: 'title', ellipsis: true },
    {
      title: 'Priority', dataIndex: 'priority', key: 'priority', width: 80,
      render: (p: string) => <Tag color={PRIORITY_COLORS[p]}>{p}</Tag>,
    },
    {
      title: 'Status', dataIndex: 'status', key: 'status', width: 120,
      render: (s: string) => <Tag color={STATUS_COLORS[s]}>{s.replace('_', ' ').toUpperCase()}</Tag>,
    },
    { title: 'Assignee', dataIndex: 'assignee_name', key: 'assignee', width: 150, render: (v: string) => v || '-' },
    {
      title: 'SLA', key: 'sla', width: 100,
      render: (_: unknown, record: any) => {
        if (!record.sla) return '-';
        const met = record.sla.resolution_met;
        if (met === true) return <Tag color="green">Met</Tag>;
        if (met === false) return <Tag color="red">Breached</Tag>;
        return <Tag color="orange">Pending</Tag>;
      },
    },
    {
      title: 'Created', dataIndex: 'created_at', key: 'created', width: 150,
      render: (d: string) => d ? dayjs(d).format('MMM DD, HH:mm') : '-',
    },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3} style={{ margin: 0 }}>Tickets</Title>
        {hasRole('admin', 'manager', 'engineer') && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/tickets/new')}>
            Create Ticket
          </Button>
        )}
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input placeholder="Search tickets..." prefix={<SearchOutlined />} style={{ width: 250 }}
                 onChange={(e) => setFilters({ ...filters, search: e.target.value || undefined, page: 1 })} />
          <Select placeholder="Status" allowClear style={{ width: 140 }}
                  onChange={(v) => setFilters({ ...filters, status: v, page: 1 })}
                  options={[
                    { value: 'open', label: 'Open' },
                    { value: 'in_progress', label: 'In Progress' },
                    { value: 'blocked', label: 'Blocked' },
                    { value: 'resolved', label: 'Resolved' },
                    { value: 'closed', label: 'Closed' },
                  ]} />
          <Select placeholder="Priority" allowClear style={{ width: 120 }}
                  onChange={(v) => setFilters({ ...filters, priority: v, page: 1 })}
                  options={[
                    { value: 'P1', label: 'P1' },
                    { value: 'P2', label: 'P2' },
                    { value: 'P3', label: 'P3' },
                    { value: 'P4', label: 'P4' },
                  ]} />
          <Select placeholder="Assignee" allowClear showSearch optionFilterProp="label" style={{ width: 180 }}
                  onChange={(v) => setFilters({ ...filters, assignee_id: v, page: 1 })}
                  options={(assignees || []).map((u: any) => ({
                    value: u.id,
                    label: `${u.first_name} ${u.last_name}`,
                  }))} />
        </Space>
      </Card>

      <Card>
        <Table
          dataSource={data?.items || []}
          columns={columns}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: data?.page || 1,
            pageSize: data?.per_page || 20,
            total: data?.total || 0,
            onChange: (page, pageSize) => setFilters({ ...filters, page, per_page: pageSize }),
            showTotal: (total) => `${total} tickets`,
          }}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default TicketsPage;
