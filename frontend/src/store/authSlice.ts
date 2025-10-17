import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '../services/api';

// 定义用户类型
export interface User {
  id: string;
  username: string;
}

// 定义认证状态类型
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  token: string | null;
  error: string | null;
  loading: boolean;
}

// 定义返回结果类型
interface AuthResult {
  success: boolean;
  error?: string;
  token?: string;
  user?: User;
}

// 初始状态
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  token: localStorage.getItem('token'),
  error: null,
  loading: false,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // 设置认证状态
    setAuthState: (state, action: PayloadAction<Partial<AuthState>>) => {
      Object.assign(state, action.payload);
    },
    
    // 设置用户信息
    setUser: (state, action: PayloadAction<User | null>) => {
      state.user = action.payload;
      state.isAuthenticated = !!action.payload;
    },
    
    // 设置令牌
    setToken: (state, action: PayloadAction<string | null>) => {
      state.token = action.payload;
      if (action.payload) {
        localStorage.setItem('token', action.payload);
      } else {
        localStorage.removeItem('token');
      }
    },
    
    // 设置错误信息
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    
    // 设置加载状态
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    
    // 登出
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.token = null;
      state.error = null;
      localStorage.removeItem('token');
    },
  },
});

export const { 
  setAuthState, 
  setUser, 
  setToken, 
  setError, 
  setLoading, 
  logout 
} = authSlice.actions;

// 异步操作函数（不使用createAsyncThunk）
export const registerUser = (userData: { username: string; password: string; email?: string }) => {
  return async (dispatch: any) => {
    dispatch(setLoading(true));
    dispatch(setError(null));
    
    try {
      const response = await apiService.register(userData);
      const { access_token } = response.data;
      
      // 注册成功后自动登录
      dispatch(setToken(access_token));
      dispatch(setLoading(false));
      
      return { success: true };
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '注册失败';
      dispatch(setError(errorMessage));
      dispatch(setLoading(false));
      return { success: false, error: errorMessage };
    }
  };
};

// 异步操作函数（不使用createAsyncThunk）
export const loginUser = (userData: { username: string; password: string }) => {
  return async (dispatch: any) => {
    dispatch(setLoading(true));
    dispatch(setError(null));
    
    try {
      const response = await apiService.login(userData);
      const { access_token } = response.data;
      
      // 登录成功后获取用户信息
      const profileResponse = await apiService.getProfile();
      const user = profileResponse.data;
      
      dispatch(setToken(access_token));
      dispatch(setUser(user));
      dispatch(setLoading(false));
      
      return { success: true };
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || '登录失败';
      dispatch(setError(errorMessage));
      dispatch(setLoading(false));
      return { success: false, error: errorMessage };
    }
  };
};

export default authSlice.reducer;