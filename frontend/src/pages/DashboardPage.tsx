import { Card, Col, Row, Statistic, Typography, Spin, Table, Tag } from 'antd';
import {
  CheckCircleOutlined, ClockCircleOutlined, ExclamationCircleOutlined,
  WarningOutlined, FileTextOutlined, SafetyCertificateOutlined,
  ThunderboltOutlined, RocketOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getOverview, getTicketsByStatus, getTicketsByPriority, getEngineerPerformance } from '../api/dashboard';

const { Title } = Typography;
const COLORS = ['#6366f1', '#f59e0b', '#ef4444', '#10b981', '#a855f7'];
const STATUS_COLORS: Record<string, string> = {
  open: '#818cf8', in_progress: '#f59e0b', blocked: '#ef4444', resolved: '#10b981', closed: '#a855f7',
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
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '6px 14px',
          borderRadius: 10,
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.15)',
        }}>
          <div style={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            background: '#10b981',
            boxShadow: '0 0 8px rgba(16, 185, 129, 0.5)',
            animation: 'badgePulse 2s ease-in-out infinite',
          }} />
          <span style={{ color: '#10b981', fontSize: 12, fontWeight: 600, letterSpacing: '0.5px' }}>24/7 MONITORING</span>
        </div>
      </div>

      {/* KPI Cards */}
      <Row gutter={[20, 20]} style={{ marginBottom: 28 }}>
        <Col xs={24} sm={12} md={6}>
          <Card className="kpi-card kpi-blue">
            <Statistic
              title="Total Tickets"
              value={overview?.total_tickets || 0}
              prefix={<FileTextOutlined style={{ color: '#818cf8' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="kpi-card kpi-orange">
            <Statistic
              title="Open"
              value={overview?.open || 0}
              prefix={<ClockCircleOutlined style={{ color: '#f59e0b' }} />}
              valueStyle={{ color: '#fbbf24' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="kpi-card kpi-green">
            <Statistic
              title="SLA Compliance"
              value={overview?.sla_compliance_pct || 0}
              suffix="%"
              prefix={<SafetyCertificateOutlined style={{ color: '#10b981' }} />}
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
              prefix={<ThunderboltOutlined style={{ color: '#a855f7' }} />}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts Row */}
      <Row gutter={[20, 20]} style={{ marginBottom: 28 }}>
        <Col xs={24} md={12}>
          <Card title="Tickets by Status">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byStatus || []}>
                <XAxis dataKey="status" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
                <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15, 12, 40, 0.95)',
                    border: '1px solid rgba(129, 140, 248, 0.15)',
                    borderRadius: 12,
                    color: '#fff',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                  }}
                />
                <Bar dataKey="count" radius={[8, 8, 0, 0]}>
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
                <Pie data={slaData} cx="50%" cy="50%" innerRadius={65} outerRadius={105} dataKey="value" label stroke="none">
                  <Cell fill="#10b981" />
                  <Cell fill="#ef4444" />
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15, 12, 40, 0.95)',
                    border: '1px solid rgba(129, 140, 248, 0.15)',
                    borderRadius: 12,
                    color: '#fff',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Tickets by Priority + Quick Stats */}
      <Row gutter={[20, 20]} style={{ marginBottom: 28 }}>
        <Col xs={24} md={12}>
          <Card title="Tickets by Priority">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={byPriority || []} layout="vertical">
                <XAxis type="number" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
                <YAxis dataKey="priority" type="category" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15, 12, 40, 0.95)',
                    border: '1px solid rgba(129, 140, 248, 0.15)',
                    borderRadius: 12,
                    color: '#fff',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                  }}
                />
                <Bar dataKey="count" radius={[0, 8, 8, 0]}>
                  {(byPriority || []).map((_: any, index: number) => (
                    <Cell key={index} fill={['#ef4444', '#f59e0b', '#818cf8', '#10b981'][index] || '#818cf8'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Quick Stats">
            <Row gutter={[20, 20]}>
              <Col span={12}>
                <div style={{ padding: '16px', borderRadius: 14, background: 'rgba(245, 158, 11, 0.06)', border: '1px solid rgba(245, 158, 11, 0.1)' }}>
                  <Statistic title="In Progress" value={overview?.in_progress || 0} prefix={<RocketOutlined />} valueStyle={{ color: '#fbbf24' }} />
                </div>
              </Col>
              <Col span={12}>
                <div style={{ padding: '16px', borderRadius: 14, background: 'rgba(239, 68, 68, 0.06)', border: '1px solid rgba(239, 68, 68, 0.1)' }}>
                  <Statistic title="Blocked" value={overview?.blocked || 0} prefix={<WarningOutlined />} valueStyle={{ color: '#f87171' }} />
                </div>
              </Col>
              <Col span={12}>
                <div style={{ padding: '16px', borderRadius: 14, background: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                  <Statistic title="Resolved" value={overview?.resolved || 0} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#10b981' }} />
                </div>
              </Col>
              <Col span={12}>
                <div style={{ padding: '16px', borderRadius: 14, background: 'rgba(239, 68, 68, 0.06)', border: '1px solid rgba(239, 68, 68, 0.1)' }}>
                  <Statistic title="SLA Breached" value={overview?.sla_breached || 0} prefix={<ExclamationCircleOutlined />} valueStyle={{ color: '#f87171' }} />
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Engineer Performance */}
      <Card title={<><RocketOutlined style={{ marginRight: 8, color: '#818cf8' }} />Engineer Performance</>}>
        <Table dataSource={engineers || []} columns={engineerColumns} rowKey="engineer_id" pagination={false} size="small" />
      </Card>
    </div>
  );
};

export default DashboardPage;
