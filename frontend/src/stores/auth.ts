/**
 * 认证状态管理
 * Zustand Store
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '@/services/api'
import type { User, Token } from '@/types'

interface AuthState {
  // 状态
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  setUser: (user: User | null) => void
  setAuthenticated: (value: boolean) => void
  setLoading: (value: boolean) => void
  setError: (message: string | null) => void
  clearError: () => void
  login: (token: Token, user: User) => void
  logout: () => void
  fetchCurrentUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setAuthenticated: (value) => set({ isAuthenticated: value }),
      setLoading: (value) => set({ isLoading: value }),
      setError: (message) => set({ error: message }),
      clearError: () => set({ error: null }),
      
      login: (token, user) => {
        localStorage.setItem('access_token', token.access_token)
        localStorage.setItem('refresh_token', token.refresh_token)
        set({ user, isAuthenticated: true, error: null })
      },
      
      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, isAuthenticated: false, error: null })
      },

      fetchCurrentUser: async () => {
        try {
          const response = await apiClient.get('/users/me')
          const userData = response.data.data
          if (userData) {
            set({ user: userData })
          }
        } catch (err) {
          console.error('Failed to fetch current user:', err)
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)

export default useAuthStore
