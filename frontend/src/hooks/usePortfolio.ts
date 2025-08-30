import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
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
  user_id?: number
  name: string
  description?: string
  is_active?: boolean
  stocks?: PortfolioStock[]
  created_at: string
  updated_at: string
  stats?: any
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
    mutationFn: async (data: PortfolioAnalysisRequest): Promise<any> => {
      // Get portfolio data first
      const portfolio = await stockService.getPortfolio(data.portfolio_id)
      
      // Transform to the format expected by analyzePortfolioStream  
      const portfolioData = portfolio.stocks.map((stock: any) => ({
        symbol: stock.symbol,
        allocation_percentage: stock.allocation_percentage
      }))
      
      // Start streaming analysis and return session info
      return new Promise((resolve, reject) => {
        let sessionId: string | null = null
        
        stockService.analyzePortfolioStream(
          portfolioData,
          data.time_frequency,
          (eventData) => {
            // Capture session_id from the first event
            if (!sessionId && eventData.session_id) {
              sessionId = eventData.session_id
              resolve({ session_id: sessionId })
            }
            // Handle other events as needed
          }
        ).catch(reject)
      })
    },
    onSuccess: (data) => {
      console.log('🚀 Portfolio analysis initiated:', data)
      console.log('✅ Portfolio analysis initiated:', data.session_id)
      setPollingSessionId(data.session_id || data.workflow_id)
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
      // Stop polling if analysis is completed or failed
      if (data?.state?.data?.status === 'completed' || data?.state?.data?.status === 'failed') {
        return false
      }
      return 3000 // Continue polling every 3 seconds
    },
    refetchOnWindowFocus: false
  })

  // Monitor analysis status and stop polling when completed
  useEffect(() => {
    if (analysisStatus.data?.status === 'completed' || analysisStatus.data?.status === 'failed') {
      setPollingSessionId(null)
    }
  }, [analysisStatus.data?.status])

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