import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { authAPI } from '../services/api'
import type { OAuthTokens, UserTypeSelectionData } from '../types'
import Cookies from 'js-cookie'

// Query keys
export const authKeys = {
  all: ['auth'] as const,
  currentUser: () => [...authKeys.all, 'currentUser'] as const,
}

// Hooks
export const useCurrentUser = () => {
  return useQuery({
    queryKey: authKeys.currentUser(),
    queryFn: authAPI.getCurrentUser,
    enabled: !!Cookies.get('access_token'),
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useOAuthLogin = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (tokens: OAuthTokens) => {
      // Store tokens in cookies
      Cookies.set('access_token', tokens.access_token, { expires: 1/24 }) // 1 hour
      if (tokens.refresh_token) {
        Cookies.set('refresh_token', tokens.refresh_token, { expires: 30 }) // 30 days
      }
      
      // Fetch user data and cache it
      const userData = await authAPI.getCurrentUser()
      queryClient.setQueryData(authKeys.currentUser(), userData)
      
      return userData
    },
    onSuccess: () => {
      toast.success('Successfully logged in!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'OAuth login failed'
      toast.error(message)
    },
  })
}

export const useUpdateUserType = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: UserTypeSelectionData) => authAPI.updateUserType(data),
    onSuccess: (updatedUser) => {
      // Update cached user data
      queryClient.setQueryData(authKeys.currentUser(), updatedUser)
      toast.success('User type updated successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'User type update failed'
      toast.error(message)
    },
  })
}

export const useUpdateProfile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: authAPI.updateProfile,
    onSuccess: (updatedUser) => {
      // Update cached user data
      queryClient.setQueryData(authKeys.currentUser(), updatedUser)
      localStorage.setItem('user', JSON.stringify(updatedUser))
      toast.success('Profile updated successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Profile update failed'
      toast.error(message)
    },
  })
}

export const useRefreshToken = () => {
  return useMutation({
    mutationFn: (refreshToken: string) => authAPI.refreshToken(refreshToken),
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Token refresh failed'
      toast.error(message)
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async () => {
      try {
        // Call logout endpoint if token exists
        const accessToken = Cookies.get('access_token')
        if (accessToken) {
          await authAPI.logout()
        }
      } catch (error) {
        // Continue with logout even if API call fails
        console.error('Logout API call failed:', error)
      }
      
      // Clear cookies
      Cookies.remove('access_token')
      Cookies.remove('refresh_token')
      
      // Clear all cached data
      queryClient.clear()
      
      toast.success('Successfully logged out')
    },
  })
} 