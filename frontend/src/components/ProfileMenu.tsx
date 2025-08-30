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
      <MenuItem onClick={onClose} component={Link} to="/dashboard">
        <DashboardIcon sx={{ mr: 1 }} />
        Profile
      </MenuItem>
      <Divider />
      <MenuItem onClick={onLogout}>
        <LogoutIcon sx={{ mr: 1 }} />
        Logout
      </MenuItem>
    </Menu>
  )
})