// 游戏相关 API

import { get, post } from "./client"
import type {
  StartGameRequest,
  StartGameResponse,
  GameActionRequest,
  GameActionResponse,
  GameStateResponse,
} from "./types"

// 开始本地游戏
export async function startLocalGame(data: StartGameRequest): Promise<StartGameResponse> {
  return post<StartGameResponse>("/api/local-game/start", data)
}

// 处理游戏行动
export async function performGameAction(sessionId: string, action: GameActionRequest): Promise<GameActionResponse> {
  return post<GameActionResponse>(`/api/local-game/${sessionId}/action`, action)
}

// 获取游戏状态
export async function getGameState(sessionId: string): Promise<GameStateResponse> {
  return get<GameStateResponse>(`/api/local-game/${sessionId}/state`)
}

// 结束游戏
export async function endGame(sessionId: string): Promise<{ message: string }> {
  return post(`/api/local-game/${sessionId}/end`)
}
