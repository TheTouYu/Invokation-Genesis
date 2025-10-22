// API 客户端基础配置

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000"

// 获取存储的 token
export function getToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("access_token")
}

// 设置 token
export function setToken(token: string): void {
  if (typeof window === "undefined") return
  localStorage.setItem("access_token", token)
}

// 清除 token
export function clearToken(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem("access_token")
}

// 通用请求函数
export async function apiRequest<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  }

  // 如果有 token，添加到请求头
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const url = `${API_BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    // 处理非 JSON 响应
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return {} as T
    }

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || data.message || `HTTP error! status: ${response.status}`)
    }

    return data as T
  } catch (error) {
    console.error("[v0] API request failed:", error)
    throw error
  }
}

// GET 请求
export async function get<T = any>(endpoint: string, params?: Record<string, any>): Promise<T> {
  const queryString = params
    ? "?" +
      new URLSearchParams(
        Object.entries(params).reduce((acc, [key, value]) => {
          if (value !== undefined && value !== null) {
            if (Array.isArray(value)) {
              // 处理数组参数
              value.forEach((v) => acc.append(key, String(v)))
            } else {
              acc.append(key, String(value))
            }
          }
          return acc
        }, new URLSearchParams()),
      ).toString()
    : ""

  return apiRequest<T>(endpoint + queryString, {
    method: "GET",
  })
}

// POST 请求
export async function post<T = any>(endpoint: string, data?: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "POST",
    body: data ? JSON.stringify(data) : undefined,
  })
}

// PUT 请求
export async function put<T = any>(endpoint: string, data?: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "PUT",
    body: data ? JSON.stringify(data) : undefined,
  })
}

// DELETE 请求
export async function del<T = any>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: "DELETE",
  })
}
