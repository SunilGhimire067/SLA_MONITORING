import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Typography, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';

const { Title, Text } = Typography;

const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.email, values.password);
      message.success('Login successful!');
      navigate('/');
    } catch {
      message.error('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 40%, #24243e 100%)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Animated background orbs */}
      <div className="app-background" />
      <div className="orb-3" />

      {/* Glass Login Card */}
      <div style={{
        width: 420,
        padding: '48px 40px 40px',
        background: 'rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(24px) saturate(1.8)',
        WebkitBackdropFilter: 'blur(24px) saturate(1.8)',
        borderRadius: 24,
        border: '1px solid rgba(255, 255, 255, 0.15)',
        boxShadow: '0 24px 80px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
        position: 'relative',
        zIndex: 1,
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{
            width: 64,
            height: 64,
            borderRadius: 18,
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.9), rgba(168, 85, 247, 0.9))',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 24,
            fontWeight: 800,
            color: '#fff',
            marginBottom: 20,
            boxShadow: '0 8px 24px rgba(99, 102, 241, 0.4)',
          }}>
            IT
          </div>
          <Title level={3} style={{
            margin: 0,
            color: 'rgba(255, 255, 255, 0.95)',
            fontWeight: 700,
            letterSpacing: '-0.5px',
          }}>
            ITSM Platform
          </Title>
          <Text style={{
            color: 'rgba(255, 255, 255, 0.45)',
            fontSize: 13,
            letterSpacing: '0.5px',
            textTransform: 'uppercase',
          }}>
            SLA Monitoring & Project Management
          </Text>
        </div>

        <Form
          layout="vertical"
          onFinish={onFinish}
          initialValues={{ email: 'admin@company.com', password: 'admin123' }}
        >
          <Form.Item name="email" rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}>
            <Input
              prefix={<UserOutlined style={{ color: 'rgba(255,255,255,0.3)' }} />}
              placeholder="Email"
              size="large"
              style={{
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 12,
                color: 'rgba(255, 255, 255, 0.9)',
                height: 48,
              }}
            />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: 'Enter your password' }]}>
            <Input.Password
              prefix={<LockOutlined style={{ color: 'rgba(255,255,255,0.3)' }} />}
              placeholder="Password"
              size="large"
              style={{
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 12,
                color: 'rgba(255, 255, 255, 0.9)',
                height: 48,
              }}
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              style={{
                height: 48,
                borderRadius: 12,
                background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                border: 'none',
                fontWeight: 600,
                fontSize: 15,
                boxShadow: '0 8px 24px rgba(99, 102, 241, 0.3)',
              }}
            >
              Sign In
            </Button>
          </Form.Item>
        </Form>

        <Text style={{
          display: 'block',
          textAlign: 'center',
          fontSize: 12,
          color: 'rgba(255, 255, 255, 0.3)',
          marginTop: 8,
        }}>
          Demo: admin@company.com / admin123
        </Text>
      </div>
    </div>
  );
};

export default LoginPage;
