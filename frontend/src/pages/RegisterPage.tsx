import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  Button,
  Typography,
  Container,
} from '@mui/material'
import {
  PersonAdd as PersonAddIcon,
  Google as GoogleIcon,
} from '@mui/icons-material'

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()

  // Redirect to login since we only support OAuth
  useEffect(() => {
    navigate('/login', { replace: true })
  }, [navigate])

  return null // Will redirect to login
}