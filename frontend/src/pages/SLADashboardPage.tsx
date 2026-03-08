import { Card, Col, Row, Statistic, Typography, Table, Tag, Spin } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';
import { getSLACompliance, getMTTR } from '../api/dashboard';
import { getSLABreaches } from '../api/sla';
import dayjs from 'dayjs';

const { Title } = Typography;

const SLADashboardPage = () => {
  const { data: compliance, isLoading } = useQuery({ queryKey: ['sla-compliance'], queryFn: () => getSLACompliance() });
  const { data: mttr } = useQuery({ queryKey: ['mttr'], queryFn: () => getMTTR() });
  const { data: breaches } = useQuery({ queryKey: ['sla-breaches'], queryFn: getSLABreaches });

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const complianceData = [
    { name: 'Met', value: compliance?.met || 0 },
    { name: 'Breached', value: compliance?.breached || 0 },
  ];

  const priorityData = compliance?.by_priority ? Object.entries(compliance.by_priority).map(([key, val]: [string, any]) => ({
    priority: key, compliance: val.compliance_pct || 0, total: val.total, met: val.met, breached: val.breached,
  })) : [];

  const breachColumns = [
    { title: 'Ticket', dataIndex: 'ticket_number', key: 'number' },
    { title: 'Response', dataIndex: 'response_met', key: 'response', render: (v: boolean | null) => v === true ? <Tag color="green">Met</Tag> : v === false ? <Tag color="red">Breached</Tag> : <Tag color="orange">Pending</Tag> },
    { title: 'Resolution', dataIndex: 'resolution_met', key: 'resolution', render: (v: boolean | null) => v === true ? <Tag color="green">Met</Tag> : v === false ? <Tag color="red">Breached</Tag> : <Tag color="orange">Pending</Tag> },
    { title: 'Response Time', dataIndex: 'actual_response_minutes', key: 'resp_time', render: (v: number) => v ? `${v} min` : '-' },
    { title: 'Created', dataIndex: 'created_at', key: 'created', render: (d: string) => d ? dayjs(d).format('MMM DD, HH:mm') : '-' },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={3}>SLA Dashboard</Title>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card><Statistic title="Overall SLA Compliance" value={compliance?.overall || 0} suffix="%" prefix={<CheckCircleOutlined />}
                          valueStyle={{ color: (compliance?.overall || 0) >= 90 ? '#3f8600' : '#cf1322' }} /></Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card><Statistic title="Total SLA Records" value={compliance?.total || 0} prefix={<ClockCircleOutlined />} /></Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card><Statistic title="Avg MTTR" value={mttr?.avg_mttr_minutes ? Math.round(mttr.avg_mttr_minutes) : 0} suffix="min" /></Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card title="SLA Compliance Overview">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={complianceData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value" label>
                  <Cell fill="#52c41a" /><Cell fill="#ff4d4f" />
                </Pie>
                <Tooltip /><Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Compliance by Priority">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={priorityData}>
                <XAxis dataKey="priority" /><YAxis domain={[0, 100]} /><Tooltip />
                <Bar dataKey="compliance" fill="#1677ff" name="Compliance %">
                  {priorityData.map((entry, i) => (
                    <Cell key={i} fill={entry.compliance >= 90 ? '#52c41a' : entry.compliance >= 70 ? '#faad14' : '#ff4d4f'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} md={12}>
          <Card title="MTTR by Priority">
            <Table dataSource={mttr?.by_priority ? Object.entries(mttr.by_priority).map(([k, v]) => ({ priority: k, mttr: v })) : []}
                   columns={[
                     { title: 'Priority', dataIndex: 'priority', key: 'p', render: (p: string) => <Tag color={p === 'P1' ? 'red' : p === 'P2' ? 'orange' : 'blue'}>{p}</Tag> },
                     { title: 'Avg MTTR', dataIndex: 'mttr', key: 'mttr', render: (v: number | null) => v ? `${Math.round(v)} min` : 'N/A' },
                   ]} rowKey="priority" pagination={false} size="small" />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="MTTR Statistics">
            <Row gutter={[16, 16]}>
              <Col span={8}><Statistic title="Min" value={mttr?.min_mttr_minutes || 0} suffix="min" /></Col>
              <Col span={8}><Statistic title="Avg" value={mttr?.avg_mttr_minutes ? Math.round(mttr.avg_mttr_minutes) : 0} suffix="min" /></Col>
              <Col span={8}><Statistic title="Max" value={mttr?.max_mttr_minutes || 0} suffix="min" /></Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Card title={<><ExclamationCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />SLA Breaches</>}>
        <Table dataSource={breaches || []} columns={breachColumns} rowKey="id" pagination={{ pageSize: 10 }} size="small" />
      </Card>
    </div>
  );
};

export default SLADashboardPage;
