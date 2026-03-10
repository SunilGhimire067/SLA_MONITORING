import { useState } from 'react';
import { Card, Button, Input, Space, Typography, List, Modal, message, Empty, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, FileTextOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMemos, createMemo, updateMemo, deleteMemo } from '../api/memos';
import type { Memo } from '../api/memos';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const MemosPage = () => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingMemo, setEditingMemo] = useState<Memo | null>(null);
  const [viewingMemo, setViewingMemo] = useState<Memo | null>(null);
  const [form, setForm] = useState({ title: '', content: '' });

  const { data, isLoading } = useQuery({
    queryKey: ['memos', search],
    queryFn: () => getMemos({ per_page: 50, search: search || undefined }),
  });

  const createMutation = useMutation({
    mutationFn: () => createMemo(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memos'] });
      setModalOpen(false);
      setForm({ title: '', content: '' });
      message.success('Memo created');
    },
  });

  const updateMutation = useMutation({
    mutationFn: () => updateMemo(editingMemo!.id, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memos'] });
      setEditingMemo(null);
      setModalOpen(false);
      setForm({ title: '', content: '' });
      message.success('Memo updated');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteMemo(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memos'] });
      message.success('Memo deleted');
    },
  });

  const openCreate = () => {
    setEditingMemo(null);
    setForm({ title: '', content: '' });
    setModalOpen(true);
  };

  const openEdit = (memo: Memo) => {
    setEditingMemo(memo);
    setForm({ title: memo.title, content: memo.content });
    setModalOpen(true);
  };

  const handleSave = () => {
    if (!form.title.trim()) {
      message.warning('Title is required');
      return;
    }
    if (editingMemo) {
      updateMutation.mutate();
    } else {
      createMutation.mutate();
    }
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: 'Delete this memo?',
      content: 'This action cannot be undone.',
      okText: 'Delete',
      okButtonProps: { danger: true },
      onOk: () => deleteMutation.mutate(id),
    });
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3} style={{ margin: 0 }}>Memos</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          New Memo
        </Button>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Input
          placeholder="Search memos..."
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          onChange={(e) => setSearch(e.target.value)}
          allowClear
        />
      </Card>

      <List
        loading={isLoading}
        grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
        dataSource={data?.items || []}
        locale={{ emptyText: <Empty description="No memos yet. Create one to get started!" /> }}
        renderItem={(memo: Memo) => (
          <List.Item>
            <Card
              hoverable
              onClick={() => setViewingMemo(memo)}
              actions={[
                <EditOutlined key="edit" onClick={(e) => { e.stopPropagation(); openEdit(memo); }} />,
                <DeleteOutlined key="delete" onClick={(e) => { e.stopPropagation(); handleDelete(memo.id); }} />,
              ]}
            >
              <Card.Meta
                avatar={
                  <div style={{
                    width: 40, height: 40, borderRadius: 10,
                    background: 'rgba(99, 102, 241, 0.15)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <FileTextOutlined style={{ fontSize: 18, color: '#818cf8' }} />
                  </div>
                }
                title={<Text strong style={{ fontSize: 15 }}>{memo.title}</Text>}
                description={
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <Paragraph
                      ellipsis={{ rows: 3 }}
                      style={{ marginBottom: 0, color: 'rgba(255,255,255,0.6)', fontSize: 13 }}
                    >
                      {memo.content || 'No content'}
                    </Paragraph>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                      <Tag color="purple" style={{ fontSize: 11 }}>{memo.author_name}</Tag>
                      <Text type="secondary" style={{ fontSize: 11 }}>
                        {dayjs(memo.updated_at).format('MMM DD, YYYY HH:mm')}
                      </Text>
                    </div>
                  </Space>
                }
              />
            </Card>
          </List.Item>
        )}
      />

      {/* Create / Edit Modal */}
      <Modal
        title={editingMemo ? 'Edit Memo' : 'New Memo'}
        open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditingMemo(null); }}
        onOk={handleSave}
        okText={editingMemo ? 'Update' : 'Create'}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        width={600}
      >
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <Input
            placeholder="Memo title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
          <TextArea
            placeholder="Write your memo here..."
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
            rows={10}
            style={{ resize: 'vertical' }}
          />
        </Space>
      </Modal>

      {/* View Modal */}
      <Modal
        title={viewingMemo?.title}
        open={!!viewingMemo}
        onCancel={() => setViewingMemo(null)}
        footer={[
          <Button key="edit" type="primary" onClick={() => { if (viewingMemo) { openEdit(viewingMemo); setViewingMemo(null); } }}>
            Edit
          </Button>,
          <Button key="close" onClick={() => setViewingMemo(null)}>Close</Button>,
        ]}
        width={700}
      >
        {viewingMemo && (
          <div>
            <div style={{ marginBottom: 12, display: 'flex', gap: 12, alignItems: 'center' }}>
              <Tag color="purple">{viewingMemo.author_name}</Tag>
              <Text type="secondary" style={{ fontSize: 12 }}>
                Created {dayjs(viewingMemo.created_at).format('MMM DD, YYYY HH:mm')}
                {viewingMemo.updated_at !== viewingMemo.created_at &&
                  ` · Updated ${dayjs(viewingMemo.updated_at).format('MMM DD, YYYY HH:mm')}`}
              </Text>
            </div>
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7, color: 'rgba(255,255,255,0.85)' }}>
              {viewingMemo.content || 'No content'}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default MemosPage;
