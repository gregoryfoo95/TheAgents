import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { chatAPI } from '../services/api'
import type { Conversation, Message } from '../types'

// Query keys
export const chatKeys = {
  all: ['chat'] as const,
  conversations: () => [...chatKeys.all, 'conversations'] as const,
  conversation: (id: number) => [...chatKeys.all, 'conversation', id] as const,
}

// Hooks
export const useConversations = () => {
  return useQuery({
    queryKey: chatKeys.conversations(),
    queryFn: chatAPI.getConversations,
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

export const useConversation = (id: number) => {
  return useQuery({
    queryKey: chatKeys.conversation(id),
    queryFn: () => chatAPI.getConversation(id),
    enabled: !!id,
    staleTime: 30 * 1000, // 30 seconds for real-time feel
    refetchInterval: 5000, // Poll every 5 seconds for new messages
  })
}

export const useCreateConversation = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: chatAPI.createConversation,
    onSuccess: (newConversation) => {
      // Add to conversations list
      queryClient.setQueryData(chatKeys.conversations(), (old: Conversation[] | undefined) => {
        if (!old) return [newConversation]
        return [newConversation, ...old]
      })
      
      // Cache the conversation detail
      queryClient.setQueryData(chatKeys.conversation(newConversation.id), newConversation)
      
      toast.success('Conversation started!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to create conversation'
      toast.error(message)
    },
  })
}

export const useSendMessage = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: chatAPI.sendMessage,
    onSuccess: (newMessage) => {
      // Update the conversation with the new message
      queryClient.setQueryData(
        chatKeys.conversation(newMessage.conversation_id),
        (old: Conversation | undefined) => {
          if (!old) return old
          return {
            ...old,
            messages: [...old.messages, newMessage],
          }
        }
      )
      
      // Update conversations list to show latest message
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() })
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to send message'
      toast.error(message)
    },
  })
}

export const useUploadMessageFile = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ messageId, file }: { messageId: number; file: File }) =>
      chatAPI.uploadMessageFile(messageId, file),
    onSuccess: (data, variables) => {
      // Find and update the message with file info
      const conversationQueries = queryClient.getQueriesData({
        queryKey: [...chatKeys.all, 'conversation'],
      })
      
      conversationQueries.forEach(([queryKey, conversation]) => {
        if (conversation) {
          const updatedConversation = {
            ...conversation,
            messages: (conversation as Conversation).messages.map((message) =>
              message.id === variables.messageId
                ? { ...message, file_url: data.file_url, file_name: data.file_name }
                : message
            ),
          }
          queryClient.setQueryData(queryKey, updatedConversation)
        }
      })
      
      toast.success('File uploaded successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to upload file'
      toast.error(message)
    },
  })
}

export const useAddLawyerToConversation = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ conversationId, lawyerId }: { conversationId: number; lawyerId: number }) =>
      chatAPI.addLawyerToConversation(conversationId, lawyerId),
    onSuccess: (_, variables) => {
      // Invalidate the conversation to refetch with lawyer added
      queryClient.invalidateQueries({ 
        queryKey: chatKeys.conversation(variables.conversationId) 
      })
      
      // Also invalidate conversations list
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() })
      
      toast.success('Lawyer added to conversation!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to add lawyer'
      toast.error(message)
    },
  })
}

// Utility function to add a message optimistically
export const useOptimisticMessage = () => {
  const queryClient = useQueryClient()
  
  return (conversationId: number, tempMessage: Partial<Message>) => {
    queryClient.setQueryData(
      chatKeys.conversation(conversationId),
      (old: Conversation | undefined) => {
        if (!old) return old
        
        const optimisticMessage: Message = {
          id: Date.now(), // Temporary ID
          conversation_id: conversationId,
          sender_id: tempMessage.sender_id!,
          message_text: tempMessage.message_text,
          message_type: tempMessage.message_type || 'text',
          created_at: new Date().toISOString(),
          sender: tempMessage.sender!,
          // Add a temporary flag to identify optimistic updates
          ...(tempMessage as any),
          _optimistic: true,
        }
        
        return {
          ...old,
          messages: [...old.messages, optimisticMessage],
        }
      }
    )
  }
} 