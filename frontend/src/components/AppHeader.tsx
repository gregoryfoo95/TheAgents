import React, { memo } from 'react'
import { AppBar, Toolbar, IconButton, useMediaQuery, useTheme } from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import { Brand } from './Brand'
import { Navigation, NavigationItem } from './Navigation'
import { UserSection } from './UserSection'
import { ThemeToggle } from './ThemeToggle'
import { User } from '../types'
import { LAYOUT_CONSTANTS } from '../constants/layout'

interface AppHeaderProps {
  user: User | null
  navigation: NavigationItem[]
  userNavigation: NavigationItem[]
  isActive: (href: string) => boolean
  onDrawerToggle: () => void
  onProfileMenuOpen: (event: React.MouseEvent<HTMLElement>) => void
}

type AppHeaderComponent = React.FC<AppHeaderProps>


export const AppHeader: AppHeaderComponent = memo(({
  user,
  navigation,
  userNavigation,
  isActive,
  onDrawerToggle,
  onProfileMenuOpen
}) => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down(LAYOUT_CONSTANTS.MOBILE_BREAKPOINT))

  return (
    <AppBar 
      position="fixed" 
      elevation={0}
      sx={{
        backdropFilter: 'blur(10px)',
        backgroundColor: (theme) => theme.palette.mode === 'light' 
          ? 'rgba(255, 255, 255, 0.95)' 
          : 'rgba(19, 78, 74, 0.95)',
        borderBottom: (theme) => `1px solid ${theme.palette.mode === 'light' ? 'rgba(20, 184, 166, 0.1)' : 'rgba(20, 184, 166, 0.2)'}`,
        zIndex: (theme) => theme.zIndex.appBar,
      }}
    >
      <Toolbar sx={{ minHeight: '56px !important', py: 0.5 }}>
        {isMobile && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        <Brand
          to="/"
          sx={{
            flexGrow: isMobile ? 1 : 0,
            mr: 2,
            fontSize: '1.3rem',
          }}
        />

        <Navigation 
          items={navigation} 
          isActive={isActive} 
          isMobile={isMobile} 
        />

        <ThemeToggle size="small" />

        <UserSection
          user={user}
          userNavigation={userNavigation}
          isActive={isActive}
          onProfileMenuOpen={onProfileMenuOpen}
          isMobile={isMobile}
        />
      </Toolbar>
    </AppBar>
  )
})