import React, { memo } from 'react'
import { Box, Container, Typography, Button, Stack } from '@mui/material'
import { Link } from 'react-router-dom'
import { Search as SearchIcon, ArrowForward as ArrowRightIcon } from '@mui/icons-material'
import { AnimatedMascot } from './AnimatedMascot'
import { HERO_GRADIENTS } from '../constants/homepage'

export const HeroSection: React.FC = memo(() => {
  return (
    <Box
      sx={{
        background: HERO_GRADIENTS.PRIMARY,
        color: 'white',
        py: { xs: 8, md: 12, lg: 16 },
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
          pointerEvents: 'none',
        },
      }}
      className="fade-in"
    >
      <AnimatedMascot />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        <Typography
          variant="h1"
          component="h1"
          fontWeight="800"
          gutterBottom
          className="slide-up"
          sx={{ 
            fontSize: { xs: '2.5rem', md: '4rem', lg: '5rem' },
            background: HERO_GRADIENTS.TEXT_PRIMARY,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2,
            letterSpacing: '-0.02em',
          }}
        >
          Your Home, Your Asset
        </Typography>
        <Typography
          variant="h3"
          sx={{
            background: HERO_GRADIENTS.TEXT_SECONDARY,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 4,
            fontSize: { xs: '1.75rem', md: '2.5rem' },
            fontWeight: 600,
          }}
          className="slide-up"
        >
          Without Agents, by Agent$
        </Typography>
        <Typography
          variant="h6"
          sx={{
            maxWidth: 700,
            mx: 'auto',
            mb: 6,
            opacity: 0.95,
            lineHeight: 1.7,
            fontSize: { xs: '1.1rem', md: '1.25rem' },
            color: 'rgba(255, 255, 255, 0.9)',
          }}
          className="slide-up"
        >
          Experience the future of real estate. Connect directly with buyers and sellers, 
          leverage AI-powered valuations, and get expert legal support—all in one seamless platform.
        </Typography>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={3}
          justifyContent="center"
          sx={{ mt: 6 }}
          className="slide-up"
        >
          <Button
            component={Link}
            to="/properties"
            variant="contained"
            size="large"
            endIcon={<SearchIcon />}
            sx={{
              background: HERO_GRADIENTS.BUTTON_PRIMARY,
              color: '#4f46e5',
              px: 6,
              py: 2,
              fontSize: '1.1rem',
              fontWeight: 600,
              borderRadius: '16px',
              textTransform: 'none',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 20px 35px rgba(0, 0, 0, 0.2)',
                background: HERO_GRADIENTS.BUTTON_HOVER,
              },
            }}
          >
            Browse Properties
          </Button>
          <Button
            component={Link}
            to="/login"
            variant="outlined"
            size="large"
            endIcon={<ArrowRightIcon />}
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.5)',
              color: 'white',
              px: 6,
              py: 2,
              fontSize: '1.1rem',
              fontWeight: 600,
              borderRadius: '16px',
              textTransform: 'none',
              borderWidth: '2px',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                borderColor: 'white',
                background: 'rgba(255, 255, 255, 0.15)',
                transform: 'translateY(-2px)',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
              },
            }}
          >
            Get Started
          </Button>
        </Stack>
      </Container>
    </Box>
  )
})