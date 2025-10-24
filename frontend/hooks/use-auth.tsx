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
    console.log('[Auth] 开始检查认证状态');
    const checkAuthStatus = async () => {
      const token = getToken();
      console.log('[Auth] 检查到本地token:', !!token);
      if (token) {
        try {
          console.log('[Auth] 尝试获取用户信息');
          const profile = await getProfile();
          console.log('[Auth] 成功获取用户信息:', profile);
          // 如果成功获取用户信息，设置用户信息
          setUser(profile);
          console.log('[Auth] 用户信息已设置，当前用户:', profile);
        } catch (error: any) {
          console.error('[Auth] 获取用户信息失败:', error);
          // 检查错误是否为认证错误，包括错误消息在msg字段的情况
          const isAuthError = error.message?.includes('401') || 
                             error.message?.includes('Missing Authorization Header') || 
                             error.message?.includes('Token has expired') ||
                             error.message?.includes('Invalid token') ||
                             error.message?.includes('AUTH_ERROR:');
          
          if (isAuthError) {
            console.log('[Auth] 检测到认证错误，清除token并重定向到登录页面');
            // 清除无效的token
            clearToken();
            // 重定向到登录页面
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }
          } else {
            // 对于其他错误（如网络错误、服务器错误等），不应该清除有效token
            console.warn('[Auth] 非认证错误，保留现有token', error);
          }
        }
      } else {
        console.log('[Auth] 无本地token，用户未登录');
      }
      // 确保在设置了用户或其他认证相关信息后，再设置loading为false
      // 这样能确保认证状态在loading结束时是确定的
      console.log('[Auth] 认证状态检查完成，设置loading为false');
      setLoading(false);
    };

    checkAuthStatus();
  }, []);
  
  // 当用户信息更新时，记录日志
  useEffect(() => {
    console.log('[Auth] 用户信息发生变化:', user);
  }, [user]);

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
