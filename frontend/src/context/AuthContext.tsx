import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { User, TokenResponse } from '../types';
import { login as apiLogin } from '../api/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: string[]) => boolean;
  hasPermission: (...permissions: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {},
  hasRole: () => false,
  hasPermission: () => false,
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('access_token');
  });

  const isAuthenticated = !!token && !!user;

  const login = useCallback(async (email: string, password: string) => {
    const data: TokenResponse = await apiLogin(email, password);
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }, []);

  const hasRole = useCallback((...roles: string[]) => {
    return !!user?.role && roles.includes(user.role);
  }, [user]);

  const hasPermission = useCallback((...permissions: string[]) => {
    return !!user?.permissions && permissions.some(p => user.permissions!.includes(p));
  }, [user]);

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, login, logout, hasRole, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};
