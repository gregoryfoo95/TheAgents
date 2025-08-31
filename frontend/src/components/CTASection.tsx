import React, { memo } from 'react'
import { Box, Container, Typography, Button } from '@mui/material'
import { Link } from 'react-router-dom'
import { SECTION_GRADIENTS, HERO_GRADIENTS } from '../constants/homepage'

export const CTASection: React.FC = memo(() => {
  return (
    <Box sx={{ 
      py: { xs: 8, md: 12 },
      background: SECTION_GRADIENTS.CTA,
      color: 'white',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'radial-gradient(circle at 70% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
        pointerEvents: 'none',
      },
    }}>
      <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1 }}>
        <Box sx={{ textAlign: 'center' }}>
          <Typography 
            variant="h3" 
            component="h2" 
            fontWeight="800" 
            gutterBottom
            className="slide-up"
            sx={{
              fontSize: { xs: '2rem', md: '3rem' },
              mb: 3,
              background: HERO_GRADIENTS.TEXT_PRIMARY,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.02em',
            }}
          >
            Ready to revolutionize your property experience?
          </Typography>
          <Typography 
            variant="h6" 
            paragraph
            className="slide-up"
            sx={{
              opacity: 0.95,
              lineHeight: 1.6,
              fontSize: '1.2rem',
              mb: 4,
              maxWidth: 600,
              mx: 'auto',
            }}
          >
            Join thousands of users who have already discovered a better way to buy and sell properties. 
            Experience the future today.
          </Typography>
          <Box className="slide-up">
            <Button
              component={Link}
              to="/login"
              variant="contained"
              size="large"
              sx={{ 
                background: HERO_GRADIENTS.BUTTON_PRIMARY,
                color: '#4f46e5',
                mt: 2, 
                px: 6, 
                py: 2,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: '16px',
                textTransform: 'none',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-3px)',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                  background: HERO_GRADIENTS.BUTTON_HOVER,
                },
              }}
            >
              Start Your Journey
            </Button>
          </Box>
        </Box>
      </Container>
    </Box>
  )
})