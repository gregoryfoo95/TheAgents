import React, { memo } from 'react'
import { Box, Container, Typography, Grid } from '@mui/material'
import { FeatureCard } from './FeatureCard'
import { FEATURES_DATA, SECTION_GRADIENTS } from '../constants/homepage'

export const FeaturesSection: React.FC = memo(() => {
  return (
    <Box sx={{ 
      py: { xs: 8, md: 12 },
      background: (theme) => theme.palette.mode === 'light' 
        ? SECTION_GRADIENTS.FEATURES 
        : `linear-gradient(180deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
      position: 'relative',
    }}>
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography
            variant="h3"
            component="h2"
            fontWeight="800"
            gutterBottom
            className="slide-up"
            sx={{ 
              mb: 3,
              background: (theme) => theme.palette.mode === 'light'
                ? `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`
                : `linear-gradient(45deg, ${theme.palette.primary.light} 30%, ${theme.palette.secondary.light} 90%)`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontSize: { xs: '2rem', md: '3rem' },
            }}
          >
            Why Choose Agent$?
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ 
              maxWidth: 600,
              mx: 'auto',
              fontSize: '1.2rem',
              lineHeight: 1.6,
            }}
            className="slide-up"
          >
            Revolutionary features that transform how you buy and sell properties
          </Typography>
        </Box>
        <Grid container spacing={4}>
          {FEATURES_DATA.map((feature, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <FeatureCard
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                index={index}
              />
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  )
})