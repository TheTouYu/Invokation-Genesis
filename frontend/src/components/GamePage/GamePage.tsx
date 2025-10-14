import React from 'react';
import GameBoard from '../GameBoard/GameBoard';

const GamePage = () => {
  return (
    <div className="game-page-container">
      <h2>多人游戏</h2>
      <GameBoard />
    </div>
  );
};

export default GamePage;