import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { apiService } from '../../services/api';
import { setAuthState, setUser, setToken, setError, setLoading } from '../../store/authSlice';
import { RootState } from '../../store';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error, isAuthenticated } = useSelector((state: RootState) => state.auth);

  // 如果已经认证，重定向到主页
  if (isAuthenticated) {
    navigate('/');
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    dispatch(setLoading(true));
    dispatch(setError(null));
    
    try {
      // 调用登录API
      const response = await apiService.login({ username, password });
      const { access_token } = response.data;
      
      // 获取用户信息
      const profileResponse = await apiService.getProfile();
      const user = profileResponse.data;
      
      // 设置认证状态
      dispatch(setToken(access_token));
      dispatch(setUser(user));
      dispatch(setLoading(false));
      
      // 登录成功，导航到游戏大厅
      navigate('/');
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || '登录失败';
      dispatch(setError(errorMessage));
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="login-container">
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <div style={{ 
          width: '100px', 
          height: '100px', 
          margin: '0 auto 15px', 
          backgroundImage: `url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`, 
          backgroundSize: 'cover',
          borderRadius: '50%',
          border: '3px solid #ffd700'
        }}>
          {/* 图片注释: 登录页面圆形头像使用了指定的image.png */}
        </div>
        <h2>用户登录</h2>
      </div>
      {error && (
        <div style={{ 
          color: 'red', 
          textAlign: 'center', 
          marginBottom: '15px',
          backgroundColor: '#ffebee',
          padding: '10px',
          borderRadius: '4px'
        }}>
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} style={{ textAlign: 'left', maxWidth: '400px', margin: '0 auto' }}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="username" style={{ display: 'block', marginBottom: '5px' }}>用户名:</label>
          <input 
            type="text" 
            id="username" 
            name="username" 
            placeholder="请输入用户名"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required 
          />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px' }}>密码:</label>
          <input 
            type="password" 
            id="password" 
            name="password" 
            placeholder="请输入密码"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required 
          />
        </div>
        <button 
          type="submit" 
          style={{ width: '100%', marginBottom: '15px' }}
          disabled={loading}
        >
          {loading ? '登录中...' : '登录'}
        </button>
        <div style={{ textAlign: 'center' }}>
          <p>还没有账号？ <Link to="/register" style={{ color: '#ffd700' }}>立即注册</Link></p>
        </div>
      </form>
    </div>
  );
};

export default Login;