import React, { memo } from 'react'
import { Card, CardContent, Box, Typography, useTheme } from '@mui/material'
import { SvgIconComponent } from '@mui/icons-material'
import { SECTION_GRADIENTS } from '../constants/homepage'

interface FeatureCardProps {
  icon: SvgIconComponent
  title: string
  description: string
  index: number
}

export const FeatureCard: React.FC<FeatureCardProps> = memo(({ 
  icon: IconComponent, 
  title, 
  description, 
  index 
}) => {
  return (
    <Card
      className="modern-card slide-up"
      sx={{
        height: '100%',
        textAlign: 'center',
        background: (theme) => theme.palette.mode === 'light' 
          ? SECTION_GRADIENTS.CARD 
          : `linear-gradient(145deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`,
        border: (theme) => `1px solid ${theme.palette.mode === 'light' ? 'rgba(20, 184, 166, 0.1)' : 'rgba(20, 184, 166, 0.2)'}`,
        borderRadius: '20px',
        overflow: 'hidden',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: (theme) => theme.palette.mode === 'light' 
            ? `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`
            : `linear-gradient(90deg, ${theme.palette.primary.light}, ${theme.palette.secondary.light})`,
        },
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-12px) scale(1.02)',
          boxShadow: (theme) => theme.palette.mode === 'light'
            ? '0 25px 50px rgba(20, 184, 166, 0.15)'
            : '0 25px 50px rgba(20, 184, 166, 0.3)',
          border: (theme) => `1px solid ${theme.palette.mode === 'light' ? 'rgba(20, 184, 166, 0.2)' : 'rgba(20, 184, 166, 0.4)'}`,
        },
      }}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <CardContent sx={{ p: 5 }}>
        <Box 
          sx={{ 
            background: SECTION_GRADIENTS.ICON,
            borderRadius: '16px',
            width: 80,
            height: 80,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mx: 'auto',
            mb: 3,
            color: (theme) => theme.palette.mode === 'light' ? 'white' : 'white',
            boxShadow: (theme) => theme.palette.mode === 'light'
              ? '0 8px 24px rgba(20, 184, 166, 0.3)'
              : '0 8px 24px rgba(20, 184, 166, 0.5)',
          }}
        >
          <IconComponent sx={{ fontSize: 40 }} />
        </Box>
        <Typography 
          variant="h5" 
          component="h3" 
          fontWeight="700" 
          gutterBottom
          sx={{ 
            color: (theme) => theme.palette.mode === 'light' ? '#1e293b' : theme.palette.text.primary,
            mb: 2,
            fontSize: '1.3rem',
          }}
        >
          {title}
        </Typography>
        <Typography 
          variant="body1" 
          color="text.secondary"
          sx={{ 
            lineHeight: 1.7,
            fontSize: '1rem',
          }}
        >
          {description}
        </Typography>
      </CardContent>
    </Card>
  )
})