import React from 'react'
import { Link } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Stack,
} from '@mui/material'
import {
  Search as SearchIcon,
  Psychology as BrainIcon,
  Gavel as ScaleIcon,
  Message as MessageIcon,
  Security as ShieldIcon,
  ArrowForward as ArrowRightIcon,
} from '@mui/icons-material'

export const HomePage: React.FC = () => {
  const features = [
    {
      icon: <BrainIcon sx={{ fontSize: 40 }} />,
      title: 'AI-Powered Valuations',
      description: 'Get accurate property valuations powered by machine learning and market data analysis.',
    },
    {
      icon: <SearchIcon sx={{ fontSize: 40 }} />,
      title: 'Smart Search',
      description: 'Find your perfect property with intelligent filters and personalized recommendations.',
    },
    {
      icon: <ScaleIcon sx={{ fontSize: 40 }} />,
      title: 'Legal Support',
      description: 'Connect with verified lawyers for seamless transaction support and documentation.',
    },
    {
      icon: <MessageIcon sx={{ fontSize: 40 }} />,
      title: 'Direct Communication',
      description: 'Chat directly with buyers, sellers, and lawyers in secure, integrated messaging.',
    },
    {
      icon: <ShieldIcon sx={{ fontSize: 40 }} />,
      title: 'Secure Transactions',
      description: 'End-to-end security with verified users and protected payment processing.',
    },
  ]

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
          color: 'white',
          py: 12,
          textAlign: 'center',
        }}
      >
        <Container maxWidth="lg">
          <Typography
            variant="h2"
            component="h1"
            fontWeight="bold"
            gutterBottom
            sx={{ fontSize: { xs: '2.5rem', md: '3.5rem', lg: '4rem' } }}
          >
            Buy & Sell Properties
          </Typography>
          <Typography
            variant="h4"
            sx={{
              color: 'primary.200',
              mb: 3,
              fontSize: { xs: '1.5rem', md: '2rem' },
            }}
          >
            Without Agents, by Agents
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 600,
            mx: 'auto',
              mb: 4,
              opacity: 0.9,
              lineHeight: 1.6,
            }}
          >
            Connect directly with buyers and sellers. Get AI-powered property valuations, 
            smart improvement recommendations, and seamless legal support.
          </Typography>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            justifyContent="center"
            sx={{ mt: 4 }}
          >
            <Button
              component={Link}
              to="/properties"
              variant="contained"
              size="large"
              endIcon={<SearchIcon />}
              sx={{
                bgcolor: 'white',
                color: 'primary.main',
                px: 4,
                py: 1.5,
                '&:hover': {
                  bgcolor: 'grey.100',
                },
              }}
            >
              Browse Properties
            </Button>
            <Button
              component={Link}
              to="/login"
              variant="outlined"
              size="large"
              endIcon={<ArrowRightIcon />}
              sx={{
                borderColor: 'white',
                color: 'white',
                px: 4,
                py: 1.5,
                '&:hover': {
                  borderColor: 'white',
                  bgcolor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
            >
              Sign In
            </Button>
          </Stack>
        </Container>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: 8, bgcolor: 'background.default' }}>
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            component="h2"
            textAlign="center"
            fontWeight="bold"
            gutterBottom
            sx={{ mb: 6 }}
          >
            Why Choose Agent$?
          </Typography>
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} lg={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    textAlign: 'center',
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ color: 'primary.main', mb: 2 }}>
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" component="h3" fontWeight="bold" gutterBottom>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box sx={{ py: 8, bgcolor: 'background.paper' }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h4" component="h2" fontWeight="bold" gutterBottom>
              Ready to revolutionize your property experience?
            </Typography>
            <Typography variant="h6" color="text.secondary" paragraph>
              Join thousands of users who have already discovered a better way to buy and sell properties.
            </Typography>
            <Button
              component={Link}
              to="/login"
              variant="contained"
              size="large"
              sx={{ mt: 2, px: 4, py: 1.5 }}
            >
              Sign In to Start
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  )
}