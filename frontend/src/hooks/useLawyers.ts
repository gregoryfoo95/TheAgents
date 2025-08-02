import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { lawyersAPI } from '../services/api'
import type { LawyerProfile } from '../types'

// Query keys
export const lawyerKeys = {
  all: ['lawyers'] as const,
  lists: () => [...lawyerKeys.all, 'list'] as const,
  list: (filters: {
    specialization?: string
    min_experience?: number
    max_rate?: number
    verified_only?: boolean
  }) => [...lawyerKeys.lists(), filters] as const,
  details: () => [...lawyerKeys.all, 'detail'] as const,
  detail: (id: number) => [...lawyerKeys.details(), id] as const,
  myProfile: () => [...lawyerKeys.all, 'myProfile'] as const,
  specializations: () => [...lawyerKeys.all, 'specializations'] as const,
}

// Hooks
export const useLawyers = (filters: {
  specialization?: string
  min_experience?: number
  max_rate?: number
  verified_only?: boolean
} = {}) => {
  return useQuery({
    queryKey: lawyerKeys.list(filters),
    queryFn: () => lawyersAPI.getLawyers(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useLawyer = (id: number) => {
  return useQuery({
    queryKey: lawyerKeys.detail(id),
    queryFn: () => lawyersAPI.getLawyer(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useMyLawyerProfile = () => {
  return useQuery({
    queryKey: lawyerKeys.myProfile(),
    queryFn: lawyersAPI.getMyProfile,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false, // Don't retry if user is not a lawyer
  })
}

export const useLawyerSpecializations = () => {
  return useQuery({
    queryKey: lawyerKeys.specializations(),
    queryFn: lawyersAPI.getSpecializations,
    staleTime: 60 * 60 * 1000, // 1 hour - specializations don't change often
  })
}

export const useCreateLawyerProfile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: lawyersAPI.createProfile,
    onSuccess: (newProfile) => {
      // Cache the new profile
      queryClient.setQueryData(lawyerKeys.myProfile(), newProfile)
      queryClient.setQueryData(lawyerKeys.detail(newProfile.id), newProfile)
      
      // Invalidate lawyers lists to include the new profile
      queryClient.invalidateQueries({ queryKey: lawyerKeys.lists() })
      
      toast.success('Lawyer profile created successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to create lawyer profile'
      toast.error(message)
    },
  })
}

export const useUpdateLawyerProfile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: lawyersAPI.updateProfile,
    onSuccess: (updatedProfile) => {
      // Update cached profiles
      queryClient.setQueryData(lawyerKeys.myProfile(), updatedProfile)
      queryClient.setQueryData(lawyerKeys.detail(updatedProfile.id), updatedProfile)
      
      // Update in lists
      queryClient.setQueryData(lawyerKeys.lists(), (oldData: any) => {
        if (!oldData) return oldData
        return oldData.map((lawyer: LawyerProfile) =>
          lawyer.id === updatedProfile.id ? updatedProfile : lawyer
        )
      })
      
      // Invalidate all lawyer lists to ensure consistency
      queryClient.invalidateQueries({ queryKey: lawyerKeys.lists() })
      
      toast.success('Lawyer profile updated successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to update lawyer profile'
      toast.error(message)
    },
  })
}

// Utility hooks for filtering lawyers
export const useVerifiedLawyers = () => {
  return useLawyers({ verified_only: true })
}

export const useLawyersBySpecialization = (specialization: string) => {
  return useLawyers({ specialization })
}

export const useAffordableLawyers = (maxRate: number) => {
  return useLawyers({ max_rate: maxRate })
}

export const useExperiencedLawyers = (minExperience: number) => {
  return useLawyers({ min_experience: minExperience })
} 