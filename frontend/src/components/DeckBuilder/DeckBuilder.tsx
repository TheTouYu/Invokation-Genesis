import React from 'react';

const DeckBuilder = () => {
  return (
    <div className="deck-builder-container">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
        <div style={{ 
          width: '80px', 
          height: '80px', 
          marginRight: '20px',
          backgroundImage: `url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`, 
          backgroundSize: 'cover',
          borderRadius: '10px',
          border: '2px solid #ffd700'
        }}>
          {/* 图片注释: 卡组构建页面标题图标使用了指定的image.png */}
        </div>
        <h2>卡组构建</h2>
      </div>
      
      <div style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3>我的卡牌</h3>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select style={{ width: 'auto' }}>
              <option>全部类型</option>
              <option>角色卡</option>
              <option>武器</option>
              <option>圣遗物</option>
              <option>天赋</option>
              <option>支援</option>
              <option>事件</option>
            </select>
            <input type="text" placeholder="搜索卡牌..." style={{ width: '200px' }} />
          </div>
        </div>
        <div className="card-list">
          {/* 卡牌列表将在这里显示 */}
          <p style={{ color: '#aaa', textAlign: 'center', paddingTop: '50px' }}>卡牌数据将从后端加载...</p>
        </div>
      </div>
      
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3>当前卡组 (0/30)</h3>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button>保存卡组</button>
            <button>重置卡组</button>
          </div>
        </div>
        <div className="current-deck">
          {/* 当前卡组将在这里显示 */}
          <p style={{ color: '#aaa', textAlign: 'center', paddingTop: '50px' }}>当前卡组为空，请从左侧选择卡牌</p>
        </div>
      </div>
    </div>
  );
};

export default DeckBuilder;