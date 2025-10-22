// 卡组相关 API

import { get, post, put, del } from "./client"
import type {
  Deck,
  DecksResponse,
  DeckDetailResponse,
  CreateDeckRequest,
  UpdateDeckRequest,
  ValidateDeckRequest,
  DeckValidationResponse,
} from "./types"

// 获取用户卡组列表
export async function getDecks(): Promise<DecksResponse> {
  return get<DecksResponse>("/api/decks")
}

// 创建卡组
export async function createDeck(data: CreateDeckRequest): Promise<{ message: string; deck: Deck }> {
  return post("/api/decks", data)
}

// 更新卡组
export async function updateDeck(deckId: string, data: UpdateDeckRequest): Promise<{ message: string; deck: Deck }> {
  return put(`/api/decks/${deckId}`, data)
}

// 删除卡组
export async function deleteDeck(deckId: string): Promise<{ message: string }> {
  return del(`/api/decks/${deckId}`)
}

// 获取卡组详情
export async function getDeckDetail(deckId: string): Promise<DeckDetailResponse> {
  return get<DeckDetailResponse>(`/api/decks/${deckId}`)
}

// 验证卡组（通用）
export async function validateDeck(data: ValidateDeckRequest): Promise<DeckValidationResponse> {
  return post<DeckValidationResponse>("/api/decks/validate", data)
}

// 验证卡组（构建器专用）
export async function validateDeckBuilder(data: ValidateDeckRequest): Promise<DeckValidationResponse> {
  return post<DeckValidationResponse>("/api/deck/validate", data)
}
