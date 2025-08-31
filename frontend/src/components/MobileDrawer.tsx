import React, { memo } from 'react'
import {
  Drawer,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material'
import { Link } from 'react-router-dom'
import LogoutIcon from '@mui/icons-material/Logout'
import { Brand } from './Brand'
import { NavigationItem } from './Navigation'
import { ThemeToggle } from './ThemeToggle'
import { User } from '../types'
import { LAYOUT_CONSTANTS } from '../constants/layout'

interface MobileDrawerProps {
  open: boolean
  onToggle: () => void
  navigation: NavigationItem[]
  userNavigation: NavigationItem[]
  user: User | null
  isActive: (href: string) => boolean
  onLogout: () => void
}


export const MobileDrawer: React.FC<MobileDrawerProps> = memo(({
  open,
  onToggle,
  navigation,
  userNavigation,
  user,
  isActive,
  onLogout
}) => {
  const handleClose = () => onToggle()

  const drawerContent = (
    <Box sx={{ width: LAYOUT_CONSTANTS.DRAWER_WIDTH }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', px: 2, py: 1 }}>
        <Brand 
          sx={{ 
            fontSize: '1.25rem',
          }}
        />
        <ThemeToggle size="small" />
      </Box>
      <Divider />
      <List>
        {navigation.map((item) => (
          <ListItem key={item.name} disablePadding>
            <ListItemButton
              component={Link}
              to={item.href}
              selected={isActive(item.href)}
              onClick={handleClose}
            >
              <ListItemIcon>
                <item.icon color={isActive(item.href) ? 'primary' : 'inherit'} />
              </ListItemIcon>
              <ListItemText primary={item.name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      {user && (
        <>
          <Divider />
          <List>
            {userNavigation.map((item) => (
              <ListItem key={item.name} disablePadding>
                <ListItemButton
                  component={Link}
                  to={item.href}
                  selected={isActive(item.href)}
                  onClick={handleClose}
                >
                  <ListItemIcon>
                    <item.icon color={isActive(item.href) ? 'primary' : 'inherit'} />
                  </ListItemIcon>
                  <ListItemText primary={item.name} />
                </ListItemButton>
              </ListItem>
            ))}
            <ListItem disablePadding>
              <ListItemButton onClick={onLogout}>
                <ListItemIcon>
                  <LogoutIcon />
                </ListItemIcon>
                <ListItemText primary="Logout" />
              </ListItemButton>
            </ListItem>
          </List>
        </>
      )}
      {!user && (
        <>
          <Divider />
          <List>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/login" onClick={handleClose}>
                <ListItemText primary="Sign In" />
              </ListItemButton>
            </ListItem>
          </List>
        </>
      )}
    </Box>
  )

  return (
    <Drawer
      variant="temporary"
      open={open}
      onClose={onToggle}
      ModalProps={{ keepMounted: true }}
      sx={{
        display: { xs: 'block', [LAYOUT_CONSTANTS.MOBILE_BREAKPOINT]: 'none' },
        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: LAYOUT_CONSTANTS.DRAWER_WIDTH },
      }}
    >
      {drawerContent}
    </Drawer>
  )
})