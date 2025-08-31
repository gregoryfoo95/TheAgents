import React from 'react'
import { Outlet } from 'react-router-dom'
import { Box } from '@mui/material'
import { useAuth } from '../contexts/AuthContext'
import { useNavigation } from '../hooks/useNavigation'
import { useLayoutState } from '../hooks/useLayoutState'
import { useActiveRoute } from '../hooks/useActiveRoute'
import { AppHeader } from './AppHeader'
import { ProfileMenu } from './ProfileMenu'
import { MobileDrawer } from './MobileDrawer'
import { Footer } from './Footer'

export const Layout: React.FC = () => {
  const { user, logout } = useAuth()
  const { publicNavigation, userNavigation } = useNavigation(user)
  const { isActive } = useActiveRoute()
  const {
    mobileOpen,
    anchorEl,
    handleDrawerToggle,
    handleProfileMenuOpen,
    handleProfileMenuClose,
    handleLogout,
  } = useLayoutState()


  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppHeader
        user={user}
        navigation={publicNavigation}
        userNavigation={userNavigation}
        isActive={isActive}
        onDrawerToggle={handleDrawerToggle}
        onProfileMenuOpen={handleProfileMenuOpen}
      />

      <ProfileMenu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        onLogout={() => handleLogout(logout)}
      />

      <MobileDrawer
        open={mobileOpen}
        onToggle={handleDrawerToggle}
        navigation={publicNavigation}
        userNavigation={userNavigation}
        user={user}
        isActive={isActive}
        onLogout={() => handleLogout(logout)}
      />

      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1,
          paddingTop: (theme) => theme.spacing(8), // Add padding for fixed AppBar
        }}
      >
        <Outlet />
      </Box>

      <Footer />
    </Box>
  )
}