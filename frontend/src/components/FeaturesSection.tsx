import React, { memo } from 'react'
import { Box, Container, Typography, Grid } from '@mui/material'
import { FeatureCard } from './FeatureCard'
import { FEATURES_DATA, SECTION_GRADIENTS } from '../constants/homepage'

export const FeaturesSection: React.FC = memo(() => {
  return (
    <Box sx={{ 
      py: { xs: 8, md: 12 },
      background: SECTION_GRADIENTS.FEATURES,
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
              background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
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