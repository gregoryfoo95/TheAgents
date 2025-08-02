import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { aiAPI } from '../services/api'
import type { AIValuation, AIRecommendation } from '../types'

// Query keys
export const aiKeys = {
  all: ['ai'] as const,
  valuations: (propertyId: number) => [...aiKeys.all, 'valuations', propertyId] as const,
  recommendations: (propertyId: number) => [...aiKeys.all, 'recommendations', propertyId] as const,
  marketTrends: (zipCode: string) => [...aiKeys.all, 'marketTrends', zipCode] as const,
}

// Hooks
export const usePropertyValuations = (propertyId: number) => {
  return useQuery({
    queryKey: aiKeys.valuations(propertyId),
    queryFn: () => aiAPI.getPropertyValuations(propertyId),
    enabled: !!propertyId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const usePropertyRecommendations = (propertyId: number) => {
  return useQuery({
    queryKey: aiKeys.recommendations(propertyId),
    queryFn: () => aiAPI.getSavedRecommendations(propertyId),
    enabled: !!propertyId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useMarketTrends = (zipCode: string) => {
  return useQuery({
    queryKey: aiKeys.marketTrends(zipCode),
    queryFn: () => aiAPI.getMarketTrends(zipCode),
    enabled: !!zipCode && zipCode.length >= 5,
    staleTime: 30 * 60 * 1000, // 30 minutes
  })
}

export const useValuateProperty = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: aiAPI.valuateProperty,
    onSuccess: (newValuation, propertyId) => {
      // Add to valuations list
      queryClient.setQueryData(
        aiKeys.valuations(propertyId),
        (old: AIValuation[] | undefined) => {
          if (!old) return [newValuation]
          return [newValuation, ...old]
        }
      )
      
      toast.success('Property valuation completed!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to valuate property'
      toast.error(message)
    },
  })
}

export const useGenerateRecommendations = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: aiAPI.getImprovementRecommendations,
    onSuccess: (newRecommendations, propertyId) => {
      // Update recommendations cache
      queryClient.setQueryData(
        aiKeys.recommendations(propertyId),
        (old: AIRecommendation[] | undefined) => {
          if (!old) return newRecommendations
          // Merge new recommendations with existing ones, avoiding duplicates
          const existingIds = old.map(r => r.id)
          const uniqueNew = newRecommendations.filter(r => !existingIds.includes(r.id))
          return [...uniqueNew, ...old]
        }
      )
      
      toast.success(`${newRecommendations.length} new recommendation(s) generated!`)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to generate recommendations'
      toast.error(message)
    },
  })
}

export const useAnalyzeImage = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ propertyId, file }: { propertyId: number; file: File }) =>
      aiAPI.analyzeImage(propertyId, file),
    onSuccess: (_, variables) => {
      // The analysis includes recommendations, we could optionally cache these
      // but they're typically viewed immediately and not stored long-term
      
      toast.success('Image analysis completed!')
      
      // Optionally invalidate recommendations to include any new ones
      queryClient.invalidateQueries({
        queryKey: aiKeys.recommendations(variables.propertyId)
      })
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to analyze image'
      toast.error(message)
    },
  })
}

// Utility hooks for common AI operations
export const useLatestValuation = (propertyId: number) => {
  const { data: valuations } = usePropertyValuations(propertyId)
  return valuations?.[0] // Most recent valuation
}

export const useHighPriorityRecommendations = (propertyId: number) => {
  const { data: recommendations } = usePropertyRecommendations(propertyId)
  return recommendations?.filter(r => r.priority === 'high') || []
}

export const useRecommendationsByType = (propertyId: number, type: string) => {
  const { data: recommendations } = usePropertyRecommendations(propertyId)
  return recommendations?.filter(r => r.recommendation_type === type) || []
}

// Hook for automatic valuation when property data changes
export const useAutoValuation = (propertyId: number) => {
  const valuateProperty = useValuateProperty()
  
  return useMutation({
    mutationFn: () => valuateProperty.mutateAsync(propertyId),
    onSuccess: () => {
      toast.success('Auto-valuation completed!')
    },
  })
} 