import axios from 'axios'
import type {
  User,
  Property,
  PropertyListResponse,
  PropertyFilters,
  CreatePropertyData,
  UpdatePropertyData,
  Conversation,
  Message,
  Booking,
  CreateBookingData,
  LawyerProfile,
  AIValuation,
  AIRecommendation,
  LoginData,
  RegisterData,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Authentication
export const authAPI = {
  login: async (data: LoginData): Promise<{ access_token: string; token_type: string }> => {
    const response = await api.post('/api/users/login', data)
    return response.data
  },

  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post('/api/users/register', data)
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/api/users/me')
    return response.data
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.put('/api/users/me', data)
    return response.data
  },
}

// Properties
export const propertiesAPI = {
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

    const response = await api.get(`/api/properties/?${params.toString()}`)
    return response.data
  },

  getProperty: async (id: number): Promise<Property> => {
    const response = await api.get(`/api/properties/${id}`)
    return response.data
  },

  createProperty: async (data: CreatePropertyData): Promise<Property> => {
    const response = await api.post('/api/properties/', data)
    return response.data
  },

  updateProperty: async (id: number, data: UpdatePropertyData): Promise<Property> => {
    const response = await api.put(`/api/properties/${id}`, data)
    return response.data
  },

  deleteProperty: async (id: number): Promise<void> => {
    await api.delete(`/api/properties/${id}`)
  },

  uploadImages: async (propertyId: number, files: File[]): Promise<{ uploaded_images: string[] }> => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    
    const response = await api.post(`/api/properties/${propertyId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getMyProperties: async (): Promise<Property[]> => {
    const response = await api.get('/api/properties/my/listings')
    return response.data
  },
}

// Chat
export const chatAPI = {
  getConversations: async (): Promise<Conversation[]> => {
    const response = await api.get('/api/chat/conversations/')
    return response.data
  },

  getConversation: async (id: number): Promise<Conversation> => {
    const response = await api.get(`/api/chat/conversations/${id}`)
    return response.data
  },

  createConversation: async (data: {
    property_id: number
    buyer_id: number
    seller_id: number
    lawyer_id?: number
  }): Promise<Conversation> => {
    const response = await api.post('/api/chat/conversations/', data)
    return response.data
  },

  sendMessage: async (data: {
    conversation_id: number
    message_text?: string
    message_type?: 'text' | 'document' | 'image'
    file_name?: string
    file_type?: string
  }): Promise<Message> => {
    const response = await api.post('/api/chat/messages/', data)
    return response.data
  },

  uploadMessageFile: async (messageId: number, file: File): Promise<{ file_url: string; file_name: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post(`/api/chat/messages/${messageId}/file`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  addLawyerToConversation: async (conversationId: number, lawyerId: number): Promise<{ message: string }> => {
    const response = await api.put(`/api/chat/conversations/${conversationId}/add-lawyer`, { lawyer_id: lawyerId })
    return response.data
  },
}

// Bookings
export const bookingsAPI = {
  getMyBookings: async (status?: string): Promise<Booking[]> => {
    const params = status ? `?status_filter=${status}` : ''
    const response = await api.get(`/api/bookings/${params}`)
    return response.data
  },

  getBooking: async (id: number): Promise<Booking> => {
    const response = await api.get(`/api/bookings/${id}`)
    return response.data
  },

  createBooking: async (data: CreateBookingData): Promise<Booking> => {
    const response = await api.post('/api/bookings/', data)
    return response.data
  },

  updateBooking: async (id: number, data: Partial<CreateBookingData> & { status?: string }): Promise<Booking> => {
    const response = await api.put(`/api/bookings/${id}`, data)
    return response.data
  },

  cancelBooking: async (id: number): Promise<void> => {
    await api.delete(`/api/bookings/${id}`)
  },

  getAvailableSlots: async (propertyId: number, date: string): Promise<{
    date: string
    available_slots: { time: string; available: boolean }[]
  }> => {
    const response = await api.get(`/api/bookings/property/${propertyId}/available-slots?date=${date}`)
    return response.data
  },
}

// Lawyers
export const lawyersAPI = {
  getLawyers: async (filters: {
    specialization?: string
    min_experience?: number
    max_rate?: number
    verified_only?: boolean
  } = {}): Promise<LawyerProfile[]> => {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString())
      }
    })

    const response = await api.get(`/api/lawyers/?${params.toString()}`)
    return response.data
  },

  getLawyer: async (id: number): Promise<LawyerProfile> => {
    const response = await api.get(`/api/lawyers/${id}`)
    return response.data
  },

  createProfile: async (data: Omit<LawyerProfile, 'id' | 'user_id' | 'is_verified' | 'created_at' | 'user'>): Promise<LawyerProfile> => {
    const response = await api.post('/api/lawyers/profile', data)
    return response.data
  },

  updateProfile: async (data: Partial<LawyerProfile>): Promise<LawyerProfile> => {
    const response = await api.put('/api/lawyers/profile/me', data)
    return response.data
  },

  getMyProfile: async (): Promise<LawyerProfile> => {
    const response = await api.get('/api/lawyers/profile/me')
    return response.data
  },

  getSpecializations: async (): Promise<{ specializations: string[] }> => {
    const response = await api.get('/api/lawyers/specializations/list')
    return response.data
  },
}

// AI Services
export const aiAPI = {
  valuateProperty: async (propertyId: number): Promise<AIValuation> => {
    const response = await api.post(`/api/ai/valuate/${propertyId}`)
    return response.data
  },

  getPropertyValuations: async (propertyId: number): Promise<AIValuation[]> => {
    const response = await api.get(`/api/ai/valuations/${propertyId}`)
    return response.data
  },

  getImprovementRecommendations: async (propertyId: number): Promise<AIRecommendation[]> => {
    const response = await api.post(`/api/ai/recommendations/${propertyId}`)
    return response.data
  },

  getSavedRecommendations: async (propertyId: number): Promise<AIRecommendation[]> => {
    const response = await api.get(`/api/ai/recommendations/${propertyId}`)
    return response.data
  },

  analyzeImage: async (propertyId: number, file: File): Promise<{
    image_analysis: {
      room_type: string
      condition: string
      style: string
      identified_issues: string[]
    }
    recommendations: {
      type: string
      description: string
      estimated_cost: number
      priority: string
    }[]
  }> => {
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await api.post(`/api/ai/analyze-image/${propertyId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getMarketTrends: async (zipCode: string): Promise<{
    zip_code: string
    median_price: number
    price_change_6_months: string
    price_change_1_year: string
    days_on_market: number
    inventory_level: string
    market_temperature: string
    price_per_sqft: number
    forecasted_appreciation: string
  }> => {
    const response = await api.get(`/api/ai/market-trends/${zipCode}`)
    return response.data
  },
}

export default api 