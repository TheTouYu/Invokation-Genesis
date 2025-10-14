import React from 'react';
import styled from 'styled-components';
import { PlayerState, CharacterCard, Card as CardInterface } from '../../types/game';
import Card from '../Card/Card';

const CharacterAreaContainer = styled.div`
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 100%;
  height: 100px;
  margin: 10px 0;
`;

const CharacterCardContainer = styled.div<{ isActive?: boolean }>`
  width: 100px;
  height: 120px;
  border: ${(props) => (props.isActive ? '3px solid gold' : '2px solid #ccc')};
  border-radius: 8px;
  padding: 5px;
  position: relative;
  background-color: ${(props) => (props.isActive ? 'rgba(255, 215, 0, 0.2)' : 'rgba(255, 255, 255, 0.1)')};
  
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
`;

const HealthBar = styled.div`
  width: 100%;
  height: 10px;
  background-color: #555;
  border-radius: 5px;
  margin-top: 5px;
`;

const HealthFill = styled.div<{ percentage: number }>`
  height: 100%;
  width: ${(props) => props.percentage}%;
  background-color: ${(props) => (props.percentage > 50 ? '#2ecc71' : props.percentage > 25 ? '#f39c12' : '#e74c3c')};
  border-radius: 5px;
  transition: width 0.3s ease;
`;

const EnergyBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: #555;
  border-radius: 4px;
  margin-top: 3px;
`;

const EnergyFill = styled.div<{ percentage: number }>`
  height: 100%;
  width: ${(props) => props.percentage}%;
  background-color: #3498db;
  border-radius: 4px;
  transition: width 0.3s ease;
`;

const CharacterName = styled.div`
  font-size: 12px;
  font-weight: bold;
  text-align: center;
  margin-top: 5px;
`;

const CharacterStatus = styled.div`
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 10px;
`;

interface CharacterAreaProps {
  player: PlayerState;
  isOpponent: boolean;
}

const CharacterArea: React.FC<CharacterAreaProps> = ({ player, isOpponent }) => {
  const renderCharacterCard = (character: CharacterCard, index: number) => {
    const healthPercentage = (character.health / character.maxHealth) * 100;
    const energyPercentage = (character.energy / character.maxEnergy) * 100;
    const isActive = index === player.activeCharacterIndex;

    return (
      <CharacterCardContainer key={character.id} isActive={isActive}>
        <CharacterName>{character.name}</CharacterName>
        <Card card={{ 
          id: character.id, 
          name: character.name, 
          type: character.type, 
          cost: character.cost || [], 
          description: character.description || 'Character card' 
        }} />
        <HealthBar>
          <HealthFill percentage={healthPercentage} />
        </HealthBar>
        <EnergyBar>
          <EnergyFill percentage={energyPercentage} />
        </EnergyBar>
        <CharacterStatus>
          <span>HP: {character.health}/{character.maxHealth}</span>
          <span>EP: {character.energy}/{character.maxEnergy}</span>
        </CharacterStatus>
      </CharacterCardContainer>
    );
  };

  return (
    <CharacterAreaContainer>
      {player.characters.map((character, index) => 
        renderCharacterCard(character as CharacterCard, index)
      )}
    </CharacterAreaContainer>
  );
};

export default CharacterArea;