import React from 'react'
import { Box } from '@mui/material'
import { HeroSection } from '../components/HeroSection'
import { FeaturesSection } from '../components/FeaturesSection'
import { CTASection } from '../components/CTASection'

export const HomePage: React.FC = () => {

  return (
    <Box>
      <HeroSection />
      <FeaturesSection />
      <CTASection />
    </Box>
  )
}