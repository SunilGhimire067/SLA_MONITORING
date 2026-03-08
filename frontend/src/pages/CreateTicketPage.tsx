import { useNavigate } from 'react-router-dom';
import { Form, Input, Select, Button, Card, Typography, message } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createTicket } from '../api/tickets';
import { getProjects } from '../api/projects';
import { getUsers } from '../api/users';
import { getTeams } from '../api/teams';

const { Title } = Typography;
const { TextArea } = Input;

const CreateTicketPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();

  const { data: projects } = useQuery({ queryKey: ['projects'], queryFn: () => getProjects() });
  const { data: usersData } = useQuery({ queryKey: ['users'], queryFn: () => getUsers({ per_page: 100 }) });
  const { data: teams } = useQuery({ queryKey: ['teams'], queryFn: () => getTeams() });

  const mutation = useMutation({
    mutationFn: createTicket,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      message.success(`Ticket ${data.ticket_number} created!`);
      navigate(`/tickets/${data.id}`);
    },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Failed to create ticket'),
  });

  return (
    <div>
      <div className="page-header">
        <Title level={3}>Create Ticket</Title>
      </div>
      <Card style={{ maxWidth: 700 }}>
        <Form form={form} layout="vertical" onFinish={(values) => { if (!mutation.isPending) mutation.mutate(values); }} initialValues={{ priority: 'P3' }}>
          <Form.Item name="project_id" label="Project" rules={[{ required: true }]}>
            <Select placeholder="Select project" options={(projects || []).map((p) => ({ value: p.id, label: `${p.key} - ${p.name}` }))} />
          </Form.Item>
          <Form.Item name="title" label="Title" rules={[{ required: true }]}>
            <Input placeholder="Ticket title" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={4} placeholder="Describe the issue..." />
          </Form.Item>
          <Form.Item name="priority" label="Priority" rules={[{ required: true }]}>
            <Select options={[
              { value: 'P1', label: 'P1 - Critical (15 min response, 1 hr resolution)' },
              { value: 'P2', label: 'P2 - High (1 hr response, 4 hr resolution)' },
              { value: 'P3', label: 'P3 - Medium (8 hr response, 24 hr resolution)' },
              { value: 'P4', label: 'P4 - Low (24 hr response, 72 hr resolution)' },
            ]} />
          </Form.Item>
          <Form.Item name="assignee_id" label="Assignee">
            <Select placeholder="Assign to..." allowClear
                    options={(usersData?.items || []).map((u) => ({ value: u.id, label: `${u.first_name} ${u.last_name} (${u.role})` }))} />
          </Form.Item>
          <Form.Item name="team_id" label="Team">
            <Select placeholder="Select team..." allowClear
                    options={(teams || []).map((t) => ({ value: t.id, label: t.name }))} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={mutation.isPending}>Create Ticket</Button>
            <Button style={{ marginLeft: 8 }} onClick={() => navigate('/tickets')}>Cancel</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default CreateTicketPage;
