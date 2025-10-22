'use client';

import { useState, useEffect, ReactNode, createContext, useContext } from 'react';
import { getProfile, logout as apiLogout } from '@/lib/api/auth';
import { getToken, clearToken } from '@/lib/api/client';
import type { UserProfile } from '@/lib/api/types';

type AuthContextType = {
  user: UserProfile | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // 检查是否有已保存的token并获取用户信息
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = getToken();
      if (token) {
        try {
          const profile = await getProfile();
          // 如果成功获取用户信息，设置用户信息
          setUser(profile);
        } catch (error: any) {
          console.error('获取用户信息失败:', error);
          // 检查错误是否为认证错误，包括错误消息在msg字段的情况
          const isAuthError = error.message?.includes('401') || 
                             error.message?.includes('Missing Authorization Header') || 
                             error.message?.includes('Token has expired') ||
                             error.message?.includes('Invalid token') ||
                             error.message?.includes('AUTH_ERROR:');
          
          if (isAuthError) {
            // 清除无效的token
            clearToken();
            // 重定向到登录页面
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
          } else {
            // 对于其他错误，只是清除token
            clearToken();
          }
        }
      }
      setLoading(false);
    };

    checkAuthStatus();
  }, []);

  const login = async (username: string, password: string) => {
    // 这里需要实际的登录逻辑，通常在组件中处理
    // 这个上下文将通过其他方式更新用户状态
  };

  const logout = () => {
    apiLogout();
    setUser(null);
  };

  const isAuthenticated = !!user;

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated
  };

  return <AuthContext.Provider value={value}> {children} </AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
