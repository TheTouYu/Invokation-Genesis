import React from 'react';
import { Link } from 'react-router-dom';

const Lobby = () => {
  return (
    <div className="lobby-container">
      <h1>七圣召唤 - 天下再集</h1>
      <nav>
        <ul>
          <li><Link to="/local-game">本地游戏</Link></li>
          <li><Link to="/deck-builder">构建卡组</Link></li>
          <li><Link to="/login">玩家登录</Link></li>
          <li><Link to="/register">用户注册</Link></li>
        </ul>
      </nav>
    </div>
  );
};

export default Lobby;