import React from 'react'
import { Box, Typography, Button, Container } from '@mui/material'
import { Link } from 'react-router-dom'
import { Home as HomeIcon } from '@mui/icons-material'
import { BRAND_GRADIENTS } from '../constants/colors'

export const NotFoundPage: React.FC = () => {
  return (
    <Container maxWidth="md">
      <Box 
        sx={{
          minHeight: '60vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          py: 8
        }}
      >
        <Typography
          variant="h1"
          sx={{
            fontSize: { xs: '6rem', md: '8rem' },
            fontWeight: 800,
            background: BRAND_GRADIENTS.PRIMARY,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2
          }}
        >
          404
        </Typography>
        
        <Typography
          variant="h4"
          sx={{
            color: (theme) => theme.palette.text.primary,
            mb: 2,
            fontWeight: 600
          }}
        >
          Page Not Found
        </Typography>
        
        <Typography
          variant="body1"
          sx={{
            color: (theme) => theme.palette.text.secondary,
            mb: 4,
            maxWidth: 500,
            fontSize: '1.1rem'
          }}
        >
          The page you're looking for doesn't exist. It might have been moved, deleted, or you entered the wrong URL.
        </Typography>
        
        <Button
          component={Link}
          to="/"
          variant="contained"
          size="large"
          startIcon={<HomeIcon />}
          sx={{
            px: 4,
            py: 1.5,
            borderRadius: 2,
            textTransform: 'none',
            fontSize: '1.1rem',
            background: (theme) => theme.palette.mode === 'light'
              ? BRAND_GRADIENTS.PRIMARY
              : BRAND_GRADIENTS.SECONDARY,
            '&:hover': {
              background: (theme) => theme.palette.mode === 'light'
                ? BRAND_GRADIENTS.SECONDARY
                : BRAND_GRADIENTS.PRIMARY,
              transform: 'translateY(-2px)'
            }
          }}
        >
          Go Home
        </Button>
      </Box>
    </Container>
  )
}