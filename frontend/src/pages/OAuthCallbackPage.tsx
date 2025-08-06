import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Box, CircularProgress, Typography, Alert, Container } from '@mui/material'
import { useAuth } from '../contexts/AuthContext'
import type { OAuthTokens } from '../types'

export const OAuthCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const { handleOAuthCallback } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    const processCallback = async () => {
      try {
        // Check for OAuth error
        const error = searchParams.get('error')
        if (error) {
          setError(`Authentication failed: ${error}`)
          setIsProcessing(false)
          return
        }

        // Check if authentication was successful
        const authStatus = searchParams.get('auth')
        if (authStatus !== 'success') {
          setError('Authentication was not completed successfully')
          setIsProcessing(false)
          return
        }

        // Extract only oauth_id and profile_picture_url for session storage
        const oauth_id = searchParams.get('oauth_id')
        const profile_picture_url = searchParams.get('profile_picture_url')

        // Store only oauth_id and profile_picture_url in session storage
        if (oauth_id) {
          sessionStorage.setItem('oauth_id', oauth_id)
        }
        if (profile_picture_url) {
          sessionStorage.setItem('profile_picture_url', profile_picture_url)
        }
        sessionStorage.setItem('isAuthenticated', 'true')

        // Tokens are now in HTTP-only cookies, set by the backend
        // Also invalidate queries to fetch user data from API
        await handleOAuthCallback()

        // Check if user needs role selection
        const needsRoleSelection = searchParams.get('needs_role_selection') === 'true'
        
        let redirectTo: string
        if (needsRoleSelection) {
          // New user needs to select role
          redirectTo = '/select-role'
        } else {
          // Existing user with role, redirect to intended destination
          redirectTo = localStorage.getItem('oauth_redirect_after_login') || '/dashboard'
          localStorage.removeItem('oauth_redirect_after_login')
        }
        
        navigate(redirectTo, { replace: true })
      } catch (error: any) {
        setError(error.message || 'Failed to process OAuth callback')
        setIsProcessing(false)
      }
    }

    processCallback()
  }, [searchParams, handleOAuthCallback, navigate])

  if (error) {
    return (
      <Container maxWidth="sm">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Typography variant="body2" color="text.secondary" align="center">
            Please try logging in again.
          </Typography>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <CircularProgress size={60} sx={{ mb: 3 }} />
        <Typography variant="h6" align="center" gutterBottom>
          {isProcessing ? 'Completing sign in...' : 'Redirecting...'}
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center">
          Please wait while we set up your account.
        </Typography>
      </Box>
    </Container>
  )
}