import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { stockService } from '../services/api'

export interface StockPrediction {
  symbol: string
  prediction: {
    time_frequency: string
    predictions: Array<{
      date: string
      price: number
    }>
  }
  analysis: {
    finance_guru: string
    geopolitics_guru: string
    legal_guru: string
    quant_dev: string
    financial_analyst: string
  }
  confidence_score: number
  workflow_id: string
}

export interface StockAnalysisRequest {
  symbol: string
  time_frequency: string
  user_context?: string
}

export interface StockAnalysisSession {
  session_id: string
  symbol: string
  workflow_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  service_url?: string
  prediction?: {
    time_frequency: string
    predictions: Array<{
      date: string
      price: number
    }>
  }
  analysis?: {
    [key: string]: string
  }
  confidence_score?: number
  factors_considered?: string[]
  created_at: string
  updated_at?: string
  completed_at?: string
}

export interface StockAnalysisHistory {
  session_id: string
  stock_symbol: string
  time_frequency: string
  status: string
  confidence_score?: number
  created_at: string
  completed_at?: string
}

export const useStockAnalysis = () => {
  const [pollingWorkflowId, setPollingWorkflowId] = useState<string | null>(null)

  // Create new stock analysis
  const createAnalysis = useMutation({
    mutationFn: (request: StockAnalysisRequest): Promise<any> => {
      return stockService.analyzeStock(request)
    },
    onSuccess: (data) => {
      // Start polling for status updates
      setPollingWorkflowId(data.workflow_id)
    }
  })

  // Get analysis history
  const getHistory = useQuery({
    queryKey: ['stockAnalysisHistory'],
    queryFn: (): Promise<StockAnalysisHistory[]> => {
      return stockService.getUserSessions()
    }
  })

  // Get analysis details
  const getAnalysisDetails = (sessionId: string) => {
    return useQuery({
      queryKey: ['stockAnalysisDetails', sessionId],
      queryFn: () => stockService.getAnalysisSession(sessionId),
      enabled: !!sessionId
    })
  }

  // Poll analysis status
  const analysisStatus = useQuery({
    queryKey: ['stockAnalysisStatus', pollingWorkflowId],
    queryFn: () => {
      if (!pollingWorkflowId) return null
      return stockService.getAnalysisSession(pollingWorkflowId)
    },
    enabled: !!pollingWorkflowId,
    refetchInterval: 2000, // Poll every 2 seconds while processing
    refetchOnWindowFocus: false
  })

  // Get chat messages for a session
  const getChatMessages = (sessionId: string) => {
    return useQuery({
      queryKey: ['stockAnalysisChat', sessionId],
      queryFn: () => stockService.getAnalysisSession(sessionId),
      enabled: !!sessionId,
      select: (data) => data.chat_messages || []
    })
  }

  // Get agents description
  const getAgentsDescription = useQuery({
    queryKey: ['agentsDescription'],
    queryFn: () => stockService.getAgentsDescription(),
    staleTime: 10 * 60 * 1000 // 10 minutes
  })

  // Get service health
  const getServiceHealth = useQuery({
    queryKey: ['stockServiceHealth'],
    queryFn: () => stockService.getHealth(),
    staleTime: 60 * 1000 // 1 minute
  })

  // Get supported symbols
  const getSupportedSymbols = useQuery({
    queryKey: ['supportedSymbols'],
    queryFn: () => stockService.getSupportedSymbols(),
    staleTime: 10 * 60 * 1000 // 10 minutes
  })

  // Get time frequencies
  const getTimeFrequencies = useQuery({
    queryKey: ['timeFrequencies'],
    queryFn: () => stockService.getTimeFrequencies(),
    staleTime: 10 * 60 * 1000 // 10 minutes
  })

  const stopPolling = () => {
    setPollingWorkflowId(null)
  }

  return {
    // Mutations
    createAnalysis,
    
    // Queries
    history: getHistory,
    analysisStatus,
    agentsDescription: getAgentsDescription,
    serviceHealth: getServiceHealth,
    getSupportedSymbols,
    getTimeFrequencies,
    
    // Query functions
    getAnalysisDetails,
    getChatMessages,
    
    // Polling control
    isPolling: !!pollingWorkflowId,
    stopPolling,
    
    // Loading states
    isCreating: createAnalysis.isPending,
    isLoadingHistory: getHistory.isLoading,
    
    // Error states
    createError: createAnalysis.error,
    historyError: getHistory.error,
  }
}

export default useStockAnalysis