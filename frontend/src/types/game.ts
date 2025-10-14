// Game Types for Genshin Impact Card Game

export enum ElementType {
  Anemo = 'Anemo',
  Cryo = 'Cryo',
  Dendro = 'Dendro',
  Electro = 'Electro',
  Geo = 'Geo',
  Hydro = 'Hydro',
  Pyro = 'Pyro',
  Physical = 'Physical',
  Piercing = 'Piercing'
}

export enum CardType {
  CharacterCard = 'CharacterCard',
  Equipment = 'Equipment',
  Talent = 'Talent',
  Weapon = 'Weapon',
  Artifact = 'Artifact',
  Support = 'Support',
  Event = 'Event'
}

export enum DiceType {
  Anemo = 'Anemo',
  Cryo = 'Cryo',
  Dendro = 'Dendro',
  Electro = 'Electro',
  Geo = 'Geo',
  Hydro = 'Hydro',
  Pyro = 'Pyro',
  Omni = 'Omni'
}

export interface Card {
  id: string;
  name: string;
  type: CardType;
  cost: DiceType[];
  description: string;
  imageUrl?: string;
}

export interface CharacterCard extends Card {
  health: number;
  maxHealth: number;
  energy: number;
  maxEnergy: number;
  element: ElementType;
  skills: Skill[];
  isActive: boolean;
}

export interface Skill {
  id: string;
  name: string;
  type: 'Normal Attack' | 'Elemental Skill' | 'Elemental Burst';
  cost: DiceType[];
  description: string;
}

export interface PlayerState {
  id: string;
  name: string;
  characters: CharacterCard[];
  activeCharacterIndex: number;
  hand: Card[];
  dice: DiceType[];
  supportCards: Card[];
  summons: Card[];
  maxHandSize: number;
  maxDiceCount: number;
  maxSupportCount: number;
  maxSummonCount: number;
}

export interface GameState {
  players: [PlayerState, PlayerState];
  currentPlayerIndex: number;
  round: number;
  maxRounds: number;
  phase: 'Roll' | 'Action' | 'End';
  turn: number;
  turnPhase: 'Action' | 'End';
  dice: DiceType[];
  gameLog: string[];
  gameEnded: boolean;
  winnerId?: string;
}

// Additional types for game actions
export enum GameActionType {
  PlayCard = 'PlayCard',
  UseSkill = 'UseSkill',
  SwitchCharacter = 'SwitchCharacter',
  EndTurn = 'EndTurn',
  Pass = 'Pass'
}

export interface GameAction {
  type: GameActionType;
  payload: any;
}