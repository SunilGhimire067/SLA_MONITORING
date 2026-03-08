import { useState } from 'react';
import { Card, Table, Button, Typography, Modal, Form, Input, message } from 'antd';
import { PlusOutlined, TeamOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTeams, createTeam } from '../api/teams';

const { Title } = Typography;

const TeamsPage = () => {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [form] = Form.useForm();

  const { data: teams, isLoading } = useQuery({ queryKey: ['teams'], queryFn: getTeams });

  const createMutation = useMutation({
    mutationFn: createTeam,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['teams'] }); setShowModal(false); form.resetFields(); message.success('Team created'); },
  });

  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name', render: (t: string) => <><TeamOutlined style={{ marginRight: 8 }} />{t}</> },
    { title: 'Description', dataIndex: 'description', key: 'desc', ellipsis: true },
    { title: 'Members', dataIndex: 'member_count', key: 'members' },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3} style={{ margin: 0 }}>Teams</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setShowModal(true)}>Create Team</Button>
      </div>
      <Card>
        <Table dataSource={teams || []} columns={columns} rowKey="id" loading={isLoading} pagination={false} />
      </Card>

      <Modal title="Create Team" open={showModal} onCancel={() => setShowModal(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={(values) => createMutation.mutate(values)}>
          <Form.Item name="name" label="Team Name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="description" label="Description"><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TeamsPage;
