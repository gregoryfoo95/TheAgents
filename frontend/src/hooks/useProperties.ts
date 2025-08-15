import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { propertiesService } from '../services/api'
import type { PropertyFilters, CreatePropertyData, UpdatePropertyData } from '../types'

// Query keys
export const propertyKeys = {
  all: ['properties'] as const,
  lists: () => [...propertyKeys.all, 'list'] as const,
  list: (filters: PropertyFilters) => [...propertyKeys.lists(), filters] as const,
  details: () => [...propertyKeys.all, 'detail'] as const,
  detail: (id: number) => [...propertyKeys.details(), id] as const,
  myProperties: () => [...propertyKeys.all, 'myProperties'] as const,
}

// Hooks
export const useProperties = (filters: PropertyFilters = {}, page: number = 1, size: number = 20) => {
  return useQuery({
    queryKey: [...propertyKeys.list(filters), page, size],
    queryFn: () => propertiesService.getProperties(page, size, filters),
    placeholderData: (previousData) => previousData,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export const useInfiniteProperties = (filters: PropertyFilters = {}, size: number = 20) => {
  return useInfiniteQuery({
    queryKey: [...propertyKeys.list(filters), 'infinite'],
    queryFn: ({ pageParam = 1 }) => propertiesService.getProperties(pageParam, size, filters),
    initialPageParam: 1,
    getNextPageParam: (lastPage, pages) => {
      const currentPage = pages.length
      return currentPage < lastPage.total_pages ? currentPage + 1 : undefined
    },
    staleTime: 2 * 60 * 1000,
  })
}

export const useProperty = (id: number) => {
  return useQuery({
    queryKey: propertyKeys.detail(id),
    queryFn: () => propertiesService.getProperty(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useMyProperties = () => {
  return useQuery({
    queryKey: propertyKeys.myProperties(),
    queryFn: propertiesService.getMyProperties,
    staleTime: 2 * 60 * 1000,
  })
}

export const useCreateProperty = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: CreatePropertyData) => propertiesService.createProperty(data),
    onSuccess: (newProperty) => {
      // Invalidate and refetch properties lists
      queryClient.invalidateQueries({ queryKey: propertyKeys.lists() })
      queryClient.invalidateQueries({ queryKey: propertyKeys.myProperties() })
      
      // Add the new property to cache
      queryClient.setQueryData(propertyKeys.detail(newProperty.id), newProperty)
      
      toast.success('Property created successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to create property'
      toast.error(message)
    },
  })
}

export const useUpdateProperty = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdatePropertyData }) =>
      propertiesService.updateProperty(id, data),
    onSuccess: (updatedProperty) => {
      // Update the property in cache
      queryClient.setQueryData(propertyKeys.detail(updatedProperty.id), updatedProperty)
      
      // Invalidate lists to ensure they're updated
      queryClient.invalidateQueries({ queryKey: propertyKeys.lists() })
      queryClient.invalidateQueries({ queryKey: propertyKeys.myProperties() })
      
      toast.success('Property updated successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to update property'
      toast.error(message)
    },
  })
}

export const useDeleteProperty = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: propertiesService.deleteProperty,
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: propertyKeys.detail(deletedId) })
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: propertyKeys.lists() })
      queryClient.invalidateQueries({ queryKey: propertyKeys.myProperties() })
      
      toast.success('Property deleted successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to delete property'
      toast.error(message)
    },
  })
}

export const useUploadPropertyImages = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ propertyId, files }: { propertyId: number; files: File[] }) =>
      propertiesService.uploadImages(propertyId, files),
    onSuccess: (data, variables) => {
      // Invalidate property detail to refetch with new images
      queryClient.invalidateQueries({ queryKey: propertyKeys.detail(variables.propertyId) })
      
      toast.success(`${data.uploaded_images.length} image(s) uploaded successfully!`)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to upload images'
      toast.error(message)
    },
  })
} 