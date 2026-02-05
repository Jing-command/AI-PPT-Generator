/**
 * 认证服务
 */

import apiClient from './api'
import type { 
  LoginRequest, 
  RegisterRequest, 
  Token, 
  User,
  ApiResponse
} from '@/types'

export const authService = {
  /**
   * 用户登录
   */
  async login(data: LoginRequest): Promise<Token> {
    const response = await apiClient.post<ApiResponse<Token>>('/auth/login', data)
    const tokenData = response.data.data
    
    // 保存 Token
    if (tokenData) {
      localStorage.setItem('access_token', tokenData.access_token)
      localStorage.setItem('refresh_token', tokenData.refresh_token)
    }
    
    return tokenData!
  },

  /**
   * 用户注册
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<ApiResponse<User>>('/auth/register', data)
    return response.data.data!
  },

  /**
   * 刷新 Token
   */
  async refreshToken(refreshToken: string): Promise<Token> {
    const response = await apiClient.post<ApiResponse<Token>>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    
    const tokenData = response.data.data
    if (tokenData) {
      localStorage.setItem('access_token', tokenData.access_token)
    }
    
    return tokenData!
  },

  /**
   * 退出登录
   */
  logout(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  /**
   * 获取当前 Token
   */
  getToken(): string | null {
    return localStorage.getItem('access_token')
  },

  /**
   * 检查是否已登录
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token')
  },
}

export default authService
