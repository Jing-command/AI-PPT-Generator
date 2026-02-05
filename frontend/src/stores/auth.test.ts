import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from './auth'

describe('Auth Store', () => {
  beforeEach(() => {
    // Reset store to initial state
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
  })

  it('should have initial state', () => {
    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.isAuthenticated).toBe(false)
    expect(state.isLoading).toBe(false)
    expect(state.error).toBeNull()
  })

  it('should set user', () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    
    useAuthStore.getState().setUser(mockUser)
    const state = useAuthStore.getState()
    
    expect(state.user).toEqual(mockUser)
    expect(state.isAuthenticated).toBe(true)
  })

  it('should logout', () => {
    useAuthStore.getState().setUser({
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })
    
    useAuthStore.getState().logout()
    const state = useAuthStore.getState()
    
    expect(state.user).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('should set loading state', () => {
    useAuthStore.getState().setLoading(true)
    expect(useAuthStore.getState().isLoading).toBe(true)
    
    useAuthStore.getState().setLoading(false)
    expect(useAuthStore.getState().isLoading).toBe(false)
  })

  it('should set error', () => {
    useAuthStore.getState().setError('Invalid credentials')
    expect(useAuthStore.getState().error).toBe('Invalid credentials')
  })

  it('should clear error', () => {
    useAuthStore.getState().setError('Some error')
    useAuthStore.getState().clearError()
    expect(useAuthStore.getState().error).toBeNull()
  })
})
