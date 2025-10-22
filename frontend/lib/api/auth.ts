// 认证相关 API

import { get, post, setToken, clearToken } from "./client"
import type { LoginRequest, RegisterRequest, LoginResponse, UserProfile } from "./types"

// 用户注册
export async function register(data: RegisterRequest): Promise<{ message: string }> {
  return post("/api/auth/register", data)
}

// 用户登录
export async function login(data: LoginRequest): Promise<LoginResponse> {
  const response = await post<LoginResponse>("/api/auth/login", data)

  // 登录成功后保存 token
  if (response.access_token) {
    setToken(response.access_token)
  }

  return response
}

// 获取用户资料
export async function getProfile(): Promise<UserProfile> {
  return get<UserProfile>("/api/auth/profile")
}

// 登出
export function logout(): void {
  clearToken()
}
