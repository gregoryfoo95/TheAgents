import React, { memo } from 'react'
import { IconButton, Tooltip } from '@mui/material'
import { Brightness4 as DarkModeIcon, Brightness7 as LightModeIcon } from '@mui/icons-material'
import { useThemeContext } from '../contexts/ThemeContext'

interface ThemeToggleProps {
  size?: 'small' | 'medium' | 'large'
  edge?: 'start' | 'end' | false
}

export const ThemeToggle: React.FC<ThemeToggleProps> = memo(({ 
  size = 'medium',
  edge = false 
}) => {
  const { mode, toggleTheme } = useThemeContext()
  
  const isDark = mode === 'dark'
  const tooltipTitle = isDark ? 'Switch to light mode' : 'Switch to dark mode'
  const ariaLabel = isDark ? 'switch to light mode' : 'switch to dark mode'

  return (
    <Tooltip title={tooltipTitle}>
      <IconButton
        onClick={toggleTheme}
        color="inherit"
        size={size}
        edge={edge}
        aria-label={ariaLabel}
        sx={{
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'rotate(20deg)',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
          },
        }}
      >
        {isDark ? (
          <LightModeIcon 
            sx={{ 
              fontSize: size === 'small' ? 20 : size === 'large' ? 32 : 24,
              transition: 'transform 0.2s ease-in-out',
            }} 
          />
        ) : (
          <DarkModeIcon 
            sx={{ 
              fontSize: size === 'small' ? 20 : size === 'large' ? 32 : 24,
              transition: 'transform 0.2s ease-in-out',
            }} 
          />
        )}
      </IconButton>
    </Tooltip>
  )
})