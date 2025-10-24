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
  console.log('[API] 发起请求:', { endpoint, hasToken: !!token })

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
    console.log('[API] 正在发送请求:', url);
    const response = await fetch(url, {
      ...options,
      headers,
    })

    // 检查响应是否为授权错误
    if (response.status === 401 || response.status === 403) {
      console.log('[API] 检测到认证错误:', response.status);
      let errorData;
      try {
        errorData = await response.json();
        console.log('[API] 错误数据:', errorData);
      } catch (e) {
        // 如果无法解析JSON，创建一个默认错误对象
        errorData = { message: `HTTP error! status: ${response.status}` };
        console.log('[API] 无法解析错误响应，使用默认错误:', errorData);
      }
      
      // 检查是否为认证相关的错误，包括消息字段为msg的情况
      const isAuthError = errorData.message?.includes('Missing Authorization Header') ||
                         errorData.message?.includes('Token has expired') ||
                         errorData.message?.includes('Invalid token') ||
                         errorData.msg?.includes('Missing Authorization Header') ||
                         errorData.msg?.includes('Token has expired') ||
                         errorData.msg?.includes('Invalid token');
      
      console.log('[API] 是否为认证错误:', isAuthError);
      
      if (isAuthError) {
        console.log('[API] 认证错误，清除token并重定向到登录页');
        // 清除无效的token
        clearToken();
        // 在客户端环境中重定向到登录页面
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        // 抛出错误以通知调用方
        const errorMessage = errorData.message || errorData.msg || `HTTP error! status: ${response.status}`;
        throw new Error('AUTH_ERROR: ' + errorMessage);
      } else {
        console.log('[API] 非认证错误，直接抛出');
        throw new Error(errorData.error || errorData.message || errorData.msg || `HTTP error! status: ${response.status}`)
      }
    }

    // 处理非 JSON 响应
    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      console.log('[API] 非JSON响应，返回空对象');
      return {} as T
    }

    const data = await response.json()

    if (!response.ok) {
      console.log('[API] 响应不成功，抛出错误:', data);
      throw new Error(data.error || data.message || `HTTP error! status: ${response.status}`)
    }

    console.log('[API] 请求成功，返回数据');
    return data as T
  } catch (error) {
    // 如果是认证错误，这里也处理
    if (error instanceof Error && error.message.startsWith('AUTH_ERROR:')) {
      console.log('[API] 重新抛出认证错误:', error.message);
      throw error; // 重新抛出认证错误，让上层处理
    }
    
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
