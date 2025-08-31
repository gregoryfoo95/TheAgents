import React from 'react'
import { Typography, SxProps, Theme, Box } from '@mui/material'
import { Link } from 'react-router-dom'
import { BRAND_GRADIENTS } from '../constants/colors'
import { Logo } from './Logo'

interface BrandProps {
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
  component?: React.ElementType
  sx?: SxProps<Theme>
  to?: string
  showLogo?: boolean
  logoSize?: number
  animate?: boolean
}

const BRAND_STYLE: SxProps<Theme> = {
  fontWeight: '800',
  background: BRAND_GRADIENTS.PRIMARY,
  backgroundClip: 'text',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  textDecoration: 'none',
}

export const Brand: React.FC<BrandProps> = ({ 
  variant = 'h6', 
  component, 
  sx = {},
  to,
  showLogo = false,
  logoSize = 32,
  animate = true
}) => {
  const brandComponent = to ? Link : component
  const linkProps = to ? { to } : {}

  if (showLogo) {
    return (
      <Box
        component={brandComponent}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          textDecoration: 'none',
          ...sx
        }}
        {...linkProps}
      >
        <Logo width={logoSize} height={logoSize} animate={animate} />
        <Typography
          variant={variant}
          sx={BRAND_STYLE}
        >
          Agent$
        </Typography>
      </Box>
    )
  }

  return (
    <Typography
      variant={variant}
      component={brandComponent}
      sx={{
        ...BRAND_STYLE,
        ...sx
      }}
      {...linkProps}
    >
      Agent$
    </Typography>
  )
}