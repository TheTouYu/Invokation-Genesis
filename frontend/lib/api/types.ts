// API 类型定义

// 通用响应类型
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

// 认证相关类型
export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  email?: string
}

export interface LoginResponse {
  access_token: string
}

export interface UserProfile {
  id: string
  username: string
}

// 卡牌相关类型
export interface CardCost {
  type: string
  value: number
}

export interface CardSkill {
  name: string
  description: string
  cost: CardCost[]
}

export interface Card {
  id: string
  name: string
  type: string
  description: string
  cost: CardCost[]
  rarity: number
  element_type?: string
  character_subtype?: string
  image_url?: string
  country?: string
  element?: string
  weapon_type?: string
  skills?: CardSkill[]
  title?: string
  health?: number
  energy?: number
  max_health?: number
  max_energy?: number
}

export interface CardsResponse {
  cards: Card[]
  total: number
  pages: number
  current_page: number
  per_page: number
  has_next: boolean
  has_prev: boolean
}

export interface CardDetailResponse {
  card: Card
}

export interface CardFilters {
  type?: string
  element?: string
  country?: string
  weapon_type?: string
  character_subtype?: string
  rarity?: number
  search?: string
  tag?: string[]
  page?: number
  per_page?: number
}

// 卡组相关类型
export interface Deck {
  id: string
  name: string
  description?: string
  cards: string[] | Card[]
  created_at: string
  updated_at?: string
}

export interface DecksResponse {
  decks: Deck[]
}

export interface DeckDetailResponse {
  deck: Deck
}

export interface CreateDeckRequest {
  name: string
  description?: string
  cards?: string[]
}

export interface UpdateDeckRequest {
  name?: string
  description?: string
  cards?: string[]
}

export interface ValidateDeckRequest {
  cards?: string[]
  characters?: string[]
  deck_name?: string
}

export interface DeckValidationResponse {
  valid?: boolean
  is_valid?: boolean
  rules?: {
    character_count?: boolean
    character_count_msg?: string
    deck_size?: boolean
    deck_size_msg?: string
    character_limit?: boolean
    character_limit_msg?: string
    card_limit?: boolean
    card_limit_msg?: string
    elemental_synergy?: boolean
    elemental_synergy_msg?: string
  }
  errors: string[]
  warnings?: string[]
  suggestions?: string[]
  details?: {
    character_count?: number
    total_cards?: number
    element_composition?: string[]
  }
}

// 过滤器类型
export interface CharacterFilters {
  countries: string[]
  elements: string[]
  weapon_types: string[]
}

export interface CardFiltersResponse {
  card_types: string[]
  countries: string[]
  elements: string[]
  tags: string[]
  weapon_types: string[]
}

// 游戏相关类型
export interface GameCharacter {
  id: string
  name: string
  health: number
  max_health: number
  energy: number
  max_energy: number
  element_type: string
  weapon_type: string
  status: string
  skills: CardSkill[]
}

export interface GamePlayer {
  player_id: string
  characters: GameCharacter[]
  active_character_index: number
  hand_cards: Card[]
  dice: string[]
  supports: any[]
  summons: any[]
}

export interface GameState {
  players: GamePlayer[]
  current_player_index: number
  round_number: number
  phase: string
  round_actions: number
  game_log: string[]
  is_game_over: boolean
  winner: string | null
}

export interface StartGameRequest {
  deck_id: string
  opponent_type?: "ai" | "human"
}

export interface StartGameResponse {
  game_session_id: string
  message: string
  game_state: GameState
}

export interface GameActionRequest {
  action_type:
    | "PLAY_CARD"
    | "USE_SKILL"
    | "SWITCH_CHARACTER"
    | "PASS"
    | "REROLL_DICE"
    | "ELEMENTAL_TUNING"
    | "REPLACE_CARDS"
    | "QUICK_ACTION"
    | "COMBAT_ACTION"
  payload?: any
}

export interface GameActionResponse {
  game_session_id: string
  message: string
  game_state: GameState
}

export interface GameStateResponse {
  game_session_id: string
  game_state: GameState
}
