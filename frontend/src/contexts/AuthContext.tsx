import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useCurrentUser, useOAuthLogin, useLogout, useRefreshToken } from '../hooks/useAuth'
import type { AuthContextType, OAuthTokens } from '../types'
import Cookies from 'js-cookie'

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
  const [tokens, setTokens] = useState<OAuthTokens | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  
  const queryClient = useQueryClient()
  
  // Use TanStack Query hooks
  const { data: user, isLoading: isUserLoading, error: userError } = useCurrentUser()
  const oauthLoginMutation = useOAuthLogin()
  const logoutMutation = useLogout()
  const refreshTokenMutation = useRefreshToken()

  // Initialize auth state by checking session storage and API
  useEffect(() => {
    const checkAuthStatus = async () => {
      // Check session storage for immediate auth status
      const sessionAuth = sessionStorage.getItem('isAuthenticated')
      const oauth_id = sessionStorage.getItem('oauth_id')
      const profile_picture_url = sessionStorage.getItem('profile_picture_url')
      
      if (sessionAuth === 'true') {
        // Authentication status available in session storage
        console.log('Found auth session storage', { oauth_id, profile_picture_url })
      }
      
      // HTTP-only cookies are automatically handled by the browser
      // Current user query will run and validate actual authentication
      if (!user && !userError) {
        // Small delay for TanStack Query to run
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
      setIsInitialized(true)
    }
    
    checkAuthStatus()
  }, [])

  // Handle auth errors (token invalid, etc.)
  useEffect(() => {
    if (userError && tokens) {
      // Try refreshing token first
      if (tokens.refresh_token) {
        refreshTokenMutation.mutate(tokens.refresh_token, {
          onSuccess: (newTokens) => {
            setTokens(newTokens)
            // Store new tokens in cookies
            Cookies.set('access_token', newTokens.access_token, { expires: 1/24 }) // 1 hour
            Cookies.set('refresh_token', newTokens.refresh_token || '', { expires: 30 }) // 30 days
          },
          onError: () => {
            // Refresh failed, clear tokens
            clearAuth()
          }
        })
      } else {
        clearAuth()
      }
    }
  }, [userError, tokens, queryClient, refreshTokenMutation])

  const clearAuth = () => {
    setTokens(null)
    // Clear session storage
    sessionStorage.removeItem('oauth_id')
    sessionStorage.removeItem('profile_picture_url')
    sessionStorage.removeItem('isAuthenticated')
    // HTTP-only cookies will be cleared by logout endpoint
    queryClient.clear()
  }

  const loginWithGoogle = () => {
    // Redirect to backend OAuth endpoint
    // The backend will handle the Google OAuth flow and redirect back to frontend
    const frontendCallbackUrl = `${window.location.origin}/auth/callback`
    console.log("Redirect URL:", frontendCallbackUrl)
    window.location.href = `${import.meta.env.VITE_API_URL}/api/auth/google?redirect_uri=${encodeURIComponent(frontendCallbackUrl)}`
  }

  const handleOAuthCallback = async () => {
    try {
      // Tokens are now in HTTP-only cookies set by backend
      // Just refresh user data to update authentication state
      await queryClient.invalidateQueries({ queryKey: ['currentUser'] })
      // Force refetch current user data
      await queryClient.refetchQueries({ queryKey: ['currentUser'] })
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    logoutMutation.mutate()
    clearAuth()
  }

  const isLoading = !isInitialized || isUserLoading || oauthLoginMutation.isPending || refreshTokenMutation.isPending

  const value: AuthContextType = {
    user: user || null,
    tokens,
    loginWithGoogle,
    handleOAuthCallback,
    logout,
    isLoading,
    isAuthenticated: !!user, // User existence indicates authentication
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
} 