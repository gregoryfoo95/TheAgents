import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { authAPI } from '../services/api'
import type { LoginData, RegisterData } from '../types'

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
    enabled: !!localStorage.getItem('token'),
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useLogin = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: LoginData) => authAPI.login(data),
    onSuccess: async (data) => {
      const { access_token } = data
      
      // Store token
      localStorage.setItem('token', access_token)
      
      // Fetch user data and cache it
      const userData = await authAPI.getCurrentUser()
      queryClient.setQueryData(authKeys.currentUser(), userData)
      localStorage.setItem('user', JSON.stringify(userData))
      
      toast.success('Successfully logged in!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Login failed'
      toast.error(message)
    },
  })
}

export const useRegister = () => {
  const loginMutation = useLogin()
  
  return useMutation({
    mutationFn: (data: RegisterData) => authAPI.register(data),
    onSuccess: async (_, variables) => {
      // Auto login after registration
      await loginMutation.mutateAsync({
        email: variables.email,
        password: variables.password,
      })
      toast.success('Account created successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Registration failed'
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

export const useLogout = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async () => {
      // Clear local storage
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Clear all cached data
      queryClient.clear()
      
      toast.success('Successfully logged out')
    },
  })
} 