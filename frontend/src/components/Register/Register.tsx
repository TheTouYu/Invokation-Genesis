import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { apiService } from '../../services/api';
import { setAuthState, setUser, setToken, setError, setLoading } from '../../store/authSlice';
import { RootState } from '../../store';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state: RootState) => state.auth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 验证密码是否匹配
    if (password !== confirmPassword) {
      dispatch(setError('两次输入的密码不一致'));
      return;
    }
    
    dispatch(setLoading(true));
    dispatch(setError(null));
    
    try {
      // 调用注册API
      const response = await apiService.register({ username, password, email });
      const { access_token } = response.data;
      
      // 注册成功后自动登录
      dispatch(setToken(access_token));
      dispatch(setLoading(false));
      
      // 注册成功，导航到登录页面
      navigate('/login');
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || '注册失败';
      dispatch(setError(errorMessage));
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="register-container">
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
          {/* 图片注释: 注册页面圆形头像使用了指定的image.png */}
        </div>
        <h2>用户注册</h2>
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
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '5px' }}>邮箱:</label>
          <input 
            type="email" 
            id="email" 
            name="email" 
            placeholder="请输入邮箱地址"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
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
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="confirmPassword" style={{ display: 'block', marginBottom: '5px' }}>确认密码:</label>
          <input 
            type="password" 
            id="confirmPassword" 
            name="confirmPassword" 
            placeholder="请再次输入密码"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required 
          />
        </div>
        <button 
          type="submit" 
          style={{ width: '100%', marginBottom: '15px' }}
          disabled={loading}
        >
          {loading ? '注册中...' : '注册'}
        </button>
        <div style={{ textAlign: 'center' }}>
          <p>已有账号？ <Link to="/login" style={{ color: '#ffd700' }}>立即登录</Link></p>
        </div>
      </form>
    </div>
  );
};

export default Register;