import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useCurrentUser, useLogin, useRegister, useLogout } from '../hooks/useAuth'
import type { AuthContextType, RegisterData } from '../types'

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  
  const queryClient = useQueryClient()
  
  // Use TanStack Query hooks
  const { data: user, isLoading: isUserLoading, error: userError } = useCurrentUser()
  const loginMutation = useLogin()
  const registerMutation = useRegister()
  const logoutMutation = useLogout()

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = () => {
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        setToken(storedToken)
      }
      setIsInitialized(true)
    }

    initAuth()
  }, [])

  // Handle auth errors (token invalid, etc.)
  useEffect(() => {
    if (userError && token) {
      // Token is invalid, clear it
      setToken(null)
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      queryClient.clear()
    }
  }, [userError, token, queryClient])

  const login = async (email: string, password: string) => {
    try {
      const response = await loginMutation.mutateAsync({ email, password })
      setToken(response.access_token)
    } catch (error) {
      throw error // Re-throw to handle in components
    }
  }

  const register = async (userData: RegisterData) => {
    try {
      await registerMutation.mutateAsync(userData)
      // loginMutation is called automatically in the register hook
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        setToken(storedToken)
      }
    } catch (error) {
      throw error // Re-throw to handle in components
    }
  }

  const logout = () => {
    logoutMutation.mutate()
    setToken(null)
  }

  const isLoading = !isInitialized || isUserLoading || loginMutation.isPending || registerMutation.isPending

  const value: AuthContextType = {
    user: user || null,
    token,
    login,
    register,
    logout,
    isLoading,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
} 