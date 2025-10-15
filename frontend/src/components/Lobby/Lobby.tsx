import React from 'react';
import { Link } from 'react-router-dom';

const Lobby = () => {
  return (
    <div className="lobby-container" style={{ backgroundImage: `url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`, backgroundSize: 'cover', backgroundPosition: 'center' }}>
      {/* 图片注释: 背景图片使用了指定的image.png */}
      <h1>七圣召唤 - 天下再集</h1>
      <p style={{ fontSize: '18px', margin: '20px 0', color: '#ffd700' }}>欢迎来到提瓦特大陆的卡牌对决！</p>
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