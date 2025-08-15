import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useCurrentUser, useLogout, useUpdateUserType } from '../hooks/useAuth'
import { authService } from '../services/api'
import type { AuthContextType, User } from '../types'

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
  const [isInitialized, setIsInitialized] = useState(false)
  
  const queryClient = useQueryClient()
  
  // Use TanStack Query hooks - OAuth only
  const { data: user, isLoading: isUserLoading, error: userError } = useCurrentUser()
  const logoutMutation = useLogout()

  // Initialize auth state - OAuth with HTTP-only cookies
  useEffect(() => {
    const checkAuthStatus = async () => {
      // Check session storage for auth status
      const isAuthenticated = sessionStorage.getItem('isAuthenticated')
      
      if (isAuthenticated && !user && !userError) {
        // Small delay for TanStack Query to run
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      setIsInitialized(true)
    }
    
    checkAuthStatus()
  }, [])

  const clearAuth = () => {
    // Clear session storage
    sessionStorage.clear()
    
    // Clear local storage
    localStorage.clear()
    
    // Clear all cached data
    queryClient.clear()
    
    // Note: HTTP-only cookies are cleared by the backend logout endpoint
  }

  const loginWithGoogle = () => {
    authService.loginWithGoogle(window.location.origin + '/auth/callback')
  }

  const logout = () => {
    logoutMutation.mutate()
    clearAuth()
  }

  const isLoading = !isInitialized || isUserLoading

  const handleOAuthCallback = async () => {
    // Invalidate current user query to refetch user data after OAuth
    await queryClient.invalidateQueries({ queryKey: ['auth', 'currentUser'] })
  }

  const value: AuthContextType = {
    user: user || null,
    loginWithGoogle,
    logout,
    handleOAuthCallback,
    isLoading,
    isAuthenticated: !!user, // User existence indicates authentication
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
} 