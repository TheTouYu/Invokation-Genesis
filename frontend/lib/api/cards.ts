// 卡牌相关 API

import { get } from "./client"
import type { Card, CardsResponse, CardDetailResponse, CardFilters, CharacterFilters, CardFiltersResponse } from "./types"

// 获取所有卡牌
export async function getCards(filters?: CardFilters): Promise<CardsResponse> {
  return get<CardsResponse>("/api/cards", filters)
}

// 获取卡牌详情
export async function getCardDetail(cardId: string): Promise<CardDetailResponse> {
  return get<CardDetailResponse>(`/api/cards/${cardId}`)
}

// 获取卡牌类型列表
export async function getCardTypes(): Promise<{ types: string[] }> {
  return get("/api/cards/types")
}

// 获取元素类型列表
export async function getElements(): Promise<{ elements: string[] }> {
  return get("/api/cards/elements")
}

// 获取国家列表
export async function getCountries(): Promise<{ countries: string[] }> {
  return get("/api/cards/countries")
}

// 获取武器类型列表
export async function getWeaponTypes(): Promise<{ weapon_types: string[] }> {
  return get("/api/cards/weapon_types")
}

// 获取卡牌标签列表
export async function getTags(): Promise<{ tags: string[] }> {
  return get("/api/cards/tags")
}

// 获取随机卡牌
export async function getRandomCards(params?: {
  type?: string
  element?: string
  country?: string
  weapon_type?: string
  count?: number
}): Promise<{ cards: Card[]; total: number }> {
  return get("/api/cards/random", params)
}

// 获取角色过滤选项
export async function getCharacterFilters(): Promise<{
  countries: string[]
  elements: string[]
  weapon_types: string[]
}> {
  return get("/api/characters/filters")
}

// 搜索卡牌
export async function searchCards(filters?: CardFilters): Promise<CardsResponse> {
  return get<CardsResponse>("/api/cards/search", filters)
}

// 过滤卡牌
export async function filterCards(filters?: CardFilters): Promise<{ cards: Card[]; total: number }> {
  return get("/api/cards/filter", filters)
}

// 获取角色牌列表
export async function getCharacters(params?: { page?: number; per_page?: number }): Promise<Card[]> {
  return get<Card[]>("/api/characters", params)
}

// 获取装备牌列表
export async function getEquipments(params?: { page?: number; per_page?: number }): Promise<Card[]> {
  return get<Card[]>("/api/equipments", params)
}

// 获取支援牌列表
export async function getSupports(params?: { page?: number; per_page?: number }): Promise<Card[]> {
  return get<Card[]>("/api/supports", params)
}

// 获取事件牌列表
export async function getEvents(params?: { page?: number; per_page?: number }): Promise<Card[]> {
  return get<Card[]>("/api/events", params)
}

// 获取角色过滤参数
export async function getCharacterFilterOptions(): Promise<CharacterFilters> {
  return get("/api/characters/filters")
}

// 获取通用卡牌过滤参数
export async function getCardFilterOptions(): Promise<CardFiltersResponse> {
  return get("/api/cards/filter")
}

// 获取所有过滤选项
export async function getAllFilters(): Promise<CardFiltersResponse> {
  return get("/api/filters")
}
