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
  background: linear-gradient(135deg, #1a2a6c, #b21f1f, #1a2a6c);
  color: white;
`;

const GameHeader = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 2px solid gold;
`;

const PlayerSection = styled.div<{ isCurrentPlayer?: boolean }>`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 45%;
  margin: 10px 0;
  padding: 15px;
  border-radius: 10px;
  background-color: ${(props) => (props.isCurrentPlayer ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.2)')};
  border: ${(props) => (props.isCurrentPlayer ? '2px solid gold' : '1px solid rgba(255, 255, 255, 0.2)')};
`;

const SectionTitle = styled.h2`
  margin: 0 0 10px 0;
  font-size: 18px;
  text-align: center;
`;

const HandArea = styled.div`
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 10px;
  min-height: 180px;
`;

const DiceArea = styled.div`
  display: flex;
  justify-content: center;
  gap: 5px;
  margin: 10px 0;
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
`;

const GameLog = styled.div`
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 5px;
  padding: 10px;
  height: 100px;
  overflow-y: auto;
  margin-top: 10px;
  font-size: 14px;
`;

const GameBoard: React.FC = () => {
  const { gameState } = useSelector((state: RootState) => state.game);

  if (!gameState) {
    return (
      <GameBoardContainer>
        <h1>No active game</h1>
        <p>Start a new game to see the game board</p>
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
      <GameHeader>
        <div>Round: {gameState.round}/{gameState.maxRounds}</div>
        <div>Phase: {gameState.phase}</div>
        <div>Turn: {gameState.turn}</div>
      </GameHeader>

      {/* Opponent Section */}
      <PlayerSection>
        <SectionTitle>Opponent</SectionTitle>
        <CharacterArea player={opponentPlayer} isOpponent={true} />
      </PlayerSection>

      {/* Central Game Area - This would contain summons, supports, etc. */}
      <div style={{ height: '10%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div>Summon/Support Area</div>
      </div>

      {/* Player Section */}
      <PlayerSection isCurrentPlayer={true}>
        <SectionTitle>Player</SectionTitle>
        <CharacterArea player={currentPlayer} isOpponent={false} />
        
        {/* Hand Area */}
        <SectionTitle>Hand</SectionTitle>
        <HandArea>
          {currentPlayer.hand.map((card, index) => (
            <Card key={index} card={card} />
          ))}
        </HandArea>
        
        {/* Dice Area */}
        <SectionTitle>Dice</SectionTitle>
        <DiceArea>
          {currentPlayer.dice.map((die, index) => (
            <Dice key={index} color={getElementTypeColor(die)} />
          ))}
        </DiceArea>
      </PlayerSection>

      {/* Game Log */}
      <GameLog>
        {gameState.gameLog.map((log, index) => (
          <div key={index}>{log}</div>
        ))}
      </GameLog>
    </GameBoardContainer>
  );
};

export default GameBoard;