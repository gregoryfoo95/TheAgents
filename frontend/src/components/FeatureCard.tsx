import React, { memo } from 'react'
import { Card, CardContent, Box, Typography } from '@mui/material'
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
        background: SECTION_GRADIENTS.CARD,
        border: '1px solid rgba(99, 102, 241, 0.1)',
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
          background: 'linear-gradient(90deg, #667eea, #764ba2)',
        },
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-12px) scale(1.02)',
          boxShadow: '0 25px 50px rgba(99, 102, 241, 0.15)',
          border: '1px solid rgba(99, 102, 241, 0.2)',
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
            color: 'white',
            boxShadow: '0 8px 24px rgba(99, 102, 241, 0.3)',
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
            color: '#1e293b',
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