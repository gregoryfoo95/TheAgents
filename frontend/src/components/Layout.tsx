import React, { useState } from 'react'
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Container,
  Grid,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import {
  Home as HomeIcon,
  Search as SearchIcon,
  Scale as ScaleIcon,
  Dashboard as DashboardIcon,
  Message as MessageIcon,
  Event as EventIcon,
  Add as AddIcon,
  Menu as MenuIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'

export const Layout: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  
  const [mobileOpen, setMobileOpen] = useState(false)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

  const handleLogout = () => {
    logout()
    navigate('/')
    setAnchorEl(null)
  }

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleProfileMenuClose = () => {
    setAnchorEl(null)
  }

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const navigation = [
    { name: 'Home', href: '/', icon: HomeIcon },
    { name: 'Properties', href: '/properties', icon: SearchIcon },
    { name: 'Lawyers', href: '/lawyers', icon: ScaleIcon },
  ]

  const userNavigation = user ? [
    { name: 'Dashboard', href: '/dashboard', icon: DashboardIcon },
    { name: 'Messages', href: '/dashboard/chat', icon: MessageIcon },
    { name: 'Bookings', href: '/dashboard/bookings', icon: EventIcon },
    ...(user.user_type === 'seller' ? [
      { name: 'Add Property', href: '/dashboard/properties/create', icon: AddIcon }
    ] : [])
  ] : []

  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/'
    return location.pathname.startsWith(href)
  }

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Typography variant="h6" sx={{ p: 2, fontWeight: 'bold', color: 'primary.main' }}>
        DaAgents
      </Typography>
      <Divider />
      <List>
        {navigation.map((item) => (
          <ListItem key={item.name} disablePadding>
            <ListItemButton
              component={Link}
              to={item.href}
              selected={isActive(item.href)}
              onClick={() => setMobileOpen(false)}
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
                  onClick={() => setMobileOpen(false)}
                >
                  <ListItemIcon>
                    <item.icon color={isActive(item.href) ? 'primary' : 'inherit'} />
                  </ListItemIcon>
                  <ListItemText primary={item.name} />
                </ListItemButton>
              </ListItem>
            ))}
            <ListItem disablePadding>
              <ListItemButton onClick={handleLogout}>
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
              <ListItemButton component={Link} to="/login" onClick={() => setMobileOpen(false)}>
                <ListItemText primary="Sign In" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton component={Link} to="/register" onClick={() => setMobileOpen(false)}>
                <ListItemText primary="Sign Up" />
              </ListItemButton>
            </ListItem>
          </List>
        </>
      )}
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Typography
            variant="h6"
            component={Link}
            to="/"
            sx={{
              flexGrow: isMobile ? 1 : 0,
              fontWeight: 'bold',
              color: 'primary.main',
              textDecoration: 'none',
              mr: 4
            }}
          >
            DaAgents
          </Typography>

          {!isMobile && (
            <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
              {navigation.map((item) => (
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
          )}

          {!isMobile && (
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
                    <Chip 
                      label={user.user_type} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                      sx={{ mr: 1 }}
                    />
                    <IconButton onClick={handleProfileMenuOpen} size="small">
                      <Avatar sx={{ width: 32, height: 32 }}>
                        <PersonIcon />
                      </Avatar>
                    </IconButton>
                  </Box>
                </>
              ) : (
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button component={Link} to="/login" color="inherit">
                    Sign In
                  </Button>
                  <Button component={Link} to="/register" variant="contained">
                    Sign Up
                  </Button>
                </Box>
              )}
            </Box>
          )}
        </Toolbar>
      </AppBar>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleProfileMenuClose} component={Link} to="/dashboard">
          <DashboardIcon sx={{ mr: 1 }} />
          Profile
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <LogoutIcon sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
        }}
      >
        {drawer}
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Outlet />
      </Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          mt: 'auto',
          py: 6,
          backgroundColor: 'background.paper',
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                PropertyMarket
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                The modern way to buy and sell properties without agents. 
                Powered by AI valuations and smart recommendations.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                For Buyers
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  component={Link}
                  to="/properties"
                  variant="text"
                  size="small"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Browse Properties
                </Button>
                <Button
                  component={Link}
                  to="/lawyers"
                  variant="text"
                  size="small"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Find Lawyers
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                For Sellers
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  component={Link}
                  to="/register"
                  variant="text"
                  size="small"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  List Your Property
                </Button>
                <Button
                  component={Link}
                  to="/lawyers"
                  variant="text"
                  size="small"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Legal Support
                </Button>
              </Box>
            </Grid>
          </Grid>
          <Divider sx={{ my: 3 }} />
          <Typography variant="body2" color="text.secondary" align="center">
            © 2024 PropertyMarket. All rights reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  )
}