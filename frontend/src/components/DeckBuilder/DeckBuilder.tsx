import React from 'react';

const DeckBuilder = () => {
  return (
    <div className="deck-builder-container">
      <h2>卡组构建</h2>
      <div>
        <h3>我的卡牌</h3>
        <div className="card-list">
          {/* 卡牌列表将在这里显示 */}
        </div>
      </div>
      <div>
        <h3>当前卡组 (0/30)</h3>
        <div className="current-deck">
          {/* 当前卡组将在这里显示 */}
        </div>
      </div>
    </div>
  );
};

export default DeckBuilder;