import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Skeleton,
  Alert,
  Paper,
  Collapse,
  InputAdornment,
  Fab,
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  LocationOn as LocationIcon,
  Bed as BedIcon,
  Bathtub as BathtubIcon,
  SquareFoot as SquareFootIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  ViewModule as GridViewIcon,
  ViewList as ListViewIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material'
import { useInfiniteProperties } from '../hooks/useProperties'
import type { PropertyFilters } from '../types'

export const PropertiesPage: React.FC = () => {
  const [filters, setFilters] = useState<PropertyFilters>({})
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [favorites, setFavorites] = useState<Set<number>>(new Set())
  
  // Use infinite query for better UX
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteProperties(filters, 12)

  const handleFilterChange = (newFilters: Partial<PropertyFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
  }

  const clearFilters = () => {
    setFilters({})
    setSearchQuery('')
  }

  const toggleFavorite = (propertyId: number, event: React.MouseEvent) => {
    event.preventDefault()
    event.stopPropagation()
    setFavorites(prev => {
      const newFavorites = new Set(prev)
      if (newFavorites.has(propertyId)) {
        newFavorites.delete(propertyId)
      } else {
        newFavorites.add(propertyId)
      }
      return newFavorites
    })
  }

  const properties = data?.pages.flatMap(page => page.items) ?? []
  const totalProperties = data?.pages[0]?.total ?? 0

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>Something went wrong</Typography>
          <Typography>Failed to load properties. Please try again.</Typography>
          <Button onClick={() => window.location.reload()} sx={{ mt: 2 }}>
            Try Again
          </Button>
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
          Properties for Sale
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {isLoading ? 'Loading...' : `${totalProperties.toLocaleString()} properties available`}
        </Typography>
      </Box>

      {/* Search and Filter Controls */}
      <Paper sx={{ p: 3, mb: 4 }}>
        {/* Search Bar */}
        <TextField
          fullWidth
          placeholder="Search by city, address, or property type..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        {/* Filter Controls */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Button
            startIcon={<FilterIcon />}
            endIcon={showFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            onClick={() => setShowFilters(!showFilters)}
            variant="outlined"
          >
            Filters
          </Button>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              View:
            </Typography>
            <IconButton
              onClick={() => setViewMode('grid')}
              color={viewMode === 'grid' ? 'primary' : 'default'}
              size="small"
            >
              <GridViewIcon />
            </IconButton>
            <IconButton
              onClick={() => setViewMode('list')}
              color={viewMode === 'list' ? 'primary' : 'default'}
              size="small"
            >
              <ListViewIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Filters Panel */}
        <Collapse in={showFilters}>
          <Box sx={{ pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Min Price"
                  type="number"
                  value={filters.min_price || ''}
                  onChange={(e) => handleFilterChange({ min_price: Number(e.target.value) || undefined })}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Max Price"
                  type="number"
                  value={filters.max_price || ''}
                  onChange={(e) => handleFilterChange({ max_price: Number(e.target.value) || undefined })}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Bedrooms</InputLabel>
                  <Select
                    value={filters.bedrooms || ''}
                    label="Bedrooms"
                    onChange={(e) => handleFilterChange({ bedrooms: Number(e.target.value) || undefined })}
                  >
                    <MenuItem value="">Any</MenuItem>
                    <MenuItem value={1}>1+</MenuItem>
                    <MenuItem value={2}>2+</MenuItem>
                    <MenuItem value={3}>3+</MenuItem>
                    <MenuItem value={4}>4+</MenuItem>
                    <MenuItem value={5}>5+</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Property Type</InputLabel>
                  <Select
                    value={filters.property_type || ''}
                    label="Property Type"
                    onChange={(e) => handleFilterChange({ property_type: e.target.value || undefined })}
                  >
                    <MenuItem value="">Any</MenuItem>
                    <MenuItem value="house">House</MenuItem>
                    <MenuItem value="apartment">Apartment</MenuItem>
                    <MenuItem value="condo">Condo</MenuItem>
                    <MenuItem value="townhouse">Townhouse</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={clearFilters} variant="outlined">
                Clear Filters
              </Button>
            </Box>
          </Box>
        </Collapse>
      </Paper>

      {/* Loading State */}
      {isLoading && (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, i) => (
            <Grid item xs={12} sm={6} md={viewMode === 'grid' ? 4 : 12} key={i}>
              <Card>
                <Skeleton variant="rectangular" height={200} />
                <CardContent>
                  <Skeleton variant="text" height={32} />
                  <Skeleton variant="text" height={24} />
                  <Skeleton variant="text" height={20} width="60%" />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Properties Grid/List */}
      {!isLoading && (
        <>
          <Grid container spacing={3}>
            {properties.map((property) => (
              <Grid 
                item 
                xs={12} 
                sm={6} 
                md={viewMode === 'grid' ? 4 : 12} 
                key={property.id}
              >
                <Card
                  component={Link}
                  to={`/properties/${property.id}`}
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: viewMode === 'list' ? 'row' : 'column',
                    textDecoration: 'none',
                    color: 'inherit',
                    transition: 'all 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                  }}
                >
                  <CardMedia
                    component="img"
                    image={property.images?.[0] || '/placeholder-property.jpg'}
                    alt={property.title}
                    sx={{
                      height: viewMode === 'list' ? 200 : 240,
                      width: viewMode === 'list' ? 300 : '100%',
                      objectFit: 'cover',
                    }}
                  />
                  
                  <CardContent sx={{ flexGrow: 1, position: 'relative' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                        {property.title}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={(e) => toggleFavorite(property.id, e)}
                        sx={{ ml: 1 }}
                      >
                        {favorites.has(property.id) ? (
                          <FavoriteIcon color="error" />
                        ) : (
                          <FavoriteBorderIcon />
                        )}
                      </IconButton>
                    </Box>
                    
                    <Typography 
                      variant="h5" 
                      color="primary" 
                      fontWeight="bold" 
                      sx={{ mb: 1 }}
                    >
                      ${property.price.toLocaleString()}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, color: 'text.secondary' }}>
                      <LocationIcon sx={{ fontSize: 16, mr: 0.5 }} />
                      <Typography variant="body2">
                        {property.city}, {property.state}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      {property.bedrooms && (
                        <Chip
                          icon={<BedIcon />}
                          label={`${property.bedrooms} bed`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                      {property.bathrooms && (
                        <Chip
                          icon={<BathtubIcon />}
                          label={`${property.bathrooms} bath`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                      {property.square_feet && (
                        <Chip
                          icon={<SquareFootIcon />}
                          label={`${property.square_feet.toLocaleString()} sq ft`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Load More Button */}
          {hasNextPage && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => fetchNextPage()}
                disabled={isFetchingNextPage}
                sx={{ px: 4 }}
              >
                {isFetchingNextPage ? 'Loading...' : 'Load More Properties'}
              </Button>
            </Box>
          )}

          {/* Empty State */}
          {properties.length === 0 && !isLoading && (
            <Paper sx={{ p: 6, textAlign: 'center', mt: 4 }}>
              <Typography variant="h5" color="text.secondary" gutterBottom>
                No properties found
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Try adjusting your search criteria or filters
              </Typography>
              <Button variant="contained" onClick={clearFilters}>
                Clear Filters
              </Button>
            </Paper>
          )}
        </>
      )}

      {/* Floating Action Button for mobile */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: { xs: 'flex', md: 'none' },
        }}
        onClick={() => setShowFilters(!showFilters)}
      >
        <FilterIcon />
      </Fab>
    </Container>
  )
}