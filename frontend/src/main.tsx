import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider, theme } from 'antd';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import App from './App';
import './styles/global.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ConfigProvider
          theme={{
            algorithm: theme.darkAlgorithm,
            token: {
              colorPrimary: '#6366f1',
              colorBgContainer: 'rgba(255, 255, 255, 0.06)',
              colorBgElevated: 'rgba(255, 255, 255, 0.1)',
              colorBorder: 'rgba(255, 255, 255, 0.1)',
              colorText: 'rgba(255, 255, 255, 0.85)',
              colorTextSecondary: 'rgba(255, 255, 255, 0.45)',
              borderRadius: 12,
              fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif",
            },
            components: {
              Card: {
                colorBgContainer: 'rgba(255, 255, 255, 0.06)',
                colorBorderSecondary: 'rgba(255, 255, 255, 0.08)',
              },
              Table: {
                colorBgContainer: 'transparent',
                headerBg: 'rgba(255, 255, 255, 0.04)',
                rowHoverBg: 'rgba(255, 255, 255, 0.04)',
              },
              Input: {
                colorBgContainer: 'rgba(255, 255, 255, 0.06)',
                colorBorder: 'rgba(255, 255, 255, 0.1)',
              },
              Select: {
                colorBgContainer: 'rgba(255, 255, 255, 0.06)',
                colorBorder: 'rgba(255, 255, 255, 0.1)',
              },
              Modal: {
                contentBg: 'rgba(20, 20, 40, 0.95)',
                headerBg: 'rgba(20, 20, 40, 0.95)',
              },
              Menu: {
                darkItemBg: 'transparent',
                darkSubMenuItemBg: 'transparent',
                darkItemSelectedBg: 'rgba(99, 102, 241, 0.15)',
                darkItemHoverBg: 'rgba(255, 255, 255, 0.06)',
                darkItemSelectedColor: '#a78bfa',
                darkItemColor: 'rgba(255, 255, 255, 0.55)',
              },
              Slider: {
                trackBg: '#6366f1',
                trackHoverBg: '#818cf8',
                handleColor: '#a78bfa',
                railBg: 'rgba(255, 255, 255, 0.1)',
                railHoverBg: 'rgba(255, 255, 255, 0.15)',
              },
            },
          }}
        >
          <ThemeProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </ThemeProvider>
        </ConfigProvider>
      </QueryClientProvider>
    </BrowserRouter>
);
