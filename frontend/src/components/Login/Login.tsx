import React from 'react';

const Login = () => {
  return (
    <div className="login-container">
      <h2>用户登录</h2>
      <form>
        <div>
          <label htmlFor="username">用户名:</label>
          <input type="text" id="username" name="username" />
        </div>
        <div>
          <label htmlFor="password">密码:</label>
          <input type="password" id="password" name="password" />
        </div>
        <button type="submit">登录</button>
      </form>
    </div>
  );
};

export default Login;