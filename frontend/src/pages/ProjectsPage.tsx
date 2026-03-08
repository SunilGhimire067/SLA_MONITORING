import { useState } from 'react';
import { Card, Table, Button, Tag, Typography, Modal, Form, Input, message } from 'antd';
import { PlusOutlined, ProjectOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getProjects, createProject } from '../api/projects';

const { Title } = Typography;

const ProjectsPage = () => {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [form] = Form.useForm();

  const { data: projects, isLoading } = useQuery({ queryKey: ['projects'], queryFn: () => getProjects() });

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['projects'] }); setShowModal(false); form.resetFields(); message.success('Project created'); },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Failed to create project'),
  });

  const columns = [
    { title: 'Key', dataIndex: 'key', key: 'key', width: 100, render: (k: string) => <Tag color="blue">{k}</Tag> },
    { title: 'Name', dataIndex: 'name', key: 'name', render: (n: string) => <><ProjectOutlined style={{ marginRight: 8 }} />{n}</> },
    { title: 'Description', dataIndex: 'description', key: 'desc', ellipsis: true },
    { title: 'Status', dataIndex: 'is_active', key: 'status', render: (v: boolean) => <Tag color={v ? 'green' : 'default'}>{v ? 'Active' : 'Archived'}</Tag> },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3} style={{ margin: 0 }}>Projects</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setShowModal(true)}>Create Project</Button>
      </div>
      <Card>
        <Table dataSource={projects || []} columns={columns} rowKey="id" loading={isLoading} pagination={false} />
      </Card>

      <Modal title="Create Project" open={showModal} onCancel={() => setShowModal(false)} onOk={() => form.submit()} confirmLoading={createMutation.isPending}>
        <Form form={form} layout="vertical" onFinish={(values) => createMutation.mutate(values)}>
          <Form.Item name="name" label="Project Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="key" label="Project Key" rules={[{ required: true }]} extra="Short unique key (e.g., INFRA, DEVOPS)"><Input maxLength={10} style={{ textTransform: 'uppercase' }} /></Form.Item>
          <Form.Item name="description" label="Description"><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ProjectsPage;
