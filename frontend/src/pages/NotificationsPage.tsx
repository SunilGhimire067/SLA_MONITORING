import { Card, List, Tag, Button, Typography, Empty, message } from 'antd';
import { BellOutlined, CheckOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getNotifications, markRead, markAllRead } from '../api/notifications';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const TYPE_COLORS: Record<string, string> = {
  sla_breach: 'red', sla_warning: 'orange', assignment: 'blue', status_change: 'green', escalation: 'purple', comment: 'cyan',
};

const NotificationsPage = () => {
  const queryClient = useQueryClient();
  const { data: notifications, isLoading } = useQuery({ queryKey: ['notifications'], queryFn: () => getNotifications() });

  const markReadMutation = useMutation({
    mutationFn: markRead,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['notifications'] }); queryClient.invalidateQueries({ queryKey: ['notifications', 'unread'] }); },
  });

  const markAllMutation = useMutation({
    mutationFn: markAllRead,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['notifications'] }); queryClient.invalidateQueries({ queryKey: ['notifications', 'unread'] }); message.success('All marked as read'); },
  });

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3} style={{ margin: 0 }}>Notifications</Title>
        <Button icon={<CheckOutlined />} onClick={() => markAllMutation.mutate()}>Mark All Read</Button>
      </div>
      <Card>
        {(!notifications || notifications.length === 0) ? (
          <Empty description="No notifications" />
        ) : (
          <List dataSource={notifications} renderItem={(item) => (
            <List.Item
              style={{ background: item.is_read ? 'transparent' : 'rgba(99, 102, 241, 0.08)', padding: '12px 16px', borderRadius: 12, marginBottom: 8, border: item.is_read ? 'none' : '1px solid rgba(99, 102, 241, 0.15)' }}
              actions={!item.is_read ? [<Button size="small" onClick={() => markReadMutation.mutate(item.id)}>Mark Read</Button>] : []}
            >
              <List.Item.Meta
                avatar={<BellOutlined style={{ fontSize: 20, color: TYPE_COLORS[item.type] || '#1677ff' }} />}
                title={<><Text strong={!item.is_read}>{item.title}</Text> <Tag color={TYPE_COLORS[item.type]}>{item.type.replace('_', ' ')}</Tag></>}
                description={<><Text type="secondary">{item.message}</Text><br /><Text type="secondary" style={{ fontSize: 12 }}>{dayjs(item.created_at).format('MMM DD, YYYY HH:mm')}</Text></>}
              />
            </List.Item>
          )} />
        )}
      </Card>
    </div>
  );
};

export default NotificationsPage;
