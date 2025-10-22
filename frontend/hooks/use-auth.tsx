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
          setUser(profile);
        } catch (error) {
          console.error('获取用户信息失败:', error);
          clearToken(); // token无效，清除它
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
