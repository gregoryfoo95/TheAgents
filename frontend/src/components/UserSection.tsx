import React, { memo } from 'react'
import { Box, Button, Typography, Chip, IconButton, Avatar } from '@mui/material'
import { Link } from 'react-router-dom'
import PersonIcon from '@mui/icons-material/Person'
import { NavigationItem } from './Navigation'
import { User } from '../types'

interface UserSectionProps {
  user: User | null
  userNavigation: NavigationItem[]
  isActive: (href: string) => boolean
  onProfileMenuOpen: (event: React.MouseEvent<HTMLElement>) => void
  isMobile?: boolean
}

export const UserSection: React.FC<UserSectionProps> = memo(({
  user,
  userNavigation,
  isActive,
  onProfileMenuOpen,
  isMobile = false
}) => {
  if (isMobile) return null

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {user ? (
        <>
          {userNavigation.map((item) => (
            <Button
              key={item.name}
              component={Link}
              to={item.href}
              startIcon={<item.icon />}
              color={isActive(item.href) ? 'primary' : 'inherit'}
              size="small"
            >
              {item.name}
            </Button>
          ))}
          
          <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
            <Typography variant="body2" sx={{ mr: 1 }}>
              {user.first_name} {user.last_name}
            </Typography>
            {user.user_type && (
              <Chip 
                label={user.user_type} 
                size="small" 
                color="primary" 
                variant="outlined"
                sx={{ mr: 1 }}
              />
            )}
            <IconButton onClick={onProfileMenuOpen} size="small">
              <Avatar sx={{ 
                width: 32, 
                height: 32,
                bgcolor: (theme) => theme.palette.mode === 'light' 
                  ? theme.palette.primary.main 
                  : theme.palette.primary.light,
                '&:hover': {
                  bgcolor: (theme) => theme.palette.mode === 'light' 
                    ? theme.palette.primary.dark 
                    : theme.palette.primary.main,
                }
              }}>
                <PersonIcon />
              </Avatar>
            </IconButton>
          </Box>
        </>
      ) : (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button component={Link} to="/login" variant="contained">
            Sign In
          </Button>
        </Box>
      )}
    </Box>
  )
})