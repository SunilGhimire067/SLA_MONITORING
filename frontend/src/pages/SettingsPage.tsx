import { Card, Col, Row, Slider, Typography, Button, Space, Tooltip, Switch } from 'antd';
import { ReloadOutlined, BgColorsOutlined, ControlOutlined, EyeOutlined, PictureOutlined } from '@ant-design/icons';
import { useTheme } from '../context/ThemeContext';

const { Title, Text } = Typography;

const SettingsPage = () => {
  const { settings, updateSettings, resetSettings, backgroundPresets } = useTheme();

  const presetEntries = Object.entries(backgroundPresets);

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <Title level={3}>
            <ControlOutlined style={{ marginRight: 8 }} />
            Theme Settings
          </Title>
          <Button icon={<ReloadOutlined />} onClick={resetSettings}>
            Reset to Defaults
          </Button>
        </div>
      </div>

      <Row gutter={[20, 20]}>
        {/* Glass Effect Controls */}
        <Col xs={24} md={12}>
          <Card title={<><EyeOutlined style={{ marginRight: 8, color: '#818cf8' }} />Transparency Controls</>}>
            <div style={{ padding: '8px 0' }}>
              <div style={{ marginBottom: 28 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text style={{ color: 'rgba(255,255,255,0.7)' }}>Blur Intensity</Text>
                  <Text style={{ color: 'rgba(165, 180, 252, 0.6)', fontFamily: 'monospace' }}>{settings.blur}px</Text>
                </div>
                <Slider min={0} max={50} value={settings.blur} onChange={(v) => updateSettings({ blur: v })}
                  tooltip={{ formatter: (v) => `${v}px` }} />
              </div>

              <div style={{ marginBottom: 28 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text style={{ color: 'rgba(255,255,255,0.7)' }}>Background Opacity</Text>
                  <Text style={{ color: 'rgba(165, 180, 252, 0.6)', fontFamily: 'monospace' }}>{Math.round(settings.opacity * 100)}%</Text>
                </div>
                <Slider min={0} max={0.4} step={0.01} value={settings.opacity} onChange={(v) => updateSettings({ opacity: v })}
                  tooltip={{ formatter: (v) => `${Math.round((v || 0) * 100)}%` }} />
              </div>

              <div style={{ marginBottom: 28 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text style={{ color: 'rgba(255,255,255,0.7)' }}>Border Opacity</Text>
                  <Text style={{ color: 'rgba(165, 180, 252, 0.6)', fontFamily: 'monospace' }}>{Math.round(settings.borderOpacity * 100)}%</Text>
                </div>
                <Slider min={0} max={0.5} step={0.01} value={settings.borderOpacity} onChange={(v) => updateSettings({ borderOpacity: v })}
                  tooltip={{ formatter: (v) => `${Math.round((v || 0) * 100)}%` }} />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text style={{ color: 'rgba(255,255,255,0.7)' }}>Saturation</Text>
                  <Text style={{ color: 'rgba(165, 180, 252, 0.6)', fontFamily: 'monospace' }}>{settings.saturation.toFixed(1)}x</Text>
                </div>
                <Slider min={0.5} max={3} step={0.1} value={settings.saturation} onChange={(v) => updateSettings({ saturation: v })}
                  tooltip={{ formatter: (v) => `${(v || 0).toFixed(1)}x` }} />
              </div>
            </div>
          </Card>
        </Col>

        {/* Background Presets */}
        <Col xs={24} md={12}>
          <Card title={<><BgColorsOutlined style={{ marginRight: 8, color: '#a855f7' }} />Background Theme</>}>
            <Row gutter={[12, 12]}>
              {presetEntries.map(([name, gradient]) => (
                <Col xs={12} key={name}>
                  <Tooltip title={name.charAt(0).toUpperCase() + name.slice(1)}>
                    <div
                      onClick={() => updateSettings({ backgroundPreset: name })}
                      style={{
                        height: 100,
                        borderRadius: 16,
                        background: gradient,
                        cursor: 'pointer',
                        border: settings.backgroundPreset === name
                          ? '2px solid rgba(129, 140, 248, 0.7)'
                          : '2px solid rgba(255, 255, 255, 0.06)',
                        transition: 'all 0.3s ease',
                        display: 'flex',
                        alignItems: 'flex-end',
                        justifyContent: 'center',
                        padding: 10,
                        position: 'relative',
                        overflow: 'hidden',
                        boxShadow: settings.backgroundPreset === name
                          ? '0 0 24px rgba(99, 102, 241, 0.25)'
                          : '0 4px 12px rgba(0,0,0,0.2)',
                      }}
                    >
                      {settings.backgroundPreset === name && (
                        <div style={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          width: 22,
                          height: 22,
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 11,
                          color: '#fff',
                          fontWeight: 700,
                          boxShadow: '0 2px 8px rgba(99, 102, 241, 0.4)',
                        }}>
                          ✓
                        </div>
                      )}
                      <Text style={{
                        color: 'rgba(255, 255, 255, 0.8)',
                        fontSize: 12,
                        fontWeight: 600,
                        textTransform: 'capitalize',
                        textShadow: '0 1px 4px rgba(0,0,0,0.5)',
                      }}>
                        {name}
                      </Text>
                    </div>
                  </Tooltip>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* Background Image */}
        <Col xs={24}>
          <Card title={<><PictureOutlined style={{ marginRight: 8, color: '#22d3ee' }} />Background Image</>}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>
              <div style={{
                width: 160,
                height: 100,
                borderRadius: 14,
                backgroundImage: 'url(/background.png)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                border: '2px solid rgba(129, 140, 248, 0.15)',
                opacity: settings.showBgImage ? 1 : 0.3,
                transition: 'opacity 0.3s',
              }} />
              <div style={{ flex: 1, minWidth: 200 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
                  <Switch
                    checked={settings.showBgImage}
                    onChange={(checked) => updateSettings({ showBgImage: checked })}
                  />
                  <Text style={{ color: 'rgba(255,255,255,0.7)' }}>
                    {settings.showBgImage ? 'Background image visible' : 'Background image hidden'}
                  </Text>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text style={{ color: 'rgba(255,255,255,0.7)' }}>Image Opacity</Text>
                    <Text style={{ color: 'rgba(165, 180, 252, 0.6)', fontFamily: 'monospace' }}>{Math.round(settings.bgImageOpacity * 100)}%</Text>
                  </div>
                  <Slider
                    min={0.05}
                    max={0.5}
                    step={0.01}
                    value={settings.bgImageOpacity}
                    onChange={(v) => updateSettings({ bgImageOpacity: v })}
                    disabled={!settings.showBgImage}
                    tooltip={{ formatter: (v) => `${Math.round((v || 0) * 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </Card>
        </Col>

        {/* Live Preview */}
        <Col xs={24}>
          <Card title="Live Preview">
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              <div style={{
                flex: 1, minWidth: 200, padding: 24, borderRadius: 18,
                background: `rgba(255, 255, 255, ${settings.opacity})`,
                backdropFilter: `blur(${settings.blur}px) saturate(${settings.saturation})`,
                WebkitBackdropFilter: `blur(${settings.blur}px) saturate(${settings.saturation})`,
                border: `1px solid rgba(255, 255, 255, ${settings.borderOpacity})`,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
              }}>
                <Text strong style={{ color: 'rgba(255,255,255,0.9)', fontSize: 14 }}>Sample Card</Text>
                <br />
                <Text style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12 }}>
                  This preview shows how your theme settings will look across the platform.
                </Text>
              </div>

              <div style={{
                flex: 1, minWidth: 200, padding: 24, borderRadius: 18,
                background: `rgba(255, 255, 255, ${settings.opacity})`,
                backdropFilter: `blur(${settings.blur}px) saturate(${settings.saturation})`,
                WebkitBackdropFilter: `blur(${settings.blur}px) saturate(${settings.saturation})`,
                border: `1px solid rgba(255, 255, 255, ${settings.borderOpacity})`,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
              }}>
                <Text strong style={{ color: 'rgba(255,255,255,0.9)', fontSize: 14 }}>Interactive Elements</Text>
                <br /><br />
                <Space>
                  <Button type="primary" style={{
                    background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                    border: 'none', borderRadius: 10,
                  }}>Primary</Button>
                  <Button style={{
                    background: 'rgba(255,255,255,0.07)',
                    border: '1px solid rgba(129, 140, 248, 0.15)',
                    color: 'rgba(255,255,255,0.8)', borderRadius: 10,
                  }}>Secondary</Button>
                </Space>
              </div>

              <div style={{
                flex: 1, minWidth: 200, padding: 24, borderRadius: 18,
                background: `rgba(255, 255, 255, ${settings.opacity})`,
                backdropFilter: `blur(${settings.blur}px) saturate(${settings.saturation})`,
                WebkitBackdropFilter: `blur(${settings.blur}px) saturate(${settings.saturation})`,
                border: `1px solid rgba(255, 255, 255, ${settings.borderOpacity})`,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
              }}>
                <Text strong style={{ color: 'rgba(255,255,255,0.9)', fontSize: 14 }}>Current Values</Text>
                <div style={{ marginTop: 12 }}>
                  {[
                    ['Blur', `${settings.blur}px`],
                    ['Opacity', `${Math.round(settings.opacity * 100)}%`],
                    ['Border', `${Math.round(settings.borderOpacity * 100)}%`],
                    ['Saturation', `${settings.saturation.toFixed(1)}x`],
                    ['Theme', settings.backgroundPreset],
                  ].map(([label, value]) => (
                    <div key={label} style={{
                      display: 'flex', justifyContent: 'space-between', padding: '5px 0',
                      borderBottom: '1px solid rgba(129, 140, 248, 0.06)',
                    }}>
                      <Text style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12 }}>{label}</Text>
                      <Text style={{ color: 'rgba(165, 180, 252, 0.8)', fontSize: 12, fontFamily: 'monospace' }}>{value}</Text>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SettingsPage;
