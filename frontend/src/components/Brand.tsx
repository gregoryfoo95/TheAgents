import React from 'react'
import { Typography, SxProps, Theme } from '@mui/material'
import { Link } from 'react-router-dom'

interface BrandProps {
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
  component?: React.ElementType
  sx?: SxProps<Theme>
  to?: string
}

const BRAND_GRADIENT = 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)'

const BRAND_STYLE: SxProps<Theme> = {
  fontWeight: '800',
  background: BRAND_GRADIENT,
  backgroundClip: 'text',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  textDecoration: 'none',
}

export const Brand: React.FC<BrandProps> = ({ 
  variant = 'h6', 
  component, 
  sx = {},
  to
}) => {
  const brandComponent = to ? Link : component
  const linkProps = to ? { to } : {}

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