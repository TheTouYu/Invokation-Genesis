import React from 'react';
import { Link } from 'react-router-dom';

const Login = () => {
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
      <form style={{ textAlign: 'left', maxWidth: '400px', margin: '0 auto' }}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="username" style={{ display: 'block', marginBottom: '5px' }}>用户名:</label>
          <input type="text" id="username" name="username" placeholder="请输入用户名" />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px' }}>密码:</label>
          <input type="password" id="password" name="password" placeholder="请输入密码" />
        </div>
        <button type="submit" style={{ width: '100%', marginBottom: '15px' }}>登录</button>
        <div style={{ textAlign: 'center' }}>
          <p>还没有账号？ <Link to="/register" style={{ color: '#ffd700' }}>立即注册</Link></p>
        </div>
      </form>
    </div>
  );
};

export default Login;