import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { bookingsAPI } from '../services/api'
import type { Booking, CreateBookingData } from '../types'

// Query keys
export const bookingKeys = {
  all: ['bookings'] as const,
  lists: () => [...bookingKeys.all, 'list'] as const,
  list: (status?: string) => [...bookingKeys.lists(), status] as const,
  details: () => [...bookingKeys.all, 'detail'] as const,
  detail: (id: number) => [...bookingKeys.details(), id] as const,
  availableSlots: (propertyId: number, date: string) => 
    [...bookingKeys.all, 'availableSlots', propertyId, date] as const,
}

// Hooks
export const useMyBookings = (status?: string) => {
  return useQuery({
    queryKey: bookingKeys.list(status),
    queryFn: () => bookingsAPI.getMyBookings(status),
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

export const useBooking = (id: number) => {
  return useQuery({
    queryKey: bookingKeys.detail(id),
    queryFn: () => bookingsAPI.getBooking(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export const useAvailableSlots = (propertyId: number, date: string) => {
  return useQuery({
    queryKey: bookingKeys.availableSlots(propertyId, date),
    queryFn: () => bookingsAPI.getAvailableSlots(propertyId, date),
    enabled: !!propertyId && !!date,
    staleTime: 30 * 1000, // 30 seconds - slots can change quickly
  })
}

export const useCreateBooking = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: bookingsAPI.createBooking,
    onSuccess: (newBooking) => {
      // Add to bookings list
      queryClient.setQueryData(bookingKeys.list(), (old: Booking[] | undefined) => {
        if (!old) return [newBooking]
        return [newBooking, ...old]
      })
      
      // Cache the booking detail
      queryClient.setQueryData(bookingKeys.detail(newBooking.id), newBooking)
      
      // Invalidate available slots for the property
      queryClient.invalidateQueries({
        queryKey: [...bookingKeys.all, 'availableSlots', newBooking.property_id],
      })
      
      // Invalidate all booking lists to refresh counts
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() })
      
      toast.success('Booking created successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to create booking'
      toast.error(message)
    },
  })
}

export const useUpdateBooking = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ 
      id, 
      data 
    }: { 
      id: number; 
      data: Partial<CreateBookingData> & { status?: string } 
    }) => bookingsAPI.updateBooking(id, data),
    onSuccess: (updatedBooking) => {
      // Update the booking in cache
      queryClient.setQueryData(bookingKeys.detail(updatedBooking.id), updatedBooking)
      
      // Update in lists
      queryClient.setQueryData(bookingKeys.list(), (old: Booking[] | undefined) => {
        if (!old) return old
        return old.map(booking => 
          booking.id === updatedBooking.id ? updatedBooking : booking
        )
      })
      
      // Invalidate available slots if date/time changed
      queryClient.invalidateQueries({
        queryKey: [...bookingKeys.all, 'availableSlots', updatedBooking.property_id],
      })
      
      // Invalidate filtered lists
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() })
      
      toast.success('Booking updated successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to update booking'
      toast.error(message)
    },
  })
}

export const useCancelBooking = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: bookingsAPI.cancelBooking,
    onSuccess: (_, cancelledId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: bookingKeys.detail(cancelledId) })
      
      // Remove from lists
      queryClient.setQueryData(bookingKeys.list(), (old: Booking[] | undefined) => {
        if (!old) return old
        return old.filter(booking => booking.id !== cancelledId)
      })
      
      // Invalidate all booking lists and available slots
      queryClient.invalidateQueries({ queryKey: bookingKeys.lists() })
      queryClient.invalidateQueries({ 
        queryKey: [...bookingKeys.all, 'availableSlots'] 
      })
      
      toast.success('Booking cancelled successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to cancel booking'
      toast.error(message)
    },
  })
}

// Utility hooks for common booking operations
export const useConfirmBooking = () => {
  const updateBooking = useUpdateBooking()
  
  return useMutation({
    mutationFn: (id: number) => updateBooking.mutateAsync({ 
      id, 
      data: { status: 'confirmed' } 
    }),
    onSuccess: () => {
      toast.success('Booking confirmed!')
    },
  })
}

export const useCompleteBooking = () => {
  const updateBooking = useUpdateBooking()
  
  return useMutation({
    mutationFn: (id: number) => updateBooking.mutateAsync({ 
      id, 
      data: { status: 'completed' } 
    }),
    onSuccess: () => {
      toast.success('Booking marked as completed!')
    },
  })
} 