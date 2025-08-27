import axios from 'axios'
import type {
  Booking,
  Conversation,
  CreateBookingData,
  CreatePropertyData,
  Message,
  Property,
  PropertyFilters,
  PropertyListResponse,
  UpdatePropertyData,
  User,
} from '../types'

const API_GATEWAY_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instances for different services
const api = axios.create({
  baseURL: API_GATEWAY_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auth service instance (via API Gateway)
const authAPI = axios.create({
  baseURL: API_GATEWAY_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Property service instance (via API Gateway)
const propertyAPI = axios.create({
  baseURL: API_GATEWAY_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Stock service instance (via API Gateway) 
const stockAPI = axios.create({
  baseURL: API_GATEWAY_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token management - now using HTTP-only cookies
let authToken: string | null = null

// Add credentials for HTTP-only cookies
const addCredentialsToRequest = (config: any) => {
  // Include credentials to send HTTP-only cookies
  config.withCredentials = true
  return config
}

// Add interceptors to all instances
[api, authAPI, propertyAPI, stockAPI].forEach(instance => {
  instance.interceptors.request.use(addCredentialsToRequest)
  
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Clear session and redirect to login
        sessionStorage.clear()
        authToken = null
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )
})

// Helper function to clear auth token and storage
export const clearAuthToken = () => {
  authToken = null
  
  // Clear session storage
  sessionStorage.clear()
  
  // Clear local storage
  localStorage.clear()
  
}

// Authentication API (OAuth-only)
export const authService = {

  getCurrentUser: async (): Promise<User> => {
    const response = await authAPI.get('/auth/me')
    return response.data
  },


  logout: async (): Promise<void> => {
    try {
      await authAPI.post('/auth/logout')
    } catch (error) {
      // Continue with logout even if API fails
      console.warn('Logout API call failed:', error)
    }
    clearAuthToken()
  },


  // OAuth methods
  getOAuthProviders: async (): Promise<{ providers: string[] }> => {
    const response = await authAPI.get('/auth/providers')
    return response.data
  },

  startGoogleOAuth: (redirectUri?: string): string => {
    const params = new URLSearchParams()
    if (redirectUri) {
      params.append('redirect_uri', redirectUri)
    }
    return `${API_GATEWAY_URL}/auth/google?${params.toString()}`
  },

  // Initiate OAuth login by redirecting to backend
  loginWithGoogle: (redirectUri?: string): void => {
    const url = authService.startGoogleOAuth(redirectUri)
    window.location.href = url
  },

  updateUserType: async (data: { user_type: string; phone?: string }): Promise<User> => {
    const response = await authAPI.put('/auth/user-type', data)
    return response.data
  },

  getUserRoles: async (): Promise<{
    roles: Array<{
      value: string
      label: string
      description: string
    }>
  }> => {
    const response = await authAPI.get('/auth/roles')
    return response.data
  },
}

// Properties API (via API Gateway)
export const propertiesService = {
  getProperties: async (
    page: number = 1,
    size: number = 20,
    filters: PropertyFilters = {}
  ): Promise<PropertyListResponse> => {
    const params = new URLSearchParams()
    params.append('page', page.toString())
    params.append('size', size.toString())
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })

    const response = await propertyAPI.get(`/properties/?${params.toString()}`)
    return response.data
  },

  getProperty: async (id: number): Promise<Property> => {
    const response = await propertyAPI.get(`/properties/${id}`)
    return response.data
  },

  createProperty: async (data: CreatePropertyData): Promise<Property> => {
    const response = await propertyAPI.post('/properties/', data)
    return response.data
  },

  updateProperty: async (id: number, data: UpdatePropertyData): Promise<Property> => {
    const response = await propertyAPI.put(`/properties/${id}`, data)
    return response.data
  },

  deleteProperty: async (id: number): Promise<void> => {
    await propertyAPI.delete(`/properties/${id}`)
  },

  uploadImages: async (propertyId: number, files: File[]): Promise<{ uploaded_images: string[] }> => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    
    const response = await propertyAPI.post(`/properties/${propertyId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getMyProperties: async (): Promise<Property[]> => {
    const response = await propertyAPI.get('/properties/my/listings')
    return response.data
  },
}

// Bookings API (via Property Service through API Gateway)
export const bookingsAPI = {
  getMyBookings: async (status?: string): Promise<Booking[]> => {
    const params = new URLSearchParams()
    if (status) params.append('status_filter', status)
    const response = await propertyAPI.get(`/properties/bookings/?${params.toString()}`)
    const items = response.data as any[]
    // Map service shape to frontend Booking type where possible
    return items.map((b: any) => ({
      id: b.id,
      property_id: b.property_id,
      buyer_id: b.tenant_id,
      seller_id: 0,
      scheduled_date: b.start_date,
      scheduled_time: new Date(b.start_date).toISOString().slice(11,16),
      duration_minutes: b.end_date ? Math.max(0, Math.floor((new Date(b.end_date).getTime() - new Date(b.start_date).getTime())/60000)) : 60,
      status: b.status,
      notes: b.notes,
      created_at: b.created_at,
      updated_at: b.updated_at,
      // Placeholders for nested objects not yet available in microservice
      property: {} as any,
      buyer: {} as any,
      seller: {} as any,
    })) as Booking[]
  },

  getBooking: async (id: number): Promise<Booking> => {
    const { data } = await propertyAPI.get(`/properties/bookings/${id}`)
    const b: any = data
    return {
      id: b.id,
      property_id: b.property_id,
      buyer_id: b.tenant_id,
      seller_id: 0,
      scheduled_date: b.start_date,
      scheduled_time: new Date(b.start_date).toISOString().slice(11,16),
      duration_minutes: b.end_date ? Math.max(0, Math.floor((new Date(b.end_date).getTime() - new Date(b.start_date).getTime())/60000)) : 60,
      status: b.status,
      notes: b.notes,
      created_at: b.created_at,
      updated_at: b.updated_at,
      property: {} as any,
      buyer: {} as any,
      seller: {} as any,
    } as Booking
  },

  getAvailableSlots: async (propertyId: number, date: string): Promise<string[]> => {
    const { data } = await propertyAPI.get(`/properties/bookings/available-slots`, {
      params: { property_id: propertyId, date },
    })
    return data
  },

  createBooking: async (data: CreateBookingData): Promise<Booking> => {
    // Translate CreateBookingData -> service payload
    const payload: any = {
      property_id: data.property_id,
      start_date: data.scheduled_date,
      end_date: data.scheduled_date,
      notes: data.notes,
    }
    const { data: created } = await propertyAPI.post(`/properties/bookings/`, payload)
    return bookingsAPI.getBooking(created.id)
  },

  updateBooking: async (
    id: number,
    data: Partial<CreateBookingData> & { status?: string }
  ): Promise<Booking> => {
    const payload: any = {}
    if (data.status) payload.status = data.status
    if (data.scheduled_date) {
      payload.start_date = data.scheduled_date
      payload.end_date = data.scheduled_date
    }
    if (data.notes !== undefined) payload.notes = data.notes
    await propertyAPI.put(`/properties/bookings/${id}`, payload)
    return bookingsAPI.getBooking(id)
  },

  cancelBooking: async (id: number): Promise<void> => {
    await propertyAPI.post(`/properties/bookings/${id}/cancel`)
  },
}

// Minimal AI API placeholder; replace when AI service is implemented
export const aiAPI = {
  getPropertyValuations: async (propertyId: number): Promise<any[]> => {
    throw new Error('AI service not implemented yet')
  },
  getSavedRecommendations: async (propertyId: number): Promise<any[]> => {
    throw new Error('AI service not implemented yet')
  },
  getMarketTrends: async (zipCode: string): Promise<any> => {
    throw new Error('AI service not implemented yet')
  },
  valuateProperty: async (propertyId: number): Promise<any> => {
    throw new Error('AI service not implemented yet')
  },
  getImprovementRecommendations: async (propertyId: number): Promise<any[]> => {
    throw new Error('AI service not implemented yet')
  },
  analyzeImage: async (propertyId: number, file: File): Promise<any> => {
    throw new Error('AI service not implemented yet')
  },
}

// Minimal Lawyers API placeholder; replace when lawyers service is implemented
export const lawyersAPI = {
  getLawyers: async (filters: any = {}): Promise<any[]> => {
    throw new Error('Lawyers service not implemented yet')
  },
  getLawyer: async (id: number): Promise<any> => {
    throw new Error('Lawyers service not implemented yet')
  },
  getMyProfile: async (): Promise<any> => {
    throw new Error('Lawyers service not implemented yet')
  },
  getSpecializations: async (): Promise<string[]> => {
    throw new Error('Lawyers service not implemented yet')
  },
  createProfile: async (data: any): Promise<any> => {
    throw new Error('Lawyers service not implemented yet')
  },
  updateProfile: async (id: number, data: any): Promise<any> => {
    throw new Error('Lawyers service not implemented yet')
  },
}

// Minimal Chat API placeholder; replace when chat service is implemented
export const chatAPI = {
  getConversations: async (): Promise<Conversation[]> => {
    return []
  },
  getConversation: async (_id: number): Promise<Conversation> => {
    throw new Error('Chat service not implemented yet')
  },
  createConversation: async (): Promise<Conversation> => {
    throw new Error('Chat service not implemented yet')
  },
  sendMessage: async (data: any): Promise<Message> => {
    throw new Error('Chat service not implemented yet')
  },
  uploadMessageFile: async (messageId: number, file: File): Promise<{ file_url: string; file_name: string }> => {
    throw new Error('Chat service not implemented yet')
  },
  addLawyerToConversation: async (conversationId: number, lawyerId: number): Promise<void> => {
    throw new Error('Chat service not implemented yet')
  },
}

// Stock & Portfolio API (via API Gateway)
export const stockService = {
  // Portfolio management
  getPortfolios: async (): Promise<any[]> => {
    // Get current user info to extract user_id
    const userResponse = await authAPI.get('/auth/me')
    const userId = userResponse.data.id
    
    const response = await stockAPI.get(`/stock/users/${userId}/portfolios`)
    return response.data
  },

  createPortfolio: async (data: {
    name: string
    description?: string
    stocks: { symbol: string; allocation_percentage: number }[]
  }): Promise<any> => {
    // Get current user info to extract user_id
    const userResponse = await authAPI.get('/auth/me')
    const userId = userResponse.data.id
    
    const response = await stockAPI.post(`/stock/portfolios?user_id=${userId}`, data)
    return response.data
  },

  getPortfolio: async (id: number): Promise<any> => {
    // Get current user info to extract user_id
    const userResponse = await authAPI.get('/auth/me')
    const userId = userResponse.data.id
    
    const response = await stockAPI.get(`/stock/portfolios/${id}?user_id=${userId}`)
    return response.data
  },

  updatePortfolio: async (id: number, data: any): Promise<any> => {
    // Get current user info to extract user_id
    const userResponse = await authAPI.get('/auth/me')
    const userId = userResponse.data.id
    
    const response = await stockAPI.put(`/stock/portfolios/${id}?user_id=${userId}`, data)
    return response.data
  },

  deletePortfolio: async (id: number): Promise<void> => {
    // Get current user info to extract user_id
    const userResponse = await authAPI.get('/auth/me')
    const userId = userResponse.data.id
    
    await stockAPI.delete(`/stock/portfolios/${id}?user_id=${userId}`)
  },

  // Portfolio analysis
  analyzePortfolio: async (portfolioId: number, timeFrequency: string = '1M'): Promise<any> => {
    // Get current user info to extract user_id
    const userResponse = await authAPI.get('/auth/me')
    const userId = userResponse.data.id
    
    // First get portfolio data
    const portfolio = await stockService.getPortfolio(portfolioId)
    
    const response = await stockAPI.post('/stock/analyze-portfolio', {
      user_id: userId,
      portfolio_data: portfolio.stocks.map((stock: any) => ({
        symbol: stock.symbol,
        allocation: stock.allocation_percentage
      })),
      time_frequency: timeFrequency,
      analysis_type: 'portfolio'
    })
    return response.data
  },

  // Single stock analysis
  analyzeStock: async (data: {
    symbol: string
    time_frequency?: string
    user_context?: string
  }): Promise<any> => {
    // Get current user info to extract user_id
    const userResponse = await authAPI.get('/auth/me')
    const userId = userResponse.data.id
    
    const response = await stockAPI.post('/stock/analyze', {
      ...data,
      user_id: userId
    })
    return response.data
  },

  // Analysis results
  getAnalysisSession: async (sessionId: string): Promise<any> => {
    const response = await stockAPI.get(`/stock/sessions/${sessionId}`)
    return response.data
  },

  getUserSessions: async (limit: number = 20, offset: number = 0): Promise<any[]> => {
    // Get current user info to extract user_id
    const userResponse = await authAPI.get('/auth/me')
    const userId = userResponse.data.id
    
    const response = await stockAPI.get(`/stock/users/${userId}/sessions?limit=${limit}&offset=${offset}`)
    return response.data
  },

  // Service health
  getHealth: async (): Promise<{ status: string; service: string; version: string }> => {
    const response = await stockAPI.get('/stock/health')
    return response.data
  },

  // Agent information
  getAgentsDescription: async (): Promise<any> => {
    const response = await stockAPI.get('/stock/agents/description')
    return response.data
  },

  // Get supported stock symbols (placeholder)
  getSupportedSymbols: async (): Promise<any> => {
    // Return common stock symbols for now
    return {
      symbols: [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 
        'JNJ', 'PG', 'KO', 'PFE', 'VZ', 'XOM', 'CVX', 'WMT', 'JPM', 'V', 'MA',
        'SPY', 'QQQ', 'VTI', 'IWM', 'SQ', 'PYPL', 'SHOP', 'CRWD', 'ZM', 'SNOW'
      ]
    }
  },

  // Get available time frequencies
  getTimeFrequencies: async (): Promise<any> => {
    return {
      frequencies: [
        { label: '1 Day', value: '1D' },
        { label: '1 Week', value: '1W' },
        { label: '1 Month', value: '1M' },
        { label: '3 Months', value: '3M' },
        { label: '6 Months', value: '6M' },
        { label: '1 Year', value: '1Y' },
      ]
    }
  },
}

export default api