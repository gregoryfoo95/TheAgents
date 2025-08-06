import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  Button,
  Typography,
  Container,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material'
import {
  Login as LoginIcon,
  Google as GoogleIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'

export const LoginPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const { loginWithGoogle } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const URI_FROM = '/dashboard'

  const handleGoogleLogin = () => {
    if (isLoading) return
    
    try {
      setIsLoading(true)
      setError('')
      // Store the intended destination
      localStorage.setItem('oauth_redirect_after_login', URI_FROM)
      loginWithGoogle()
    } catch (error: any) {
      setError('Failed to initialize Google login')
      setIsLoading(false)
    }
  }

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          py: 3,
        }}
      >
        <Card elevation={3}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <LoginIcon
                sx={{
                  fontSize: 48,
                  color: 'primary.main',
                  mb: 2,
                }}
              />
              <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
                Sign in to Property Marketplace
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Use your Google account to get started
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box sx={{ mt: 2 }}>
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={handleGoogleLogin}
                disabled={isLoading}
                startIcon={isLoading ? <CircularProgress size={20} /> : <GoogleIcon />}
                sx={{
                  py: 1.5,
                  borderColor: '#4285f4',
                  color: '#4285f4',
                  '&:hover': {
                    borderColor: '#3367d6',
                    backgroundColor: 'rgba(66, 133, 244, 0.04)',
                  },
                }}
              >
                {isLoading ? 'Connecting...' : 'Continue with Google'}
              </Button>
              
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  By signing in, you agree to our Terms of Service and Privacy Policy
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}