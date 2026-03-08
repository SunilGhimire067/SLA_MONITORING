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
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
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
  const { getBackground } = useTheme();

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
    { key: '/roles', icon: <SafetyCertificateOutlined />, label: 'Role Permissions', roles: ['admin'] },
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
            background: 'rgba(255, 255, 255, var(--glass-opacity, 0.12))',
            backdropFilter: 'blur(var(--glass-blur, 20px)) saturate(var(--glass-saturation, 1.8))',
            WebkitBackdropFilter: 'blur(var(--glass-blur, 20px)) saturate(var(--glass-saturation, 1.8))',
            borderRight: '1px solid rgba(255, 255, 255, var(--glass-border-opacity, 0.18))',
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
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            padding: '0 16px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              overflow: 'hidden',
            }}>
              <div style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.8), rgba(168, 85, 247, 0.8))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 16,
                fontWeight: 700,
                color: '#fff',
                flexShrink: 0,
                boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
              }}>
                IT
              </div>
              {!collapsed && (
                <Typography.Text strong style={{
                  color: 'rgba(255, 255, 255, 0.95)',
                  fontSize: 16,
                  letterSpacing: '-0.3px',
                  whiteSpace: 'nowrap',
                }}>
                  ITSM Platform
                </Typography.Text>
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
              padding: '8px 0',
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
              borderTop: '1px solid rgba(255, 255, 255, 0.08)',
              color: 'rgba(255, 255, 255, 0.5)',
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
            padding: '0 28px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'rgba(255, 255, 255, calc(var(--glass-opacity, 0.12) * 0.5))',
            backdropFilter: 'blur(calc(var(--glass-blur, 20px) * 0.8))',
            WebkitBackdropFilter: 'blur(calc(var(--glass-blur, 20px) * 0.8))',
            borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
            position: 'sticky',
            top: 0,
            zIndex: 50,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <Typography.Text style={{ color: 'rgba(255, 255, 255, 0.4)', fontSize: 13 }}>
                {location.pathname === '/' ? 'Dashboard' : location.pathname.replace('/', '').replace(/\//g, ' / ').replace(/(^|\s)\S/g, t => t.toUpperCase())}
              </Typography.Text>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
              <Tooltip title="Notifications">
                <Badge count={unreadData?.unread_count || 0} size="small" offset={[-2, 2]}>
                  <BellOutlined
                    onClick={() => navigate('/notifications')}
                    style={{
                      fontSize: 18,
                      cursor: 'pointer',
                      color: 'rgba(255, 255, 255, 0.7)',
                      padding: 8,
                      borderRadius: 8,
                      transition: 'all 0.2s',
                    }}
                  />
                </Badge>
              </Tooltip>
              <Dropdown menu={userMenu} placement="bottomRight">
                <div style={{
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '4px 12px 4px 4px',
                  borderRadius: 24,
                  background: 'rgba(255, 255, 255, 0.06)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  transition: 'all 0.2s',
                }}>
                  <Avatar
                    icon={<UserOutlined />}
                    size={32}
                    style={{
                      background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                      boxShadow: '0 2px 8px rgba(99, 102, 241, 0.3)',
                    }}
                  />
                  <span style={{ color: 'rgba(255, 255, 255, 0.85)', fontSize: 13 }}>
                    {user?.first_name}
                  </span>
                </div>
              </Dropdown>
            </div>
          </div>

          {/* Page Content */}
          <Content className="page-content" style={{ padding: 28 }}>
            {children}
          </Content>
        </AntLayout>
      </AntLayout>
    </div>
  );
};

export default Layout;
