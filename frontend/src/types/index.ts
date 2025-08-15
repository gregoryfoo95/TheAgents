export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  display_name?: string
  profile_picture_url?: string
  user_type?: 'consumer' | 'agent' | 'lawyer'
  is_active: boolean
  is_verified: boolean
  email_verified: boolean
  created_at: string
  updated_at?: string
  last_login?: string
}

export interface Property {
  id: number
  seller_id: number
  title: string
  description?: string
  property_type: string
  price: number
  ai_estimated_price?: number
  bedrooms?: number
  bathrooms?: number
  square_feet?: number
  address: string
  city: string
  state: string
  zip_code: string
  latitude?: number
  longitude?: number
  status: 'active' | 'pending' | 'sold' | 'withdrawn'
  images?: string[]
  created_at: string
  updated_at: string
  features: PropertyFeature[]
  seller: User
}

export interface PropertyFeature {
  id: number
  feature_name: string
  feature_value?: string
}

export interface PropertyListResponse {
  items: Property[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface PropertyFilters {
  min_price?: number
  max_price?: number
  bedrooms?: number
  bathrooms?: number
  property_type?: string
  city?: string
  state?: string
  status?: 'active' | 'pending' | 'sold' | 'withdrawn'
}

export interface Conversation {
  id: number
  property_id: number
  buyer_id: number
  seller_id: number
  lawyer_id?: number
  status: 'active' | 'closed'
  created_at: string
  updated_at: string
  property: Property
  buyer: User
  seller: User
  lawyer?: User
  messages: Message[]
}

export interface Message {
  id: number
  conversation_id: number
  sender_id: number
  message_text?: string
  message_type: 'text' | 'document' | 'image'
  file_url?: string
  file_name?: string
  file_type?: string
  created_at: string
  sender: User
}

export interface Booking {
  id: number
  property_id: number
  buyer_id: number
  seller_id: number
  scheduled_date: string
  scheduled_time: string
  duration_minutes: number
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled'
  notes?: string
  created_at: string
  updated_at: string
  property: Property
  buyer: User
  seller: User
}

export interface LawyerProfile {
  id: number
  user_id: number
  firm_name: string
  license_number: string
  specializations?: string[]
  years_experience?: number
  hourly_rate?: number
  bio?: string
  is_verified: boolean
  created_at: string
  user: User
}

export interface AIValuation {
  id: number
  property_id: number
  estimated_price: number
  confidence_score?: number
  valuation_factors?: Record<string, any>
  market_data?: Record<string, any>
  created_at: string
}

export interface AIRecommendation {
  id: number
  property_id: number
  recommendation_type: string
  recommendation_text: string
  estimated_cost?: number
  estimated_value_increase?: number
  priority: 'low' | 'medium' | 'high'
  created_at: string
}

export interface OAuthTokens {
  access_token: string
  refresh_token?: string
  token_type: string
  expires_in: number
  refresh_expires_in?: number
}

export interface AuthContextType {
  user: User | null
  loginWithGoogle: () => void
  logout: () => void
  handleOAuthCallback: () => Promise<void>
  isLoading: boolean
  isAuthenticated: boolean
}

export interface UserTypeSelectionData {
  user_type: 'consumer' | 'agent' | 'lawyer'
  phone?: string
}

export interface OAuthCallbackParams {
  access_token: string
  refresh_token?: string
  token_type: string
  error?: string
}

export interface CreatePropertyData {
  title: string
  description?: string
  property_type: string
  price: number
  bedrooms?: number
  bathrooms?: number
  square_feet?: number
  address: string
  city: string
  state: string
  zip_code: string
  latitude?: number
  longitude?: number
}

export interface UpdatePropertyData {
  title?: string
  description?: string
  property_type?: string
  price?: number
  bedrooms?: number
  bathrooms?: number
  square_feet?: number
  address?: string
  city?: string
  state?: string
  zip_code?: string
  latitude?: number
  longitude?: number
  status?: 'active' | 'pending' | 'sold' | 'withdrawn'
}

export interface CreateBookingData {
  property_id: number
  scheduled_date: string
  scheduled_time: string
  duration_minutes?: number
  notes?: string
}

export interface ApiError {
  detail: string
  status?: number
} 