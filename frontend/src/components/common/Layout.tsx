import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout as AntLayout, Menu, Avatar, Dropdown, Badge, Typography, Tooltip } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  UserOutlined,
  TeamOutlined,
  ProjectOutlined,
  SettingOutlined,
  BellOutlined,
  AuditOutlined,
  SafetyCertificateOutlined,
  LockOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useQuery } from '@tanstack/react-query';
import { getUnreadCount } from '../../api/notifications';

const { Sider, Content } = AntLayout;

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasRole } = useAuth();
  const { getBackground, settings } = useTheme();

  const { data: unreadData } = useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: getUnreadCount,
    refetchInterval: 30000,
  });

  const allMenuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Dashboard', roles: ['admin', 'manager', 'engineer', 'viewer'] },
    { key: '/tickets', icon: <FileTextOutlined />, label: 'Tickets', roles: ['admin', 'manager', 'engineer', 'viewer'] },
    { key: '/projects', icon: <ProjectOutlined />, label: 'Projects', roles: ['admin', 'manager'] },
    { key: '/users', icon: <UserOutlined />, label: 'Users', roles: ['admin'] },
    { key: '/teams', icon: <TeamOutlined />, label: 'Teams', roles: ['admin', 'manager'] },
    {
      key: 'sla', icon: <SafetyCertificateOutlined />, label: 'SLA',
      roles: ['admin', 'manager', 'engineer', 'viewer'],
      children: [
        { key: '/dashboard/sla', label: 'SLA Dashboard' },
        ...(hasRole('admin', 'manager') ? [{ key: '/sla/config', label: 'SLA Config' }] : []),
      ],
    },
    { key: '/notifications', icon: <BellOutlined />, label: 'Notifications', roles: ['admin', 'manager', 'engineer', 'viewer'] },
    { key: '/audit', icon: <AuditOutlined />, label: 'Audit Logs', roles: ['admin', 'manager'] },
    { key: '/roles', icon: <LockOutlined />, label: 'Role Permissions', roles: ['admin'] },
    { key: '/settings', icon: <SettingOutlined />, label: 'Settings', roles: ['admin', 'manager', 'engineer', 'viewer'] },
  ];

  const menuItems = allMenuItems.filter((item) => item.roles.some((r) => hasRole(r)));

  const userMenu = {
    items: [
      { key: 'profile', label: `${user?.first_name} ${user?.last_name}`, disabled: true },
      { key: 'role', label: `Role: ${user?.role}`, disabled: true },
      { type: 'divider' as const },
      { key: 'logout', icon: <LogoutOutlined />, label: 'Logout', danger: true },
    ],
    onClick: ({ key }: { key: string }) => {
      if (key === 'logout') {
        logout();
        navigate('/login');
      }
    },
  };

  return (
    <div style={{ minHeight: '100vh', background: getBackground(), position: 'relative', overflow: 'hidden' }}>
      {/* Animated background orbs */}
      <div className="app-background" />
      <div className="orb-3" />
      <div className="orb-4" />

      {/* Background image overlay */}
      {settings.showBgImage && (
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundImage: 'url(/background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          opacity: settings.bgImageOpacity,
          zIndex: 0,
          pointerEvents: 'none',
        }} />
      )}

      <AntLayout style={{ minHeight: '100vh', background: 'transparent', position: 'relative', zIndex: 1 }}>
        {/* Glass Sidebar */}
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          width={260}
          collapsedWidth={72}
          className="glass-sidebar"
          style={{
            background: 'linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.04) 50%, rgba(15, 12, 40, 0.3) 100%)',
            backdropFilter: 'blur(24px) saturate(1.6)',
            WebkitBackdropFilter: 'blur(24px) saturate(1.6)',
            borderRight: '1px solid rgba(129, 140, 248, 0.1)',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
            zIndex: 100,
            overflow: 'auto',
          }}
        >
          {/* Logo */}
          <div style={{
            height: 68,
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'flex-start',
            borderBottom: '1px solid rgba(129, 140, 248, 0.08)',
            padding: collapsed ? '0' : '0 20px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              overflow: 'hidden',
            }}>
              <div style={{
                width: 38,
                height: 38,
                borderRadius: 12,
                background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                boxShadow: '0 4px 16px rgba(99, 102, 241, 0.4), inset 0 1px 0 rgba(255,255,255,0.2)',
              }}>
                <ThunderboltOutlined style={{ fontSize: 18, color: '#fff' }} />
              </div>
              {!collapsed && (
                <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
                  <Typography.Text strong style={{
                    color: '#fff',
                    fontSize: 15,
                    letterSpacing: '-0.3px',
                    whiteSpace: 'nowrap',
                  }}>
                    DevOps ITSM
                  </Typography.Text>
                  <Typography.Text style={{
                    color: 'rgba(165, 180, 252, 0.7)',
                    fontSize: 10,
                    letterSpacing: '1px',
                    textTransform: 'uppercase',
                    whiteSpace: 'nowrap',
                  }}>
                    SLA Monitoring
                  </Typography.Text>
                </div>
              )}
            </div>
          </div>

          {/* Navigation Menu */}
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            style={{
              background: 'transparent',
              border: 'none',
              padding: '12px 0',
            }}
          />

          {/* Sidebar collapse toggle */}
          <div
            onClick={() => setCollapsed(!collapsed)}
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: 48,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              borderTop: '1px solid rgba(129, 140, 248, 0.08)',
              color: 'rgba(165, 180, 252, 0.5)',
              transition: 'color 0.3s, background 0.3s',
            }}
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </div>
        </Sider>

        {/* Main Content Area */}
        <AntLayout style={{
          marginLeft: collapsed ? 72 : 260,
          background: 'transparent',
          transition: 'margin-left 0.3s cubic-bezier(0.2, 0, 0, 1)',
          height: '100vh',
          overflowY: 'auto',
        }}>
          {/* Glass Header */}
          <div style={{
            height: 64,
            padding: '0 32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'rgba(15, 12, 40, 0.4)',
            backdropFilter: 'blur(16px) saturate(1.4)',
            WebkitBackdropFilter: 'blur(16px) saturate(1.4)',
            borderBottom: '1px solid rgba(129, 140, 248, 0.06)',
            position: 'sticky',
            top: 0,
            zIndex: 50,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: '#10b981',
                boxShadow: '0 0 8px rgba(16, 185, 129, 0.5)',
              }} />
              <Typography.Text style={{ color: 'rgba(165, 180, 252, 0.6)', fontSize: 13, fontWeight: 500 }}>
                {location.pathname === '/' ? 'Dashboard' : location.pathname.replace('/', '').replace(/\//g, ' / ').replace(/(^|\s)\S/g, t => t.toUpperCase())}
              </Typography.Text>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <Tooltip title="Notifications">
                <Badge count={unreadData?.unread_count || 0} size="small" offset={[-2, 2]}>
                  <div
                    onClick={() => navigate('/notifications')}
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 10,
                      background: 'rgba(129, 140, 248, 0.08)',
                      border: '1px solid rgba(129, 140, 248, 0.1)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    <BellOutlined style={{ fontSize: 16, color: 'rgba(165, 180, 252, 0.7)' }} />
                  </div>
                </Badge>
              </Tooltip>
              <Dropdown menu={userMenu} placement="bottomRight">
                <div style={{
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '4px 14px 4px 4px',
                  borderRadius: 24,
                  background: 'rgba(129, 140, 248, 0.08)',
                  border: '1px solid rgba(129, 140, 248, 0.1)',
                  transition: 'all 0.2s',
                }}>
                  <Avatar
                    icon={<UserOutlined />}
                    size={32}
                    style={{
                      background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                      boxShadow: '0 2px 10px rgba(99, 102, 241, 0.35)',
                    }}
                  />
                  <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: 13, fontWeight: 500 }}>
                    {user?.first_name}
                  </span>
                </div>
              </Dropdown>
            </div>
          </div>

          {/* Page Content */}
          <Content className="page-content" style={{ padding: 32 }}>
            {children}
          </Content>
        </AntLayout>
      </AntLayout>
    </div>
  );
};

export default Layout;
