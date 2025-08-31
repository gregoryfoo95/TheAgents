import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'react-hot-toast'
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'
import { createAppTheme } from './theme/index'
import { ThemeProvider } from './contexts/ThemeContext'
import { useThemeContext } from './contexts/ThemeContext'
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

const AppWithTheme: React.FC = () => {
  const { mode } = useThemeContext()
  const theme = createAppTheme(mode)

  return (
    <MuiThemeProvider theme={theme}>
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
    </MuiThemeProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <AppWithTheme />
    </ThemeProvider>
  </React.StrictMode>,
) 