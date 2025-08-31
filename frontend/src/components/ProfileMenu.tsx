import React, { memo } from 'react'
import { Menu, MenuItem, Divider } from '@mui/material'
import { Link } from 'react-router-dom'
import DashboardIcon from '@mui/icons-material/Dashboard'
import LogoutIcon from '@mui/icons-material/Logout'

interface ProfileMenuProps {
  anchorEl: HTMLElement | null
  open: boolean
  onClose: () => void
  onLogout: () => void
}

export const ProfileMenu: React.FC<ProfileMenuProps> = memo(({
  anchorEl,
  open,
  onClose,
  onLogout
}) => {
  return (
    <Menu
      anchorEl={anchorEl}
      open={open}
      onClose={onClose}
      transformOrigin={{ horizontal: 'right', vertical: 'top' }}
      anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
    >
      <MenuItem 
        onClick={onClose} 
        component={Link} 
        to="/dashboard"
        sx={{
          '&:hover': {
            backgroundColor: (theme) => theme.palette.mode === 'light'
              ? theme.palette.primary.light + '20'
              : theme.palette.primary.dark + '20'
          }
        }}
      >
        <DashboardIcon sx={{ 
          mr: 1, 
          color: (theme) => theme.palette.primary.main 
        }} />
        Profile
      </MenuItem>
      <Divider />
      <MenuItem 
        onClick={onLogout}
        sx={{
          '&:hover': {
            backgroundColor: (theme) => theme.palette.mode === 'light'
              ? theme.palette.error.light + '20'
              : theme.palette.error.dark + '20'
          }
        }}
      >
        <LogoutIcon sx={{ 
          mr: 1,
          color: (theme) => theme.palette.error.main
        }} />
        Logout
      </MenuItem>
    </Menu>
  )
})