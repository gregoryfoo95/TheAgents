/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_NODE_ENV: string
  readonly VITE_ENABLE_AI_FEATURES: string
  readonly VITE_ENABLE_CHAT: string
  readonly VITE_ENABLE_LAWYER_INTEGRATION: string
  readonly VITE_ENABLE_ANALYTICS: string
  readonly VITE_GOOGLE_MAPS_API_KEY?: string
  readonly VITE_STRIPE_PUBLIC_KEY?: string
  readonly VITE_ANALYTICS_ID?: string
  readonly VITE_DEBUG_MODE: string
  readonly VITE_SHOW_DEBUG_INFO: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_MAX_UPLOAD_SIZE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}