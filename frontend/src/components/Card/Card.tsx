import React from 'react';
import styled from 'styled-components';
import { Card as CardInterface, CardType, DiceType } from '../../types/game';

const CardContainer = styled.div<{ cardType: CardType }>`
  width: 120px;
  height: 160px;
  border: 2px solid #ccc;
  border-radius: 8px;
  padding: 8px;
  margin: 4px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    cursor: pointer;
  }

  ${(props) => {
    switch (props.cardType) {
      case CardType.CharacterCard:
        return 'border-color: #3498db; background-color: #e1f0fa;';
      case CardType.Weapon:
        return 'border-color: #e67e22; background-color: #fae5d3;';
      case CardType.Artifact:
        return 'border-color: #9b59b6; background-color: #ead5f3;';
      case CardType.Talent:
        return 'border-color: #2ecc71; background-color: #d5f5e3;';
      case CardType.Support:
        return 'border-color: #f1c40f; background-color: #fef9e7;';
      case CardType.Event:
        return 'border-color: #e74c3c; background-color: #fadbd8;';
      default:
        return 'border-color: #95a5a6; background-color: #f5f5f5;';
    }
  }}
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
`;

const CardTitle = styled.h3`
  font-size: 12px;
  font-weight: bold;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const CardCost = styled.div`
  display: flex;
  gap: 2px;
`;

const CostElement = styled.div<{ color: string }>`
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: ${(props) => props.color};
`;

const CardBody = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`;

const CardDescription = styled.p`
  font-size: 10px;
  color: #333;
  margin: 0;
  text-align: center;
`;

const CardImage = styled.div`
  width: 60px;
  height: 60px;
  background-color: #ddd;
  border-radius: 8px;
  margin-bottom: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  color: #666;
`;

interface CardProps {
  card: CardInterface;
  onClick?: () => void;
  disabled?: boolean;
}

const Card: React.FC<CardProps> = ({ card, onClick, disabled }) => {
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

  const renderCost = () => {
    return card.cost.map((costType: DiceType, index: number) => (
      <CostElement key={index} color={getElementTypeColor(costType)} />
    ));
  };

  return (
    <CardContainer 
      cardType={card.type} 
      onClick={!disabled ? onClick : undefined}
      style={{ opacity: disabled ? 0.5 : 1, cursor: disabled ? 'not-allowed' : 'pointer' }}
    >
      <CardHeader>
        <CardTitle>{card.name}</CardTitle>
        <CardCost>
          {renderCost()}
        </CardCost>
      </CardHeader>
      <CardBody>
        {card.imageUrl ? (
          <CardImage>
            <img src={card.imageUrl} alt={card.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </CardImage>
        ) : (
          <CardImage>
            CARD IMG
          </CardImage>
        )}
        <CardDescription>{card.description}</CardDescription>
      </CardBody>
    </CardContainer>
  );
};

export default Card;