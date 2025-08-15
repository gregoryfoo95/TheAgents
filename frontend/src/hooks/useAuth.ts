import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { authService } from '../services/api'
import type { User, UserTypeSelectionData } from '../types'

// Query keys
export const authKeys = {
  all: ['auth'] as const,
  currentUser: () => [...authKeys.all, 'currentUser'] as const,
}

// Hooks
export const useCurrentUser = () => {
  return useQuery({
    queryKey: authKeys.currentUser(),
    queryFn: authService.getCurrentUser,
    enabled: !!sessionStorage.getItem('isAuthenticated'),
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Removed local login - OAuth only

// Removed local registration - OAuth only

// Removed refresh token - using HTTP-only cookies

export const useLogout = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async () => {
      try {
        // Call logout endpoint if authenticated
        const isAuthenticated = sessionStorage.getItem('isAuthenticated')
        if (isAuthenticated) {
          await authService.logout()
        }
      } catch (error) {
        // Continue with logout even if API call fails
        console.error('Logout API call failed:', error)
      }
      
      // Clear session storage
      sessionStorage.clear()
      
      // Clear local storage
      localStorage.clear()
      
      // Clear all cached data
      queryClient.clear()
      
      // Note: HTTP-only cookies are cleared by the backend logout endpoint
      
      toast.success('Successfully logged out')
    },
  })
} 

export const useUpdateUserType = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: UserTypeSelectionData) => authService.updateUserType({
      user_type: data.user_type,
      phone: data.phone,
    }),
    onSuccess: (updatedUser: User) => {
      queryClient.setQueryData(authKeys.currentUser(), updatedUser)
      toast.success('Profile updated!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to update profile'
      toast.error(message)
    },
  })
}