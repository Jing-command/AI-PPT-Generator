"use client";

import { useState, useEffect, useCallback } from 'react';
import { authAPI } from '@/lib/api';

interface User {
  id: string;
  email: string;
  username?: string;
  avatar_url?: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

// 认证 Hook
export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // 检查登录状态
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setState({ user: null, isLoading: false, isAuthenticated: false });
        return;
      }

      try {
        const user = await authAPI.getCurrentUser();
        setState({ user, isLoading: false, isAuthenticated: true });
      } catch (error) {
        // Token 无效，尝试刷新
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            const tokens = await authAPI.refresh(refreshToken);
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);
            const user = await authAPI.getCurrentUser();
            setState({ user, isLoading: false, isAuthenticated: true });
          } catch {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setState({ user: null, isLoading: false, isAuthenticated: false });
          }
        } else {
          localStorage.removeItem('access_token');
          setState({ user: null, isLoading: false, isAuthenticated: false });
        }
      }
    };

    checkAuth();
  }, []);

  // 登录
  const login = useCallback(async (email: string, password: string) => {
    const tokens = await authAPI.login({ email, password });
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    const user = await authAPI.getCurrentUser();
    setState({ user, isLoading: false, isAuthenticated: true });
    return user;
  }, []);

  // 注册
  const register = useCallback(async (email: string, password: string, username?: string) => {
    await authAPI.register({ email, password, username });
    return login(email, password);
  }, [login]);

  // 登出
  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setState({ user: null, isLoading: false, isAuthenticated: false });
  }, []);

  return {
    ...state,
    login,
    register,
    logout,
  };
}
