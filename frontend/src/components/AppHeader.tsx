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
      position="static" 
      elevation={0}
      sx={{
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(99, 102, 241, 0.1)',
      }}
    >
      <Toolbar>
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
          showLogo={true}
          sx={{
            flexGrow: isMobile ? 1 : 0,
            mr: 4,
            fontSize: '1.5rem',
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