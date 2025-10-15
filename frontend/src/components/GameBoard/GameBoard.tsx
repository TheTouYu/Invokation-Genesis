import React from 'react';
import styled from 'styled-components';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import { PlayerState, DiceType } from '../../types/game';
import Card from '../Card/Card';
import CharacterArea from '../CharacterArea/CharacterArea';

const GameBoardContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  background: 
    linear-gradient(135deg, rgba(26, 42, 108, 0.8), rgba(178, 31, 31, 0.8), rgba(26, 42, 108, 0.8)),
    var(--background, url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png'));
  background-size: cover;
  background-position: center;
  background-blend-mode: overlay;
  color: var(--text-primary, white);
`;

const GameHeader = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 2px solid var(--accent, gold);
  background: var(--container-background, rgba(0, 0, 0, 0.5));
  border-radius: 10px;
  margin-bottom: 10px;
  padding: 10px;
`;

const PlayerSection = styled.div<{ isCurrentPlayer?: boolean }>`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 45%;
  margin: 10px 0;
  padding: 15px;
  border-radius: 15px;
  background: var(--container-background, ${(props) => 
    props.isCurrentPlayer 
      ? 'linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 140, 0, 0.15))'
      : 'linear-gradient(135deg, rgba(0, 0, 0, 0.4), rgba(25, 25, 112, 0.4))'
  });
  border: ${(props) => (props.isCurrentPlayer ? `2px solid var(--accent, gold)` : `1px solid var(--border, rgba(255, 255, 255, 0.2))`)};
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
`;

const SectionTitle = styled.h2`
  margin: 0 0 10px 0;
  font-size: 18px;
  text-align: center;
  color: var(--text-header, #ffd700);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
`;

const HandArea = styled.div`
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 10px;
  min-height: 180px;
  padding: 10px;
  background: var(--container-background, rgba(0, 0, 0, 0.2));
  border-radius: 10px;
`;

const DiceArea = styled.div`
  display: flex;
  justify-content: center;
  gap: 5px;
  margin: 10px 0;
  padding: 10px;
  background: var(--container-background, rgba(0, 0, 0, 0.2));
  border-radius: 10px;
`;

const Dice = styled.div<{ color: string }>`
  width: 30px;
  height: 30px;
  border-radius: 5px;
  background-color: ${(props) => props.color};
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
`;

const GameLog = styled.div`
  background: var(--container-background, rgba(0, 0, 0, 0.6));
  border-radius: 10px;
  padding: 15px;
  height: 120px;
  overflow-y: auto;
  margin-top: 15px;
  font-size: 14px;
  border: 1px solid var(--accent, rgba(255, 215, 0, 0.3));
`;

const GameBoard: React.FC = () => {
  const { gameState } = useSelector((state: RootState) => state.game);

  if (!gameState) {
    return (
      <GameBoardContainer>
        <h1>暂无活动游戏</h1>
        <p>开始新游戏以查看游戏面板</p>
      </GameBoardContainer>
    );
  }

  const currentPlayer = gameState.players[gameState.currentPlayerIndex];
  const opponentPlayer = gameState.players[1 - gameState.currentPlayerIndex];

  const getElementTypeColor = (elementType: DiceType): string => {
    switch (elementType) {
      case 'Pyro':
        return '#e74c3c';
      case 'Hydro':
        return '#3498db';
      case 'Dendro':
        return '#2ecc71';
      case 'Electro':
        return '#9b59b6';
      case 'Anemo':
        return '#1abc9c';
      case 'Cryo':
        return '#3498db';
      case 'Geo':
        return '#f1c40f';
      case 'Omni':
        return '#ecf0f1';
      default:
        return '#95a5a6';
    }
  };

  return (
    <GameBoardContainer>
      {/* 图片注释: 游戏面板背景使用了指定的image.png作为纹理背景 */}
      <GameHeader>
        <div>回合: {gameState.round}/{gameState.maxRounds}</div>
        <div>阶段: {gameState.phase}</div>
        <div>轮次: {gameState.turn}</div>
      </GameHeader>

      {/* Opponent Section */}
      <PlayerSection>
        <SectionTitle>对手</SectionTitle>
        <CharacterArea player={opponentPlayer} isOpponent={true} />
      </PlayerSection>

      {/* Central Game Area - This would contain summons, supports, etc. */}
      <div style={{ 
        height: '10%', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        margin: '10px 0',
        padding: '10px',
        background: 'var(--container-background, rgba(0, 0, 0, 0.3))',
        borderRadius: '10px',
        border: '1px solid var(--accent, rgba(255, 215, 0, 0.2))'
      }}>
        <div>召唤物/支援区</div>
      </div>

      {/* Player Section */}
      <PlayerSection isCurrentPlayer={true}>
        <SectionTitle>玩家</SectionTitle>
        <CharacterArea player={currentPlayer} isOpponent={false} />
        
        {/* Hand Area */}
        <SectionTitle>手牌</SectionTitle>
        <HandArea>
          {currentPlayer.hand.map((card, index) => (
            <Card key={index} card={card} />
          ))}
        </HandArea>
        
        {/* Dice Area */}
        <SectionTitle>骰子</SectionTitle>
        <DiceArea>
          {currentPlayer.dice.map((die, index) => (
            <Dice key={index} color={getElementTypeColor(die)} />
          ))}
        </DiceArea>
      </PlayerSection>

      {/* Game Log */}
      <GameLog>
        {gameState.gameLog.map((log, index) => (
          <div key={index} style={{ color: 'var(--text-primary, white)' }}>{log}</div>
        ))}
      </GameLog>
    </GameBoardContainer>
  );
};

export default GameBoard;