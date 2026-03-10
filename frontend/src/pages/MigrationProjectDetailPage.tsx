import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Button, Typography, Tag, Space, Modal, Input, Select, DatePicker,
  Progress, Collapse, Descriptions, Tooltip, message, Empty, Spin,
  Row, Col, Popconfirm,
} from 'antd';
import {
  PlusOutlined, ArrowLeftOutlined, FilePdfOutlined, EditOutlined,
  DeleteOutlined, LinkOutlined, RocketOutlined, CheckCircleOutlined,
  ClockCircleOutlined, PauseCircleOutlined, ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getMigrationProject, updateMigrationProject,
  createMigrationService, updateMigrationService, deleteMigrationService,
  updateMigrationPhase, addDependency, removeDependency,
  exportMigrationPDF,
} from '../api/migration';
import { getAssignees } from '../api/users';
import { useAuth } from '../context/AuthContext';
import type { MigrationProject, MigrationService } from '../types';
import dayjs from 'dayjs';

const { Title, Text, Paragraph } = Typography;

const STATUS_COLORS: Record<string, string> = {
  draft: 'default', active: 'processing', completed: 'success', on_hold: 'warning',
  pending: 'default', in_progress: 'processing', blocked: 'error',
  not_started: 'default',
};

const STATUS_ICONS: Record<string, React.ReactNode> = {
  not_started: <ClockCircleOutlined />,
  in_progress: <RocketOutlined spin />,
  completed: <CheckCircleOutlined />,
  blocked: <ExclamationCircleOutlined />,
  pending: <PauseCircleOutlined />,
};

const PHASE_COLORS: Record<string, string> = {
  planning: '#6366f1',
  preparation: '#f59e0b',
  migration: '#10b981',
  validation: '#8b5cf6',
};

const MigrationProjectDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const canWrite = hasRole('admin', 'manager', 'engineer');

  const [editProjectOpen, setEditProjectOpen] = useState(false);
  const [addServiceOpen, setAddServiceOpen] = useState(false);
  const [editServiceId, setEditServiceId] = useState<number | null>(null);
  const [depModalServiceId, setDepModalServiceId] = useState<number | null>(null);
  const [depTarget, setDepTarget] = useState<number | undefined>();
  const [projectForm, setProjectForm] = useState<any>({});
  const [serviceForm, setServiceForm] = useState<any>({});
  const [editServiceForm, setEditServiceForm] = useState<any>({});

  const { data: project, isLoading } = useQuery<MigrationProject>({
    queryKey: ['migration-project', id],
    queryFn: () => getMigrationProject(Number(id)),
    enabled: !!id,
  });

  const { data: assignees } = useQuery({
    queryKey: ['assignees'],
    queryFn: getAssignees,
  });

  // Mutations
  const updateProjectMut = useMutation({
    mutationFn: (payload: any) => updateMigrationProject(Number(id), payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migration-project', id] });
      setEditProjectOpen(false);
      message.success('Project updated');
    },
    onError: () => message.error('Failed to update project'),
  });

  const addServiceMut = useMutation({
    mutationFn: (payload: any) => createMigrationService(Number(id), payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migration-project', id] });
      setAddServiceOpen(false);
      setServiceForm({});
      message.success('Service added');
    },
    onError: () => message.error('Failed to add service'),
  });

  const updateServiceMut = useMutation({
    mutationFn: ({ sid, payload }: { sid: number; payload: any }) =>
      updateMigrationService(sid, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migration-project', id] });
      setEditServiceId(null);
      message.success('Service updated');
    },
  });

  const deleteServiceMut = useMutation({
    mutationFn: (sid: number) => deleteMigrationService(sid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migration-project', id] });
      message.success('Service deleted');
    },
  });

  const updatePhaseMut = useMutation({
    mutationFn: ({ pid, payload, serviceId }: { pid: number; payload: any; serviceId?: number }) =>
      updateMigrationPhase(pid, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['migration-project', id] }).then(() => {
        // Auto-complete service if all 4 phases are completed
        if (variables.payload.status === 'completed' && variables.serviceId && project) {
          const svc = project.services.find(s => s.id === variables.serviceId);
          if (svc) {
            const allCompleted = svc.phases.every(p =>
              p.id === variables.pid ? variables.payload.status === 'completed' : p.status === 'completed'
            );
            if (allCompleted && svc.status !== 'completed') {
              updateServiceMut.mutate({ sid: svc.id, payload: { status: 'completed' } });
            }
          }
        }
      });
      message.success('Phase updated');
    },
  });

  const addDepMut = useMutation({
    mutationFn: ({ sid, depId }: { sid: number; depId: number }) =>
      addDependency(sid, depId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migration-project', id] });
      setDepModalServiceId(null);
      setDepTarget(undefined);
      message.success('Dependency added');
    },
    onError: (err: any) =>
      message.error(err?.response?.data?.detail || 'Failed to add dependency'),
  });

  const removeDepMut = useMutation({
    mutationFn: (depId: number) => removeDependency(depId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['migration-project', id] });
      message.success('Dependency removed');
    },
  });

  const handleExportPDF = async () => {
    try {
      const response = await exportMigrationPDF(Number(id));
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `migration_timeline_${project?.name?.replace(/\s+/g, '_').toLowerCase() || id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      message.success('PDF downloaded');
    } catch {
      message.error('Failed to export PDF');
    }
  };

  const calcServiceProgress = (svc: MigrationService) => {
    if (!svc.phases?.length) return 0;
    const completed = svc.phases.filter(p => p.status === 'completed').length;
    return Math.round((completed / svc.phases.length) * 100);
  };

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>;
  }

  if (!project) {
    return <Empty description="Project not found" />;
  }

  const sortedServices = [...(project.services || [])].sort((a, b) => a.order - b.order);

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <Space direction="vertical" size={4}>
          <Space>
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/migration')}
              style={{ padding: '4px 8px' }}
            />
            <Title level={3} style={{ margin: 0 }}>{project.name}</Title>
            <Tag color={STATUS_COLORS[project.status] || 'default'}>
              {project.status.replace('_', ' ').toUpperCase()}
            </Tag>
          </Space>
          {project.description && (
            <Paragraph type="secondary" style={{ margin: 0, paddingLeft: 40 }}>
              {project.description}
            </Paragraph>
          )}
        </Space>
        <Space>
          <Button icon={<FilePdfOutlined />} onClick={handleExportPDF}>Export PDF</Button>
          {canWrite && (
            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={() => {
                setProjectForm({
                  name: project.name,
                  description: project.description || '',
                  owner_id: project.owner_id,
                  status: project.status,
                  start_date: project.start_date || '',
                  end_date: project.end_date || '',
                });
                setEditProjectOpen(true);
              }}
            >
              Edit Project
            </Button>
          )}
        </Space>
      </div>

      {/* Project Info Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card size="small">
            <Text type="secondary" style={{ fontSize: 12 }}>Owner</Text>
            <div><Text strong>{project.owner_name || 'Unassigned'}</Text></div>
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Text type="secondary" style={{ fontSize: 12 }}>Services</Text>
            <div><Text strong style={{ fontSize: 20 }}>{project.services?.length || 0}</Text></div>
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Text type="secondary" style={{ fontSize: 12 }}>Timeline</Text>
            <div>
              <Text strong style={{ fontSize: 13 }}>
                {project.start_date ? dayjs(project.start_date).format('MMM DD') : 'TBD'}
                {' - '}
                {project.end_date ? dayjs(project.end_date).format('MMM DD, YYYY') : 'TBD'}
              </Text>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small">
            <Text type="secondary" style={{ fontSize: 12 }}>Overall Progress</Text>
            <Progress
              percent={
                sortedServices.length
                  ? Math.round(
                      sortedServices.reduce((a, s) => a + calcServiceProgress(s), 0) /
                        sortedServices.length
                    )
                  : 0
              }
              strokeColor={{ '0%': '#6366f1', '100%': '#a855f7' }}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      {/* Visual Timeline */}
      {sortedServices.length > 0 && (
        <Card title="Migration Timeline" style={{ marginBottom: 24 }}>
          <div style={{ overflowX: 'auto' }}>
            {sortedServices.map((svc) => (
              <div key={svc.id} style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                <div style={{ width: 180, flexShrink: 0, paddingRight: 16 }}>
                  <Text strong style={{ fontSize: 13 }}>{svc.name}</Text>
                  <div>
                    <Text type="secondary" style={{ fontSize: 11 }}>
                      {svc.assignee_name || 'Unassigned'}
                    </Text>
                  </div>
                </div>
                <div style={{ flex: 1, display: 'flex', gap: 3, height: 32 }}>
                  {(svc.phases || [])
                    .sort((a, b) => {
                      const order = ['planning', 'preparation', 'migration', 'validation'];
                      return order.indexOf(a.phase_type) - order.indexOf(b.phase_type);
                    })
                    .map((phase) => {
                      const color = PHASE_COLORS[phase.phase_type] || '#6366f1';
                      const opacity = phase.status === 'completed' ? 1 : phase.status === 'in_progress' ? 0.7 : 0.25;
                      return (
                        <Tooltip
                          key={phase.id}
                          title={`${phase.phase_type.replace('_', ' ').toUpperCase()} - ${phase.status.replace('_', ' ')}`}
                        >
                          <div
                            style={{
                              flex: 1,
                              background: color,
                              opacity,
                              borderRadius: 4,
                              position: 'relative',
                              overflow: 'hidden',
                              cursor: 'default',
                            }}
                          >
                            <div style={{
                              position: 'absolute',
                              inset: 0,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: '#fff',
                              fontSize: 10,
                              fontWeight: 600,
                              textTransform: 'uppercase',
                              letterSpacing: 0.5,
                            }}>
                              {phase.phase_type.substring(0, 4)}
                            </div>
                          </div>
                        </Tooltip>
                      );
                    })}
                </div>
                <div style={{ width: 80, textAlign: 'right', flexShrink: 0, paddingLeft: 12 }}>
                  <Text strong style={{ fontSize: 13 }}>{calcServiceProgress(svc)}%</Text>
                </div>
              </div>
            ))}
            {/* Legend */}
            <div style={{ display: 'flex', gap: 16, marginTop: 12, paddingLeft: 180 }}>
              {Object.entries(PHASE_COLORS).map(([name, color]) => (
                <Space key={name} size={4}>
                  <div style={{ width: 12, height: 12, borderRadius: 3, background: color }} />
                  <Text type="secondary" style={{ fontSize: 11, textTransform: 'capitalize' }}>{name}</Text>
                </Space>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Services List */}
      <Card
        title={`Services (${sortedServices.length})`}
        extra={
          canWrite && (
            <Button type="primary" size="small" icon={<PlusOutlined />} onClick={() => setAddServiceOpen(true)}>
              Add Service
            </Button>
          )
        }
      >
        {sortedServices.length === 0 ? (
          <Empty description="No services added yet" />
        ) : (
          <Collapse
            accordion
            items={sortedServices.map((svc) => ({
              key: svc.id,
              label: (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', paddingRight: 16 }}>
                  <Space>
                    {STATUS_ICONS[svc.status] || STATUS_ICONS.pending}
                    <Text strong>{svc.name}</Text>
                    <Tag color={STATUS_COLORS[svc.status] || 'default'} style={{ fontSize: 11 }}>
                      {svc.status.replace('_', ' ').toUpperCase()}
                    </Tag>
                    {svc.assignee_name && (
                      <Tag color="purple" style={{ fontSize: 11 }}>{svc.assignee_name}</Tag>
                    )}
                  </Space>
                  <Space>
                    <Progress
                      percent={calcServiceProgress(svc)}
                      size="small"
                      style={{ width: 120 }}
                      strokeColor={{ '0%': '#6366f1', '100%': '#10b981' }}
                    />
                    {svc.expected_duration_days && (
                      <Text type="secondary" style={{ fontSize: 11 }}>{svc.expected_duration_days}d</Text>
                    )}
                  </Space>
                </div>
              ),
              children: (
                <div>
                  {svc.description && (
                    <Paragraph type="secondary" style={{ marginBottom: 16 }}>{svc.description}</Paragraph>
                  )}

                  <Descriptions size="small" column={4} style={{ marginBottom: 16 }}>
                    <Descriptions.Item label="Start Date">
                      {svc.start_date ? dayjs(svc.start_date).format('MMM DD, YYYY') : 'TBD'}
                    </Descriptions.Item>
                    <Descriptions.Item label="End Date">
                      {svc.end_date ? dayjs(svc.end_date).format('MMM DD, YYYY') : 'TBD'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Duration">
                      {svc.expected_duration_days ? `${svc.expected_duration_days} days` : 'TBD'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Assignee">
                      {svc.assignee_name || 'Unassigned'}
                    </Descriptions.Item>
                  </Descriptions>

                  {/* Dependencies */}
                  {(svc.dependencies?.length > 0) && (
                    <div style={{ marginBottom: 16 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>Dependencies:</Text>
                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 4 }}>
                        {svc.dependencies.map((dep) => (
                          <Tag
                            key={dep.id}
                            color="blue"
                            closable={canWrite}
                            onClose={() => removeDepMut.mutate(dep.id)}
                          >
                            <LinkOutlined /> {dep.depends_on_name || `Service #${dep.depends_on_id}`}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Phases */}
                  <div style={{ marginBottom: 16 }}>
                    <Text strong style={{ fontSize: 13, display: 'block', marginBottom: 8 }}>Migration Phases</Text>
                    <Row gutter={[12, 12]}>
                      {(svc.phases || [])
                        .sort((a, b) => {
                          const order = ['planning', 'preparation', 'migration', 'validation'];
                          return order.indexOf(a.phase_type) - order.indexOf(b.phase_type);
                        })
                        .map((phase) => (
                          <Col span={6} key={phase.id}>
                            <Card
                              size="small"
                              style={{
                                borderLeft: `3px solid ${PHASE_COLORS[phase.phase_type] || '#6366f1'}`,
                              }}
                            >
                              <div style={{ marginBottom: 8 }}>
                                <Text strong style={{ textTransform: 'capitalize', fontSize: 13 }}>
                                  {phase.phase_type}
                                </Text>
                                <Tag
                                  color={STATUS_COLORS[phase.status] || 'default'}
                                  style={{ marginLeft: 8, fontSize: 10 }}
                                >
                                  {phase.status.replace('_', ' ')}
                                </Tag>
                              </div>
                              {phase.notes && (
                                <Text type="secondary" style={{ fontSize: 11, display: 'block', marginTop: 4 }}>
                                  {phase.notes}
                                </Text>
                              )}
                              {canWrite && (
                                <div style={{ marginTop: 8 }}>
                                  <Select
                                    size="small"
                                    value={phase.status}
                                    style={{ width: '100%' }}
                                    onChange={(val) =>
                                      updatePhaseMut.mutate({ pid: phase.id, payload: { status: val }, serviceId: svc.id })
                                    }
                                    options={[
                                      { label: 'Not Started', value: 'not_started' },
                                      { label: 'In Progress', value: 'in_progress' },
                                      { label: 'Completed', value: 'completed' },
                                      { label: 'Blocked', value: 'blocked' },
                                    ]}
                                  />
                                </div>
                              )}
                            </Card>
                          </Col>
                        ))}
                    </Row>
                  </div>

                  {/* Service Actions */}
                  {canWrite && (
                    <Space>
                      <Button
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => {
                          setEditServiceId(svc.id);
                          setEditServiceForm({
                            name: svc.name,
                            description: svc.description || '',
                            assignee_id: svc.assignee_id,
                            status: svc.status,
                            expected_duration_days: svc.expected_duration_days,
                            start_date: svc.start_date || '',
                            end_date: svc.end_date || '',
                          });
                        }}
                      >
                        Edit Service
                      </Button>
                      <Button
                        size="small"
                        icon={<LinkOutlined />}
                        onClick={() => setDepModalServiceId(svc.id)}
                      >
                        Add Dependency
                      </Button>
                      <Popconfirm
                        title="Delete this service?"
                        onConfirm={() => deleteServiceMut.mutate(svc.id)}
                      >
                        <Button size="small" danger icon={<DeleteOutlined />}>
                          Delete
                        </Button>
                      </Popconfirm>
                    </Space>
                  )}
                </div>
              ),
            }))}
          />
        )}
      </Card>

      {/* Edit Project Modal */}
      <Modal
        title="Edit Migration Project"
        open={editProjectOpen}
        onCancel={() => setEditProjectOpen(false)}
        onOk={() => updateProjectMut.mutate(projectForm)}
        okText="Save"
        confirmLoading={updateProjectMut.isPending}
        width={560}
      >
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Project Name</Text>
            <Input
              value={projectForm.name}
              onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Description</Text>
            <Input.TextArea
              value={projectForm.description}
              onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
              rows={3}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Status</Text>
            <Select
              value={projectForm.status}
              style={{ width: '100%' }}
              onChange={(val) => setProjectForm({ ...projectForm, status: val })}
              options={[
                { label: 'Draft', value: 'draft' },
                { label: 'Active', value: 'active' },
                { label: 'Completed', value: 'completed' },
                { label: 'On Hold', value: 'on_hold' },
              ]}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Owner</Text>
            <Select
              value={projectForm.owner_id}
              allowClear
              style={{ width: '100%' }}
              onChange={(val) => setProjectForm({ ...projectForm, owner_id: val })}
              options={(assignees || []).map((u: any) => ({
                label: `${u.first_name} ${u.last_name}`,
                value: u.id,
              }))}
            />
          </div>
          <Space size={12}>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Start Date</Text>
              <DatePicker
                value={projectForm.start_date ? dayjs(projectForm.start_date) : undefined}
                onChange={(_d, ds) => setProjectForm({ ...projectForm, start_date: ds as string })}
                style={{ width: 180 }}
              />
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>End Date</Text>
              <DatePicker
                value={projectForm.end_date ? dayjs(projectForm.end_date) : undefined}
                onChange={(_d, ds) => setProjectForm({ ...projectForm, end_date: ds as string })}
                style={{ width: 180 }}
              />
            </div>
          </Space>
        </Space>
      </Modal>

      {/* Add Service Modal */}
      <Modal
        title="Add Service"
        open={addServiceOpen}
        onCancel={() => { setAddServiceOpen(false); setServiceForm({}); }}
        onOk={() => {
          if (!serviceForm.name?.trim()) {
            message.warning('Service name is required');
            return;
          }
          addServiceMut.mutate(serviceForm);
        }}
        okText="Add"
        confirmLoading={addServiceMut.isPending}
        width={560}
      >
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Service/Application Name *</Text>
            <Input
              placeholder="e.g. user-auth-service"
              value={serviceForm.name}
              onChange={(e) => setServiceForm({ ...serviceForm, name: e.target.value })}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Description</Text>
            <Input.TextArea
              placeholder="Describe the service..."
              value={serviceForm.description}
              onChange={(e) => setServiceForm({ ...serviceForm, description: e.target.value })}
              rows={2}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Assign To (Engineer)</Text>
            <Select
              placeholder="Select engineer"
              allowClear
              style={{ width: '100%' }}
              value={serviceForm.assignee_id}
              onChange={(val) => setServiceForm({ ...serviceForm, assignee_id: val })}
              options={(assignees || []).map((u: any) => ({
                label: `${u.first_name} ${u.last_name}`,
                value: u.id,
              }))}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Expected Duration (days)</Text>
            <Input
              type="number"
              placeholder="e.g. 14"
              value={serviceForm.expected_duration_days}
              onChange={(e) => setServiceForm({ ...serviceForm, expected_duration_days: e.target.value ? Number(e.target.value) : undefined })}
              style={{ width: 140 }}
            />
          </div>
          <Space size={12}>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Start Date</Text>
              <DatePicker
                onChange={(_d, ds) => setServiceForm({ ...serviceForm, start_date: ds as string })}
                style={{ width: 180 }}
              />
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>End Date</Text>
              <DatePicker
                onChange={(_d, ds) => setServiceForm({ ...serviceForm, end_date: ds as string })}
                style={{ width: 180 }}
              />
            </div>
          </Space>
        </Space>
      </Modal>

      {/* Edit Service Modal */}
      <Modal
        title="Edit Service"
        open={editServiceId !== null}
        onCancel={() => setEditServiceId(null)}
        onOk={() => updateServiceMut.mutate({ sid: editServiceId!, payload: editServiceForm })}
        okText="Save"
        confirmLoading={updateServiceMut.isPending}
        width={560}
      >
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Name</Text>
            <Input
              value={editServiceForm.name}
              onChange={(e) => setEditServiceForm({ ...editServiceForm, name: e.target.value })}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Description</Text>
            <Input.TextArea
              value={editServiceForm.description}
              onChange={(e) => setEditServiceForm({ ...editServiceForm, description: e.target.value })}
              rows={2}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Status</Text>
            <Select
              value={editServiceForm.status}
              style={{ width: '100%' }}
              onChange={(val) => setEditServiceForm({ ...editServiceForm, status: val })}
              options={[
                { label: 'Pending', value: 'pending' },
                { label: 'In Progress', value: 'in_progress' },
                { label: 'Completed', value: 'completed' },
                { label: 'Blocked', value: 'blocked' },
              ]}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Assignee</Text>
            <Select
              value={editServiceForm.assignee_id}
              allowClear
              style={{ width: '100%' }}
              onChange={(val) => setEditServiceForm({ ...editServiceForm, assignee_id: val })}
              options={(assignees || []).map((u: any) => ({
                label: `${u.first_name} ${u.last_name}`,
                value: u.id,
              }))}
            />
          </div>
          <div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Expected Duration (days)</Text>
            <Input
              type="number"
              value={editServiceForm.expected_duration_days}
              onChange={(e) => setEditServiceForm({ ...editServiceForm, expected_duration_days: e.target.value ? Number(e.target.value) : undefined })}
              style={{ width: 140 }}
            />
          </div>
          <Space size={12}>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>Start Date</Text>
              <DatePicker
                value={editServiceForm.start_date ? dayjs(editServiceForm.start_date) : undefined}
                onChange={(_d, ds) => setEditServiceForm({ ...editServiceForm, start_date: ds as string })}
                style={{ width: 180 }}
              />
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>End Date</Text>
              <DatePicker
                value={editServiceForm.end_date ? dayjs(editServiceForm.end_date) : undefined}
                onChange={(_d, ds) => setEditServiceForm({ ...editServiceForm, end_date: ds as string })}
                style={{ width: 180 }}
              />
            </div>
          </Space>
        </Space>
      </Modal>

      {/* Add Dependency Modal */}
      <Modal
        title="Add Dependency"
        open={depModalServiceId !== null}
        onCancel={() => { setDepModalServiceId(null); setDepTarget(undefined); }}
        onOk={() => {
          if (!depTarget) {
            message.warning('Select a service');
            return;
          }
          addDepMut.mutate({ sid: depModalServiceId!, depId: depTarget });
        }}
        okText="Add"
        confirmLoading={addDepMut.isPending}
        width={440}
      >
        <div>
          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 4 }}>
            This service depends on:
          </Text>
          <Select
            placeholder="Select service"
            style={{ width: '100%' }}
            value={depTarget}
            onChange={(val) => setDepTarget(val)}
            options={sortedServices
              .filter((s) => s.id !== depModalServiceId)
              .map((s) => ({ label: s.name, value: s.id }))}
          />
        </div>
      </Modal>
    </div>
  );
};

export default MigrationProjectDetailPage;
