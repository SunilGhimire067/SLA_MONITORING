import { useState } from 'react';
import { Card, Table, Button, Typography, Modal, Form, Input, Select, InputNumber, Tag, message } from 'antd';
import { PlusOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSLAPolicies, createSLAPolicy } from '../api/sla';

const { Title } = Typography;

const SLAConfigPage = () => {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [form] = Form.useForm();

  const { data: policies, isLoading } = useQuery({ queryKey: ['sla-policies'], queryFn: () => getSLAPolicies() });

  const createMutation = useMutation({
    mutationFn: createSLAPolicy,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['sla-policies'] }); setShowModal(false); form.resetFields(); message.success('SLA Policy created'); },
  });

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes} min`;
    if (minutes < 1440) return `${Math.round(minutes / 60)} hr`;
    return `${Math.round(minutes / 1440)} day`;
  };

  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name', render: (n: string) => <><SafetyCertificateOutlined style={{ marginRight: 8 }} />{n}</> },
    { title: 'Priority', dataIndex: 'priority', key: 'priority', render: (p: string) => <Tag color={p === 'P1' ? 'red' : p === 'P2' ? 'orange' : 'blue'}>{p}</Tag> },
    { title: 'Response Time', dataIndex: 'response_time_minutes', key: 'response', render: formatTime },
    { title: 'Resolution Time', dataIndex: 'resolution_time_minutes', key: 'resolution', render: formatTime },
    { title: 'Default', dataIndex: 'is_default', key: 'default', render: (v: boolean) => v ? <Tag color="green">Yes</Tag> : 'No' },
    { title: 'Status', dataIndex: 'is_active', key: 'status', render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? 'Active' : 'Inactive'}</Tag> },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3} style={{ margin: 0 }}>SLA Policies</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setShowModal(true)}>Create Policy</Button>
      </div>
      <Card>
        <Table dataSource={policies || []} columns={columns} rowKey="id" loading={isLoading} pagination={false} />
      </Card>

      <Modal title="Create SLA Policy" open={showModal} onCancel={() => setShowModal(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={(values) => createMutation.mutate(values)}>
          <Form.Item name="name" label="Policy Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="priority" label="Priority" rules={[{ required: true }]}>
            <Select options={[{ value: 'P1', label: 'P1 - Critical' }, { value: 'P2', label: 'P2 - High' }, { value: 'P3', label: 'P3 - Medium' }, { value: 'P4', label: 'P4 - Low' }]} />
          </Form.Item>
          <Form.Item name="response_time_minutes" label="Response Time (minutes)" rules={[{ required: true }]}><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="resolution_time_minutes" label="Resolution Time (minutes)" rules={[{ required: true }]}><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default SLAConfigPage;
