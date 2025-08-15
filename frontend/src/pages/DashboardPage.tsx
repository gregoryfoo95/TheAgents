import {
    Event as CalendarIcon,
    Home as HomeIcon,
    Message as MessageIcon,
    Add as PlusIcon,
    TrendingUp,
    People as UsersIcon,
} from '@mui/icons-material'
import {
    Avatar,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Container,
    Grid,
    Skeleton,
    Stack,
    Typography,
} from '@mui/material'
import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useConversations, useMyBookings, useMyProperties } from '../hooks'

export const DashboardPage: React.FC = () => {
  const { user } = useAuth()
  
  // Fetch user's data based on their role
  const { data: properties, isLoading: propertiesLoading } = useMyProperties()
  const { data: bookings, isLoading: bookingsLoading } = useMyBookings()
  const { data: conversations, isLoading: conversationsLoading } = useConversations()

  // Calculate stats
  const activeProperties = properties?.filter(p => p.status === 'active').length || 0
  const pendingBookings = bookings?.filter(b => b.status === 'pending').length || 0
  const unreadConversations = conversations?.filter(c => c.status === 'active').length || 0

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  const isLoading = propertiesLoading || bookingsLoading || conversationsLoading

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
          {getGreeting()}, {user?.first_name}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome to your dashboard. Here's what's happening with your properties.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Active Properties */}
        <Grid item xs={12} sm={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <HomeIcon sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {isLoading ? '...' : activeProperties}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Properties
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Pending Bookings */}
        <Grid item xs={12} sm={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CalendarIcon sx={{ fontSize: 32, color: 'warning.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {isLoading ? '...' : pendingBookings}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending Bookings
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Conversations */}
        <Grid item xs={12} sm={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <MessageIcon sx={{ fontSize: 32, color: 'success.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    {isLoading ? '...' : unreadConversations}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Chats
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Total Revenue */}
        <Grid item xs={12} sm={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ fontSize: 32, color: 'secondary.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" component="div" fontWeight="bold">
                    ${properties?.reduce((sum, p) => sum + p.price, 0)?.toLocaleString() || '0'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Value
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={4}>
        {/* Recent Properties */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2" fontWeight="semibold">
                  Recent Properties
                </Typography>
                <Button
                  component={Link}
                  to="/create-property"
                  variant="outlined"
                  size="small"
                  startIcon={<PlusIcon />}
                >
                  Add Property
                </Button>
              </Box>
          
              {propertiesLoading ? (
                <Stack spacing={2}>
                  {[...Array(3)].map((_, i) => (
                    <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Skeleton variant="rectangular" width={64} height={64} />
                      <Box sx={{ flex: 1 }}>
                        <Skeleton variant="text" width="75%" />
                        <Skeleton variant="text" width="50%" />
                      </Box>
                    </Box>
                  ))}
                </Stack>
              ) : properties && properties.length > 0 ? (
                <Stack spacing={1}>
                  {properties.slice(0, 3).map((property) => (
                    <Box
                      key={property.id}
                      component={Link}
                      to={`/properties/${property.id}`}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        p: 2,
                        borderRadius: 1,
                        textDecoration: 'none',
                        color: 'inherit',
                        '&:hover': { bgcolor: 'grey.50' },
                      }}
                    >
                      <Avatar
                        src={property.images?.[0] || '/placeholder-property.jpg'}
                        alt={property.title}
                        variant="rounded"
                        sx={{ width: 64, height: 64 }}
                      />
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="body2" fontWeight="medium" noWrap>
                          {property.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          ${property.price.toLocaleString()}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {property.city}, {property.state}
                        </Typography>
                      </Box>
                      <Chip
                        size="small"
                        label={property.status}
                        color={
                          property.status === 'active'
                            ? 'success'
                            : property.status === 'pending'
                            ? 'warning'
                            : 'default'
                        }
                      />
                    </Box>
                  ))}
                  {properties.length > 3 && (
                    <Button
                      component={Link}
                      to="/properties/my"
                      variant="text"
                      size="small"
                      sx={{ mt: 1 }}
                    >
                      View all properties →
                    </Button>
                  )}
                </Stack>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <HomeIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    No properties yet
                  </Typography>
                  <Button
                    component={Link}
                    to="/create-property"
                    variant="contained"
                    size="small"
                    sx={{ mt: 2 }}
                  >
                    List Your First Property
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Conversations */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2" fontWeight="semibold">
                  Recent Conversations
                </Typography>
                <Button
                  component={Link}
                  to="/chat"
                  variant="text"
                  size="small"
                >
                  View all
                </Button>
              </Box>
          
              {conversationsLoading ? (
                <Stack spacing={2}>
                  {[...Array(3)].map((_, i) => (
                    <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Skeleton variant="circular" width={40} height={40} />
                      <Box sx={{ flex: 1 }}>
                        <Skeleton variant="text" width="75%" />
                        <Skeleton variant="text" width="50%" />
                      </Box>
                    </Box>
                  ))}
                </Stack>
              ) : conversations && conversations.length > 0 ? (
                <Stack spacing={1}>
                  {conversations.slice(0, 5).map((conversation) => (
                    <Box
                      key={conversation.id}
                      component={Link}
                      to={`/chat/${conversation.id}`}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        p: 2,
                        borderRadius: 1,
                        textDecoration: 'none',
                        color: 'inherit',
                        '&:hover': { bgcolor: 'grey.50' },
                      }}
                    >
                      <Avatar sx={{ bgcolor: 'primary.light' }}>
                        <UsersIcon />
                      </Avatar>
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="body2" fontWeight="medium" noWrap>
                          {conversation.property.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          with {user?.user_type === 'seller' ? conversation.buyer.first_name : conversation.seller.first_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {conversation.messages.length} messages
                        </Typography>
                      </Box>
                      <Chip
                        size="small"
                        label={conversation.status}
                        color={conversation.status === 'active' ? 'success' : 'default'}
                      />
                    </Box>
                  ))}
                </Stack>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <MessageIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    No conversations yet
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Start chatting when someone shows interest in your properties
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" component="h2" fontWeight="semibold" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6} md={3}>
            <Button
              component={Link}
              to="/create-property"
              variant="outlined"
              fullWidth
              sx={{
                flexDirection: 'column',
                py: 3,
                gap: 1,
              }}
            >
              <PlusIcon sx={{ fontSize: 32 }} />
              <Typography variant="caption">Add Property</Typography>
            </Button>
          </Grid>
          
          <Grid item xs={6} md={3}>
            <Button
              component={Link}
              to="/properties"
              variant="outlined"
              fullWidth
              sx={{
                flexDirection: 'column',
                py: 3,
                gap: 1,
              }}
            >
              <HomeIcon sx={{ fontSize: 32 }} />
              <Typography variant="caption">Browse Properties</Typography>
            </Button>
          </Grid>
          
          <Grid item xs={6} md={3}>
            <Button
              component={Link}
              to="/bookings"
              variant="outlined"
              fullWidth
              sx={{
                flexDirection: 'column',
                py: 3,
                gap: 1,
              }}
            >
              <CalendarIcon sx={{ fontSize: 32 }} />
              <Typography variant="caption">View Bookings</Typography>
            </Button>
          </Grid>
          
          <Grid item xs={6} md={3}>
            <Button
              component={Link}
              to="/chat"
              variant="outlined"
              fullWidth
              sx={{
                flexDirection: 'column',
                py: 3,
                gap: 1,
              }}
            >
              <MessageIcon sx={{ fontSize: 32 }} />
              <Typography variant="caption">Messages</Typography>
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Container>
  )
} 