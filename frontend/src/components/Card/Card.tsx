import React from 'react';
import styled from 'styled-components';
import { Card as CardInterface, CardType, DiceType } from '../../types/game';

const CardContainer = styled.div<{ cardType: CardType }>`
  width: 120px;
  height: 160px;
  border: 2px solid var(--border, #ccc);
  border-radius: 12px;
  padding: 8px;
  margin: 4px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  background: var(--card-background, linear-gradient(135deg, #2c3e50, #4a235a));
  color: var(--text-primary, white);
  
  &:hover {
    transform: translateY(-8px) scale(1.05);
    box-shadow: 0 12px 20px rgba(0, 0, 0, 0.4);
    cursor: pointer;
  }

  ${(props) => {
    switch (props.cardType) {
      case CardType.CharacterCard:
        return `border: 2px solid var(--accent, #3498db); background: var(--card-background, linear-gradient(135deg, #1a5276, #3498db));`;
      case CardType.Weapon:
        return `border: 2px solid var(--accent-secondary, #e67e22); background: var(--card-background, linear-gradient(135deg, #ca6f1e, #e67e22));`;
      case CardType.Artifact:
        return `border: 2px solid var(--accent, #9b59b6); background: var(--card-background, linear-gradient(135deg, #6c3483, #9b59b6));`;
      case CardType.Talent:
        return `border: 2px solid var(--accent, #2ecc71); background: var(--card-background, linear-gradient(135deg, #27ae60, #2ecc71));`;
      case CardType.Support:
        return `border: 2px solid var(--accent, #f1c40f); background: var(--card-background, linear-gradient(135deg, #d68910, #f1c40f)); color: var(--text-primary, #000);`;
      case CardType.Event:
        return `border: 2px solid var(--accent, #e74c3c); background: var(--card-background, linear-gradient(135deg, #cd6155, #e74c3c));`;
      default:
        return `border: 2px solid var(--border, #95a5a6); background: var(--card-background, linear-gradient(135deg, #7f8c8d, #95a5a6));`;
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
  flex-grow: 1;
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
  border: 1px solid rgba(255, 255, 255, 0.5);
`;

const CardBody = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`;

const CardDescription = styled.p`
  font-size: 9px;
  color: var(--text-secondary, #ecf0f1);
  margin: 0;
  text-align: center;
  height: 50px;
  overflow: hidden;
`;

const CardImage = styled.div`
  width: 70px;
  height: 70px;
  border-radius: 8px;
  margin-bottom: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  color: #666;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
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
            {/* 图片注释: 卡牌图片使用了从后端传来的图片URL */}
            <img src={card.imageUrl} alt={card.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </CardImage>
        ) : (
          <CardImage style={{ 
            backgroundImage: `url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`, 
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}>
            {/* 图片注释: 当没有卡牌图片时，使用指定的默认图片image.png */}
          </CardImage>
        )}
        <CardDescription>{card.description}</CardDescription>
      </CardBody>
    </CardContainer>
  );
};

export default Card;