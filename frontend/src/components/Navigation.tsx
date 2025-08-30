import React, { memo } from 'react'
import { Box, Button } from '@mui/material'
import { Link } from 'react-router-dom'
import { SvgIconComponent } from '@mui/icons-material'

export interface NavigationItem {
  name: string
  href: string
  icon: SvgIconComponent
}

interface NavigationProps {
  items: NavigationItem[]
  isActive: (href: string) => boolean
  isMobile?: boolean
}

export const Navigation: React.FC<NavigationProps> = memo(({ 
  items, 
  isActive, 
  isMobile = false 
}) => {
  if (isMobile) return null

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
      {items.map((item) => (
        <Button
          key={item.name}
          component={Link}
          to={item.href}
          startIcon={<item.icon />}
          color={isActive(item.href) ? 'primary' : 'inherit'}
          sx={{ mr: 2 }}
        >
          {item.name}
        </Button>
      ))}
    </Box>
  )
})