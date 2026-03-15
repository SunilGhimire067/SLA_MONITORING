import React, { useState } from 'react';
import {
  Card, Button, Typography, Tag, Space, Modal, Input, Select,
  message, Empty, Spin, Row, Col, Popconfirm, Collapse, Descriptions,
} from 'antd';
import {
  PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined,
  TagsOutlined, UserOutlined, FilterOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { getArticles, getCategories, createArticle, updateArticle, deleteArticle } from '../api/knowledgebase';
import type { KBArticle } from '../types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const CATEGORY_COLORS: Record<string, string> = {
  VCC: 'purple',
  QR: 'blue',
  IBFT: 'green',
  SETTLEMENT: 'orange',
};

const KnowledgeBasePage: React.FC = () => {
  const { hasRole } = useAuth();
  const queryClient = useQueryClient();
  const canWrite = hasRole('admin', 'manager', 'engineer');

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingArticle, setEditingArticle] = useState<KBArticle | null>(null);
  const [form, setForm] = useState({
    title: '',
    category: '',
    subcategory: '',
    keywords: '',
    problem: '',
    description: '',
    solution: '',
  });

  const { data, isLoading } = useQuery({
    queryKey: ['kb-articles', page, search, categoryFilter],
    queryFn: () => getArticles({ page, per_page: 20, search: search || undefined, category: categoryFilter }),
  });

  const { data: categories } = useQuery({
    queryKey: ['kb-categories'],
    queryFn: getCategories,
  });

  const createMut = useMutation({
    mutationFn: (payload: Partial<KBArticle>) => createArticle(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kb-articles'] });
      queryClient.invalidateQueries({ queryKey: ['kb-categories'] });
      message.success('Article created');
      closeModal();
    },
    onError: () => message.error('Failed to create article'),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<KBArticle> }) => updateArticle(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kb-articles'] });
      queryClient.invalidateQueries({ queryKey: ['kb-categories'] });
      message.success('Article updated');
      closeModal();
    },
    onError: () => message.error('Failed to update article'),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteArticle(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kb-articles'] });
      queryClient.invalidateQueries({ queryKey: ['kb-categories'] });
      message.success('Article deleted');
    },
  });

  const closeModal = () => {
    setModalOpen(false);
    setEditingArticle(null);
    setForm({ title: '', category: '', subcategory: '', keywords: '', problem: '', description: '', solution: '' });
  };

  const openCreate = () => {
    setEditingArticle(null);
    setForm({ title: '', category: '', subcategory: '', keywords: '', problem: '', description: '', solution: '' });
    setModalOpen(true);
  };

  const openEdit = (article: KBArticle) => {
    setEditingArticle(article);
    setForm({
      title: article.title,
      category: article.category,
      subcategory: article.subcategory || '',
      keywords: article.keywords || '',
      problem: article.problem,
      description: article.description || '',
      solution: article.solution,
    });
    setModalOpen(true);
  };

  const handleSubmit = () => {
    if (!form.title.trim() || !form.category.trim() || !form.problem.trim() || !form.solution.trim()) {
      message.warning('Title, Category, Problem, and Solution are required');
      return;
    }
    const payload = {
      title: form.title.trim(),
      category: form.category.trim().toUpperCase(),
      subcategory: form.subcategory.trim() || undefined,
      keywords: form.keywords.trim() || undefined,
      problem: form.problem.trim(),
      description: form.description.trim() || undefined,
      solution: form.solution.trim(),
    };
    if (editingArticle) {
      updateMut.mutate({ id: editingArticle.id, payload });
    } else {
      createMut.mutate(payload);
    }
  };

  const articles = data?.items || [];

  const defaultCategories = ['VCC', 'QR', 'IBFT', 'SETTLEMENT'];
  const allCategories = Array.from(new Set([...defaultCategories, ...(categories || [])]));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, color: '#e2e8f0' }}>Knowledge Base</Title>
        {canWrite && (
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            New Article
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Input
              placeholder="Search articles by title, problem, keywords, or solution..."
              prefix={<SearchOutlined />}
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              allowClear
              style={{ maxWidth: 500 }}
            />
          </Col>
          <Col>
            <Space>
              <FilterOutlined style={{ color: 'rgba(165, 180, 252, 0.7)' }} />
              <Select
                placeholder="Filter by Category"
                allowClear
                value={categoryFilter}
                onChange={(val) => { setCategoryFilter(val); setPage(1); }}
                style={{ width: 180 }}
                options={allCategories.map((c) => ({ label: c, value: c }))}
              />
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Articles */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 60 }}><Spin size="large" /></div>
      ) : articles.length === 0 ? (
        <Card><Empty description="No articles found" /></Card>
      ) : (
        <Space direction="vertical" style={{ width: '100%' }} size={16}>
          {articles.map((article) => (
            <Card key={article.id} hoverable style={{ borderLeft: `3px solid ${getCategoryColor(article.category)}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <Space align="center" style={{ marginBottom: 8 }}>
                    <Text strong style={{ fontSize: 16, color: '#e2e8f0' }}>{article.title}</Text>
                    <Tag color={CATEGORY_COLORS[article.category] || 'default'}>{article.category}</Tag>
                    {article.subcategory && (
                      <Tag color="cyan">{article.subcategory}</Tag>
                    )}
                  </Space>

                  {article.keywords && (
                    <div style={{ marginBottom: 8 }}>
                      <TagsOutlined style={{ color: 'rgba(165, 180, 252, 0.5)', marginRight: 6, fontSize: 12 }} />
                      {article.keywords.split(',').map((kw, i) => (
                        <Tag key={i} style={{ fontSize: 11, borderStyle: 'dashed' }}>{kw.trim()}</Tag>
                      ))}
                    </div>
                  )}
                </div>
                {canWrite && (
                  <Space>
                    <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(article)}>Edit</Button>
                    <Popconfirm title="Delete this article?" onConfirm={() => deleteMut.mutate(article.id)}>
                      <Button size="small" danger icon={<DeleteOutlined />}>Delete</Button>
                    </Popconfirm>
                  </Space>
                )}
              </div>

              <Collapse
                ghost
                items={[{
                  key: 'details',
                  label: <Text type="secondary" style={{ fontSize: 13 }}>View Details</Text>,
                  children: (
                    <div>
                      <Descriptions column={1} size="small" style={{ marginBottom: 12 }}>
                        <Descriptions.Item label="Problem / Question">
                          <Text style={{ whiteSpace: 'pre-wrap' }}>{article.problem}</Text>
                        </Descriptions.Item>
                        {article.description && (
                          <Descriptions.Item label="Description / Background">
                            <Text style={{ whiteSpace: 'pre-wrap' }}>{article.description}</Text>
                          </Descriptions.Item>
                        )}
                        <Descriptions.Item label="Solution / Answer">
                          <Text style={{ whiteSpace: 'pre-wrap' }}>{article.solution}</Text>
                        </Descriptions.Item>
                      </Descriptions>
                      <div style={{ display: 'flex', gap: 24, fontSize: 12, color: 'rgba(165, 180, 252, 0.5)' }}>
                        <span><UserOutlined /> {article.author_name || 'Unknown'}</span>
                        <span>Updated: {new Date(article.updated_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ),
                }]}
              />
            </Card>
          ))}

          {/* Pagination */}
          {(data?.pages || 0) > 1 && (
            <div style={{ textAlign: 'center', marginTop: 16 }}>
              <Space>
                <Button disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
                <Text type="secondary">Page {page} of {data?.pages}</Text>
                <Button disabled={page >= (data?.pages || 1)} onClick={() => setPage(page + 1)}>Next</Button>
              </Space>
            </div>
          )}
        </Space>
      )}

      {/* Create / Edit Modal */}
      <Modal
        title={editingArticle ? 'Edit Article' : 'New Knowledge Base Article'}
        open={modalOpen}
        onCancel={closeModal}
        onOk={handleSubmit}
        okText={editingArticle ? 'Update' : 'Create'}
        confirmLoading={createMut.isPending || updateMut.isPending}
        width={720}
      >
        <Space direction="vertical" style={{ width: '100%' }} size={12}>
          <div>
            <Text type="secondary" style={{ fontSize: 12 }}>Title *</Text>
            <Input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Article title"
            />
          </div>
          <Row gutter={12}>
            <Col span={12}>
              <Text type="secondary" style={{ fontSize: 12 }}>Category *</Text>
              <Select
                value={form.category || undefined}
                onChange={(val) => setForm({ ...form, category: val })}
                placeholder="Select or type category"
                style={{ width: '100%' }}
                showSearch
                options={allCategories.map((c) => ({ label: c, value: c }))}
              />
            </Col>
            <Col span={12}>
              <Text type="secondary" style={{ fontSize: 12 }}>Subcategory</Text>
              <Input
                value={form.subcategory}
                onChange={(e) => setForm({ ...form, subcategory: e.target.value })}
                placeholder="Optional subcategory"
              />
            </Col>
          </Row>
          <div>
            <Text type="secondary" style={{ fontSize: 12 }}>Keywords</Text>
            <Input
              value={form.keywords}
              onChange={(e) => setForm({ ...form, keywords: e.target.value })}
              placeholder="e.g. #cardwithdraw, #settlement, #slowqr"
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12 }}>Problem / Question *</Text>
            <TextArea
              value={form.problem}
              onChange={(e) => setForm({ ...form, problem: e.target.value })}
              placeholder="Describe the issue or question"
              rows={3}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12 }}>Description / Background</Text>
            <TextArea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Optional context or explanation"
              rows={2}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12 }}>Solution / Answer *</Text>
            <TextArea
              value={form.solution}
              onChange={(e) => setForm({ ...form, solution: e.target.value })}
              placeholder="Step-by-step solution or explanation"
              rows={4}
            />
          </div>
        </Space>
      </Modal>
    </div>
  );
};

function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    VCC: '#a855f7',
    QR: '#3b82f6',
    IBFT: '#10b981',
    SETTLEMENT: '#f59e0b',
  };
  return colors[category] || '#6366f1';
}

export default KnowledgeBasePage;
