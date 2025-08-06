import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  Button,
  Typography,
  Container,
  Alert,
  CircularProgress,
  TextField,
  Grid,
  Paper,
} from '@mui/material'
import {
  Business as BusinessIcon,
  Person as PersonIcon,
  Gavel as GavelIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import { useUpdateUserType } from '../hooks/useAuth'
import type { UserTypeSelectionData } from '../types'

const userTypeOptions = [
  {
    value: 'consumer' as const,
    label: 'Consumer',
    description: 'Looking to buy or rent properties',
    icon: PersonIcon,
    color: '#2196f3',
  },
  {
    value: 'agent' as const,
    label: 'Agent',
    description: 'Real estate professional listing and selling properties',
    icon: BusinessIcon,
    color: '#4caf50',
  },
  {
    value: 'lawyer' as const,
    label: 'Lawyer',
    description: 'Legal professional providing real estate law services',
    icon: GavelIcon,
    color: '#ff9800',
  },
]

export const UserTypeSelectionPage: React.FC = () => {
  const [selectedType, setSelectedType] = useState<'consumer' | 'agent' | 'lawyer' | null>(null)
  const [phone, setPhone] = useState('')
  const [error, setError] = useState('')
  const { user } = useAuth()
  const updateUserTypeMutation = useUpdateUserType()
  const navigate = useNavigate()

  // Redirect if user already has a type set
  React.useEffect(() => {
    if (user && user.user_type) {
      navigate('/dashboard', { replace: true })
    }
  }, [user, navigate])

  const handleSubmit = async () => {
    if (!selectedType) {
      setError('Please select your account type')
      return
    }

    try {
      setError('')
      const userData: UserTypeSelectionData = {
        user_type: selectedType,
        phone: phone.trim() || undefined,
      }

      await updateUserTypeMutation.mutateAsync(userData)
      navigate('/dashboard', { replace: true })
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to set user type')
    }
  }

  const isLoading = updateUserTypeMutation.isPending

  return (
    <Container component="main" maxWidth="md">
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
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
                Complete Your Profile
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Help us personalize your experience by selecting your role
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Grid container spacing={3} sx={{ mb: 4 }}>
              {userTypeOptions.map((option) => {
                const IconComponent = option.icon
                const isSelected = selectedType === option.value

                return (
                  <Grid item xs={12} sm={4} key={option.value}>
                    <Paper
                      elevation={isSelected ? 4 : 1}
                      sx={{
                        p: 3,
                        textAlign: 'center',
                        cursor: 'pointer',
                        border: isSelected ? `2px solid ${option.color}` : '2px solid transparent',
                        '&:hover': {
                          elevation: 3,
                          borderColor: option.color,
                        },
                        transition: 'all 0.2s ease-in-out',
                      }}
                      onClick={() => setSelectedType(option.value)}
                    >
                      <IconComponent
                        sx={{
                          fontSize: 48,
                          color: isSelected ? option.color : 'text.secondary',
                          mb: 2,
                        }}
                      />
                      <Typography
                        variant="h6"
                        gutterBottom
                        color={isSelected ? option.color : 'text.primary'}
                        fontWeight="medium"
                      >
                        {option.label}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {option.description}
                      </Typography>
                    </Paper>
                  </Grid>
                )
              })}
            </Grid>

            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                label="Phone Number (Optional)"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 123-4567"
                disabled={isLoading}
                helperText="We'll use this to contact you about property viewings"
                sx={{ mb: 2 }}
              />
            </Box>

            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleSubmit}
              disabled={isLoading || !selectedType}
              sx={{ py: 1.5 }}
              startIcon={isLoading ? <CircularProgress size={20} /> : undefined}
            >
              {isLoading ? 'Setting up your account...' : 'Continue'}
            </Button>

            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                You can update your information later in your profile settings
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}