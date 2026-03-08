import { useState } from 'react';
import { Card, Table, Typography, Select, DatePicker, Space, Tag, Button, message } from 'antd';
import { AuditOutlined, DownloadOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { getAuditLogs, exportAuditReport } from '../api/audit';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

const ACTION_COLORS: Record<string, string> = {
  create: 'green', update: 'blue', delete: 'red', status_change: 'orange', assign: 'cyan', sla_breach: 'red', escalation: 'purple',
};

const AuditLogPage = () => {
  const [filters, setFilters] = useState<Record<string, unknown>>({ page: 1, per_page: 50 });

  const { data, isLoading } = useQuery({ queryKey: ['audit-logs', filters], queryFn: () => getAuditLogs(filters) });

  const handleExport = async (reportType: string) => {
    try {
      const response = await exportAuditReport({ report_type: reportType, format: 'csv' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${reportType}_audit_report.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('Report downloaded');
    } catch {
      message.error('Failed to export report');
    }
  };

  const columns = [
    {
      title: 'Timestamp', dataIndex: 'created_at', key: 'time', width: 160,
      render: (d: string) => d ? dayjs(d).format('MMM DD, HH:mm:ss') : '-',
    },
    { title: 'User', dataIndex: 'user_email', key: 'user', width: 180, render: (v: string) => v || 'System' },
    { title: 'Entity', key: 'entity', width: 150, render: (_: unknown, r: any) => `${r.entity_type} #${r.entity_id}` },
    {
      title: 'Action', dataIndex: 'action', key: 'action', width: 130,
      render: (a: string) => <Tag color={ACTION_COLORS[a] || 'default'}>{a.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Changes', key: 'changes',
      render: (_: unknown, r: any) => (
        <div style={{ fontSize: 12 }}>
          {r.old_values && <Text type="secondary">From: {JSON.stringify(r.old_values)}</Text>}
          {r.new_values && <div><Text>To: {JSON.stringify(r.new_values)}</Text></div>}
        </div>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3} style={{ margin: 0 }}><AuditOutlined style={{ marginRight: 8 }} />Audit Logs</Title>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={() => handleExport('PCI')}>PCI Report</Button>
          <Button icon={<DownloadOutlined />} onClick={() => handleExport('ISO')}>ISO Report</Button>
          <Button icon={<DownloadOutlined />} onClick={() => handleExport('SOC2')}>SOC2 Report</Button>
        </Space>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select placeholder="Entity Type" allowClear style={{ width: 140 }}
                  onChange={(v) => setFilters({ ...filters, entity_type: v, page: 1 })}
                  options={[{ value: 'ticket', label: 'Ticket' }, { value: 'user', label: 'User' }, { value: 'project', label: 'Project' }]} />
          <Select placeholder="Action" allowClear style={{ width: 150 }}
                  onChange={(v) => setFilters({ ...filters, action: v, page: 1 })}
                  options={[{ value: 'create', label: 'Create' }, { value: 'update', label: 'Update' }, { value: 'status_change', label: 'Status Change' }, { value: 'assign', label: 'Assign' }, { value: 'sla_breach', label: 'SLA Breach' }]} />
          <RangePicker onChange={(dates) => {
            if (dates) {
              setFilters({ ...filters, date_from: dates[0]?.toISOString(), date_to: dates[1]?.toISOString(), page: 1 });
            } else {
              const { date_from, date_to, ...rest } = filters as any;
              setFilters({ ...rest, page: 1 });
            }
          }} />
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
            pageSize: data?.per_page || 50,
            total: data?.total || 0,
            onChange: (page, pageSize) => setFilters({ ...filters, page, per_page: pageSize }),
          }}
          size="small"
        />
      </Card>
    </div>
  );
};

export default AuditLogPage;
