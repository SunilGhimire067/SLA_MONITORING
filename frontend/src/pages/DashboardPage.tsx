import { Card, Col, Row, Statistic, Typography, Spin, Table, Tag } from 'antd';
import {
  CheckCircleOutlined, ClockCircleOutlined, ExclamationCircleOutlined,
  WarningOutlined, FileTextOutlined, SafetyCertificateOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getOverview, getTicketsByStatus, getTicketsByPriority, getEngineerPerformance } from '../api/dashboard';

const { Title } = Typography;
const COLORS = ['#6366f1', '#f59e0b', '#ef4444', '#10b981', '#8b5cf6'];
const STATUS_COLORS: Record<string, string> = {
  open: '#6366f1', in_progress: '#f59e0b', blocked: '#ef4444', resolved: '#10b981', closed: '#8b5cf6',
};

const DashboardPage = () => {
  const { data: overview, isLoading } = useQuery({ queryKey: ['dashboard', 'overview'], queryFn: () => getOverview() });
  const { data: byStatus } = useQuery({ queryKey: ['dashboard', 'by-status'], queryFn: () => getTicketsByStatus() });
  const { data: byPriority } = useQuery({ queryKey: ['dashboard', 'by-priority'], queryFn: () => getTicketsByPriority() });
  const { data: engineers } = useQuery({ queryKey: ['dashboard', 'engineers'], queryFn: () => getEngineerPerformance() });

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const slaData = overview ? [
    { name: 'Met', value: overview.sla_met },
    { name: 'Breached', value: overview.sla_breached },
  ] : [];

  const engineerColumns = [
    { title: 'Engineer', dataIndex: 'engineer_name', key: 'name' },
    { title: 'Total', dataIndex: 'total_tickets', key: 'total', sorter: (a: any, b: any) => a.total_tickets - b.total_tickets },
    { title: 'Resolved', dataIndex: 'resolved', key: 'resolved' },
    {
      title: 'Avg Resolution', dataIndex: 'avg_resolution_minutes', key: 'avg',
      render: (v: number | null) => v ? `${Math.round(v)} min` : '-',
    },
    {
      title: 'SLA Compliance', dataIndex: 'sla_compliance_pct', key: 'sla',
      render: (v: number | null) => v !== null && v !== undefined
        ? <Tag color={v >= 90 ? 'green' : v >= 70 ? 'orange' : 'red'}>{v}%</Tag>
        : '-',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={3}>Dashboard</Title>
      </div>

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card className="kpi-card kpi-blue">
            <Statistic
              title="Total Tickets"
              value={overview?.total_tickets || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="kpi-card kpi-orange">
            <Statistic
              title="Open"
              value={overview?.open || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#f59e0b' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="kpi-card kpi-green">
            <Statistic
              title="SLA Compliance"
              value={overview?.sla_compliance_pct || 0}
              suffix="%"
              prefix={<SafetyCertificateOutlined />}
              valueStyle={{ color: (overview?.sla_compliance_pct || 0) >= 90 ? '#10b981' : '#ef4444' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="kpi-card kpi-purple">
            <Statistic
              title="Avg Resolution"
              value={overview?.avg_resolution_minutes ? Math.round(overview.avg_resolution_minutes) : 0}
              suffix="min"
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card title="Tickets by Status">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byStatus || []}>
                <XAxis dataKey="status" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15, 15, 30, 0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: 8,
                    color: '#fff',
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {(byStatus || []).map((entry: any, index: number) => (
                    <Cell key={index} fill={STATUS_COLORS[entry.status] || COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="SLA Compliance">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={slaData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value" label stroke="none">
                  <Cell fill="#10b981" />
                  <Cell fill="#ef4444" />
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15, 15, 30, 0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: 8,
                    color: '#fff',
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Tickets by Priority + Quick Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card title="Tickets by Priority">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={byPriority || []} layout="vertical">
                <XAxis type="number" />
                <YAxis dataKey="priority" type="category" />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15, 15, 30, 0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: 8,
                    color: '#fff',
                  }}
                />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {(byPriority || []).map((_: any, index: number) => (
                    <Cell key={index} fill={['#ef4444', '#f59e0b', '#6366f1', '#10b981'][index] || '#6366f1'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Quick Stats">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic title="In Progress" value={overview?.in_progress || 0} valueStyle={{ color: '#f59e0b' }} />
              </Col>
              <Col span={12}>
                <Statistic title="Blocked" value={overview?.blocked || 0} prefix={<WarningOutlined />} valueStyle={{ color: '#ef4444' }} />
              </Col>
              <Col span={12}>
                <Statistic title="Resolved" value={overview?.resolved || 0} valueStyle={{ color: '#10b981' }} />
              </Col>
              <Col span={12}>
                <Statistic title="SLA Breached" value={overview?.sla_breached || 0} prefix={<ExclamationCircleOutlined />} valueStyle={{ color: '#ef4444' }} />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Engineer Performance */}
      <Card title="Engineer Performance">
        <Table dataSource={engineers || []} columns={engineerColumns} rowKey="engineer_id" pagination={false} size="small" />
      </Card>
    </div>
  );
};

export default DashboardPage;
