import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'react-hot-toast'
import { ThemeProvider } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'
import theme from './theme/index'
import App from './App.tsx'
import { queryClient } from './utils/queryClient'
import './index.css'

const TOAST_POSITION = "top-right"
const TOAST_DURATION = 4000

const DEFAULT_TOAST_STYLE = {
  background: '#363636',
  color: '#fff',
}

const SUCCESS_TOAST_STYLE = {
  background: '#059669',
}

const ERROR_TOAST_STYLE = {
  background: '#DC2626',
}

const toastOptions = {
  duration: TOAST_DURATION,
  style: DEFAULT_TOAST_STYLE,
  success: {
    style: SUCCESS_TOAST_STYLE,
  },
  error: {
    style: ERROR_TOAST_STYLE,
  },
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
          <Toaster
            position={TOAST_POSITION}
            toastOptions={toastOptions}
          />
        </BrowserRouter>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ThemeProvider>
  </React.StrictMode>,
) 