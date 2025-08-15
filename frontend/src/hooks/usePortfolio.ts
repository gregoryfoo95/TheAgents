import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { stockService } from '../services/api'

export interface PortfolioStock {
  id?: number
  symbol: string
  allocation_percentage: number
  shares?: number
  purchase_price?: number
  created_at?: string
}

export interface Portfolio {
  id: number
  name: string
  description?: string
  stocks: PortfolioStock[]
  created_at: string
  updated_at: string
}

export interface PortfolioCreateRequest {
  name: string
  description?: string
  stocks: Omit<PortfolioStock, 'id' | 'created_at'>[]
}

export interface PortfolioAnalysisRequest {
  portfolio_id: number
  time_frequency: string
  analysis_type: string
}

export interface PortfolioAnalysisSession {
  session_id: string
  portfolio_id: number
  status: string
  analysis_type: string
  time_frequency: string
  created_at: string
}

export const usePortfolio = () => {
  const queryClient = useQueryClient()
  const [pollingSessionId, setPollingSessionId] = useState<string | null>(null)

  // Create new portfolio
  const createPortfolio = useMutation({
    mutationFn: (data: PortfolioCreateRequest): Promise<Portfolio> => {
      return stockService.createPortfolio({
        name: data.name,
        description: data.description,
        stocks: data.stocks
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
    }
  })

  // Get user's portfolios
  const getPortfolios = useQuery({
    queryKey: ['portfolios'],
    queryFn: (): Promise<Portfolio[]> => {
      return stockService.getPortfolios()
    }
  })

  // Get specific portfolio
  const getPortfolio = (portfolioId: number) => {
    return useQuery({
      queryKey: ['portfolio', portfolioId],
      queryFn: (): Promise<Portfolio> => {
        return stockService.getPortfolio(portfolioId)
      },
      enabled: !!portfolioId
    })
  }

  // Start portfolio analysis
  const analyzePortfolio = useMutation({
    mutationFn: (data: PortfolioAnalysisRequest): Promise<any> => {
      return stockService.analyzePortfolio(data.portfolio_id, data.time_frequency)
    },
    onSuccess: (data) => {
      setPollingSessionId(data.workflow_id || data.session_id)
    }
  })

  // Poll analysis status
  const analysisStatus = useQuery({
    queryKey: ['portfolioAnalysisStatus', pollingSessionId],
    queryFn: () => {
      if (!pollingSessionId) return null
      return stockService.getAnalysisSession(pollingSessionId)
    },
    enabled: !!pollingSessionId,
    refetchInterval: (data) => {
      if (!data?.data || data.data.status === 'completed' || data.data.status === 'failed') {
        return false
      }
      return 3000 // Poll every 3 seconds while processing
    },
    refetchOnWindowFocus: false
  })

  // Get portfolio analysis results
  const getAnalysisResults = (sessionId: string) => {
    return useQuery({
      queryKey: ['portfolioAnalysisResults', sessionId],
      queryFn: () => stockService.getAnalysisSession(sessionId),
      enabled: !!sessionId
    })
  }

  // Get portfolio analyses history
  const getPortfolioAnalyses = (portfolioId: number) => {
    return useQuery({
      queryKey: ['portfolioAnalyses', portfolioId],
      queryFn: () => stockService.getUserSessions(),
      enabled: !!portfolioId
    })
  }

  // Delete portfolio
  const deletePortfolio = useMutation({
    mutationFn: (portfolioId: number): Promise<void> => {
      return stockService.deletePortfolio(portfolioId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
    }
  })

  const stopPolling = () => {
    setPollingSessionId(null)
  }

  return {
    // Mutations
    createPortfolio,
    analyzePortfolio,
    deletePortfolio,
    
    // Queries
    portfolios: getPortfolios,
    analysisStatus,
    
    // Query functions
    getPortfolio,
    getAnalysisResults,
    getPortfolioAnalyses,
    
    // Polling control
    isPolling: !!pollingSessionId,
    stopPolling,
    
    // Loading states
    isCreating: createPortfolio.isPending,
    isAnalyzing: analyzePortfolio.isPending,
    isDeleting: deletePortfolio.isPending,
    
    // Error states
    createError: createPortfolio.error,
    analyzeError: analyzePortfolio.error,
    deleteError: deletePortfolio.error,
  }
}