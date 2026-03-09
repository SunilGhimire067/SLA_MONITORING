import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Typography, message } from 'antd';
import { UserOutlined, LockOutlined, ThunderboltOutlined } from '@ant-design/icons';
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
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0d0b2e 0%, #1a1154 30%, #2d1b69 60%, #1a1040 100%)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Animated background orbs */}
      <div className="app-background" />
      <div className="orb-3" />
      <div className="orb-4" />

      {/* Left side — Login Form */}
      <div style={{
        flex: '0 0 480px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '40px 48px',
        position: 'relative',
        zIndex: 2,
      }}>
        <div style={{
          width: '100%',
          maxWidth: 400,
          padding: '48px 40px 40px',
          background: 'rgba(255, 255, 255, 0.06)',
          backdropFilter: 'blur(30px) saturate(1.6)',
          WebkitBackdropFilter: 'blur(30px) saturate(1.6)',
          borderRadius: 28,
          border: '1px solid rgba(129, 140, 248, 0.12)',
          boxShadow: '0 32px 80px rgba(0, 0, 0, 0.4), 0 0 60px rgba(99, 102, 241, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.08)',
        }}>
          {/* Logo */}
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <div style={{
              width: 68,
              height: 68,
              borderRadius: 20,
              background: 'linear-gradient(135deg, #6366f1, #a855f7)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 22,
              boxShadow: '0 8px 32px rgba(99, 102, 241, 0.4), inset 0 1px 0 rgba(255,255,255,0.2)',
            }}>
              <ThunderboltOutlined style={{ fontSize: 30, color: '#fff' }} />
            </div>
            <Title level={2} style={{
              margin: 0,
              color: '#fff',
              fontWeight: 800,
              letterSpacing: '-0.5px',
              fontSize: 24,
            }}>
              DevOps ITSM
            </Title>
            <Text style={{
              color: 'rgba(165, 180, 252, 0.6)',
              fontSize: 11,
              letterSpacing: '2px',
              textTransform: 'uppercase',
              fontWeight: 500,
            }}>
              SLA Monitoring & Management
            </Text>
          </div>

          <Form
            layout="vertical"
            onFinish={onFinish}
            initialValues={{ email: 'admin@company.com', password: 'admin123' }}
          >
            <Form.Item name="email" rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}>
              <Input
                prefix={<UserOutlined style={{ color: 'rgba(165, 180, 252, 0.4)' }} />}
                placeholder="Email"
                size="large"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(129, 140, 248, 0.12)',
                  borderRadius: 14,
                  color: 'rgba(255, 255, 255, 0.9)',
                  height: 50,
                  fontSize: 14,
                }}
              />
            </Form.Item>
            <Form.Item name="password" rules={[{ required: true, message: 'Enter your password' }]}>
              <Input.Password
                prefix={<LockOutlined style={{ color: 'rgba(165, 180, 252, 0.4)' }} />}
                placeholder="Password"
                size="large"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(129, 140, 248, 0.12)',
                  borderRadius: 14,
                  color: 'rgba(255, 255, 255, 0.9)',
                  height: 50,
                  fontSize: 14,
                }}
              />
            </Form.Item>
            <Form.Item style={{ marginBottom: 16, marginTop: 8 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                size="large"
                style={{
                  height: 50,
                  borderRadius: 14,
                  background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                  border: 'none',
                  fontWeight: 700,
                  fontSize: 15,
                  letterSpacing: '0.5px',
                  boxShadow: '0 8px 28px rgba(99, 102, 241, 0.35)',
                }}
              >
                Sign In
              </Button>
            </Form.Item>
          </Form>

          {/* Status indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            marginTop: 8,
          }}>
            <div style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: '#10b981',
              boxShadow: '0 0 8px rgba(16, 185, 129, 0.5)',
            }} />
            <Text style={{
              fontSize: 11,
              color: 'rgba(165, 180, 252, 0.4)',
              letterSpacing: '0.5px',
            }}>
              System Online — 24/7 Monitoring Active
            </Text>
          </div>
        </div>
      </div>

      {/* Right side — Background Image */}
      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        zIndex: 1,
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: 'url(/background.png)',
          backgroundSize: 'contain',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          opacity: 0.85,
          filter: 'drop-shadow(0 0 40px rgba(99, 102, 241, 0.15))',
        }} />
        {/* Gradient overlay to blend edges */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(90deg, rgba(13, 11, 46, 0.95) 0%, rgba(13, 11, 46, 0.3) 15%, transparent 40%, transparent 85%, rgba(13, 11, 46, 0.5) 100%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(180deg, rgba(13, 11, 46, 0.4) 0%, transparent 20%, transparent 80%, rgba(13, 11, 46, 0.6) 100%)',
          pointerEvents: 'none',
        }} />
      </div>
    </div>
  );
};

export default LoginPage;
