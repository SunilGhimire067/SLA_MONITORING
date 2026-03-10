import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Button, Space, Timeline, Input, Checkbox, message, Typography, Row, Col, Divider, Spin } from 'antd';
import { ArrowLeftOutlined, ClockCircleOutlined, CheckCircleOutlined, ExclamationCircleOutlined, UserAddOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTicket, getComments, transitionStatus, addComment, assignTicket } from '../api/tickets';
import { useAuth } from '../context/AuthContext';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { TextArea } = Input;

const STATUS_COLORS: Record<string, string> = { open: 'blue', in_progress: 'orange', blocked: 'red', resolved: 'green', closed: 'purple' };
const TRANSITIONS: Record<string, string[]> = {
  open: ['in_progress'], in_progress: ['blocked', 'resolved'], blocked: ['in_progress'], resolved: ['in_progress', 'closed'], closed: ['open'],
};

const TicketDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { hasRole, user } = useAuth();
  const canWrite = hasRole('admin', 'manager', 'engineer');
  const [commentBody, setCommentBody] = useState('');
  const [isInternal, setIsInternal] = useState(false);

  const { data: ticket, isLoading } = useQuery({ queryKey: ['ticket', id], queryFn: () => getTicket(Number(id)) });
  const { data: comments } = useQuery({ queryKey: ['comments', id], queryFn: () => getComments(Number(id)) });

  const statusMutation = useMutation({
    mutationFn: (status: string) => transitionStatus(Number(id), status),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['ticket', id] }); message.success('Status updated'); },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Failed to update status'),
  });

  const assignMutation = useMutation({
    mutationFn: () => assignTicket(Number(id), user!.id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['ticket', id] }); message.success('Ticket assigned to you'); },
    onError: (err: any) => message.error(err.response?.data?.detail || 'Failed to assign ticket'),
  });

  const commentMutation = useMutation({
    mutationFn: () => addComment(Number(id), commentBody, isInternal),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', id] });
      queryClient.invalidateQueries({ queryKey: ['ticket', id] });
      setCommentBody('');
      message.success('Comment added');
    },
  });

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!ticket) return <div>Ticket not found</div>;

  return (
    <div>
      <div className="page-header">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/tickets')}>Back to Tickets</Button>
      </div>

      <Row gutter={[24, 24]}>
        <Col xs={24} md={16}>
          <Card>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <Text type="secondary">{ticket.ticket_number}</Text>
                  <Title level={4} style={{ margin: '4px 0' }}>{ticket.title}</Title>
                </div>
                <Space>
                  <Tag color={STATUS_COLORS[ticket.status]}>{ticket.status.replace('_', ' ').toUpperCase()}</Tag>
                  <Tag color={ticket.priority === 'P1' ? 'red' : ticket.priority === 'P2' ? 'orange' : 'blue'}>{ticket.priority}</Tag>
                </Space>
              </div>
              {ticket.description && <Text>{ticket.description}</Text>}
            </Space>
          </Card>

          {/* Status Transitions */}
          {canWrite && (
            <Card title="Actions" style={{ marginTop: 16 }}>
              <Space wrap>
                {(TRANSITIONS[ticket.status] || []).map((s) => (
                  <Button key={s} type={s === 'resolved' ? 'primary' : 'default'}
                          danger={s === 'blocked'} onClick={() => statusMutation.mutate(s)}
                          loading={statusMutation.isPending}>
                    {s.replace('_', ' ').toUpperCase()}
                  </Button>
                ))}
              </Space>
            </Card>
          )}

          {/* Comments */}
          <Card title="Comments" style={{ marginTop: 16 }}>
            <Timeline items={(comments || []).map((c) => ({
              color: c.is_internal ? 'gray' : 'blue',
              children: (
                <div key={c.id}>
                  <Text strong>{c.author_name}</Text>
                  {c.is_internal && <Tag style={{ marginLeft: 8 }} color="default">Internal</Tag>}
                  <Text type="secondary" style={{ marginLeft: 8 }}>{dayjs(c.created_at).format('MMM DD, HH:mm')}</Text>
                  <div style={{ marginTop: 4 }}>
                    {c.body.split('\n').map((line: string, i: number) => (
                      <span key={i}>{line}{i < c.body.split('\n').length - 1 && <br />}</span>
                    ))}
                  </div>
                </div>
              ),
            }))} />
            {canWrite && (
              <>
                <Divider />
                <TextArea rows={3} value={commentBody} onChange={(e) => setCommentBody(e.target.value)} placeholder="Add a comment..." />
                <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
                  <Checkbox checked={isInternal} onChange={(e) => setIsInternal(e.target.checked)}>Internal note</Checkbox>
                  <Button type="primary" onClick={() => commentMutation.mutate()} disabled={!commentBody.trim()} loading={commentMutation.isPending}>
                    Add Comment
                  </Button>
                </div>
              </>
            )}
          </Card>
        </Col>

        <Col xs={24} md={8}>
          <Card title="Details">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Reporter">{ticket.reporter_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="Assignee">
                {ticket.assignee_name || 'Unassigned'}
                {!ticket.assignee_id && canWrite && (
                  <Button
                    type="link"
                    size="small"
                    icon={<UserAddOutlined />}
                    onClick={() => assignMutation.mutate()}
                    loading={assignMutation.isPending}
                    style={{ marginLeft: 8, padding: 0 }}
                  >
                    Assign to me
                  </Button>
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Project">{ticket.project_key}</Descriptions.Item>
              <Descriptions.Item label="Created">{dayjs(ticket.created_at).format('MMM DD, YYYY HH:mm')}</Descriptions.Item>
              {ticket.first_response_at && <Descriptions.Item label="First Response">{dayjs(ticket.first_response_at).format('MMM DD, HH:mm')}</Descriptions.Item>}
              {ticket.resolved_at && <Descriptions.Item label="Resolved">{dayjs(ticket.resolved_at).format('MMM DD, HH:mm')}</Descriptions.Item>}
              {ticket.closed_at && <Descriptions.Item label="Closed">{dayjs(ticket.closed_at).format('MMM DD, HH:mm')}</Descriptions.Item>}
            </Descriptions>
          </Card>

          {ticket.sla && (
            <Card title="SLA" style={{ marginTop: 16 }}>
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Response">
                  {ticket.sla.response_met === true && <Tag icon={<CheckCircleOutlined />} color="success">Met</Tag>}
                  {ticket.sla.response_met === false && <Tag icon={<ExclamationCircleOutlined />} color="error">Breached</Tag>}
                  {ticket.sla.response_met === null && <Tag icon={<ClockCircleOutlined />} color="warning">Pending</Tag>}
                </Descriptions.Item>
                <Descriptions.Item label="Response Deadline">
                  {ticket.sla.response_deadline ? dayjs(ticket.sla.response_deadline).format('MMM DD, HH:mm') : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="Resolution">
                  {ticket.sla.resolution_met === true && <Tag icon={<CheckCircleOutlined />} color="success">Met</Tag>}
                  {ticket.sla.resolution_met === false && <Tag icon={<ExclamationCircleOutlined />} color="error">Breached</Tag>}
                  {ticket.sla.resolution_met === null && <Tag icon={<ClockCircleOutlined />} color="warning">Pending</Tag>}
                </Descriptions.Item>
                <Descriptions.Item label="Resolution Deadline">
                  {ticket.sla.resolution_deadline ? dayjs(ticket.sla.resolution_deadline).format('MMM DD, HH:mm') : '-'}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default TicketDetailPage;
