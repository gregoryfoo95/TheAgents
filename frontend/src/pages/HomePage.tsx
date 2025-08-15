import React, { useState, useEffect } from 'react'
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
  SmartToy as RobotIcon,
} from '@mui/icons-material'

export const HomePage: React.FC = () => {
  const [mascotPosition, setMascotPosition] = useState({ x: 20, y: 20 })
  const [mascotAnimation, setMascotAnimation] = useState('bounce')
  const [clickCount, setClickCount] = useState(0)
  
  const animations = ['jump', 'bounce', 'float', 'wiggle']
  
  // Random movement and animation changes
  useEffect(() => {
    const moveInterval = setInterval(() => {
      // Random position within hero section bounds (with some padding)
      const newX = Math.random() * 70 + 10 // 10% to 80% from left
      const newY = Math.random() * 50 + 15 // 15% to 65% from top
      const newAnimation = animations[Math.floor(Math.random() * animations.length)]
      
      setMascotPosition({ x: newX, y: newY })
      setMascotAnimation(newAnimation)
    }, 3500 + Math.random() * 2000) // Random interval between 3.5-5.5 seconds
    
    return () => clearInterval(moveInterval)
  }, [])

  // Initial random position
  useEffect(() => {
    const initialX = Math.random() * 70 + 10
    const initialY = Math.random() * 50 + 15
    setMascotPosition({ x: initialX, y: initialY })
  }, [])

  const handleMascotClick = () => {
    setClickCount(prev => prev + 1)
    // Jump to a new position when clicked
    const newX = Math.random() * 80 + 5
    const newY = Math.random() * 60 + 10
    setMascotPosition({ x: newX, y: newY })
    setMascotAnimation('jump')
    
    // Special effects for multiple clicks
    if (clickCount >= 5) {
      setMascotAnimation('wiggle')
      setClickCount(0)
    }
  }

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
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: { xs: 8, md: 12, lg: 16 },
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
            pointerEvents: 'none',
          },
        }}
        className="fade-in"
      >
        {/* Animated Robot Mascot */}
        <Box
          className={`robot-mascot ${mascotAnimation}`}
          sx={{
            left: `${mascotPosition.x}%`,
            top: `${mascotPosition.y}%`,
            transition: 'left 2s ease-in-out, top 2s ease-in-out',
          }}
          onClick={handleMascotClick}
          title={`Click me! I'm your AI assistant! (Clicks: ${clickCount})`}
        >
          <RobotIcon
            sx={{
              fontSize: { xs: 50, md: 60 },
              color: '#ffffff',
              background: clickCount >= 3 
                ? 'linear-gradient(135deg, #f093fb, #f5576c)' 
                : 'linear-gradient(135deg, #667eea, #764ba2)',
              borderRadius: '50%',
              padding: 2,
              boxShadow: clickCount >= 3 
                ? '0 8px 24px rgba(240, 147, 251, 0.6)' 
                : '0 8px 24px rgba(99, 102, 241, 0.4)',
              border: '3px solid rgba(255, 255, 255, 0.3)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'scale(1.1) rotate(5deg)',
              },
            }}
          />
        </Box>

        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Typography
            variant="h1"
            component="h1"
            fontWeight="800"
            gutterBottom
            className="slide-up"
            sx={{ 
              fontSize: { xs: '2.5rem', md: '4rem', lg: '5rem' },
              background: 'linear-gradient(45deg, #ffffff 30%, #f0f9ff 90%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2,
              letterSpacing: '-0.02em',
            }}
          >
            Your Home, Your Asset
          </Typography>
          <Typography
            variant="h3"
            sx={{
              background: 'linear-gradient(45deg, #a78bfa 30%, #c084fc 90%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 4,
              fontSize: { xs: '1.75rem', md: '2.5rem' },
              fontWeight: 600,
            }}
            className="slide-up"
          >
            Without Agents, by Agent$
          </Typography>
          <Typography
            variant="h6"
            sx={{
              maxWidth: 700,
              mx: 'auto',
              mb: 6,
              opacity: 0.95,
              lineHeight: 1.7,
              fontSize: { xs: '1.1rem', md: '1.25rem' },
              color: 'rgba(255, 255, 255, 0.9)',
            }}
            className="slide-up"
          >
            Experience the future of real estate. Connect directly with buyers and sellers, 
            leverage AI-powered valuations, and get expert legal support—all in one seamless platform.
          </Typography>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={3}
            justifyContent="center"
            sx={{ mt: 6 }}
            className="slide-up"
          >
            <Button
              component={Link}
              to="/properties"
              variant="contained"
              size="large"
              endIcon={<SearchIcon />}
              sx={{
                background: 'linear-gradient(45deg, #ffffff 30%, #f8fafc 90%)',
                color: '#4f46e5',
                px: 6,
                py: 2,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: '16px',
                textTransform: 'none',
                boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 20px 35px rgba(0, 0, 0, 0.2)',
                  background: 'linear-gradient(45deg, #f8fafc 30%, #ffffff 90%)',
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
                borderColor: 'rgba(255, 255, 255, 0.5)',
                color: 'white',
                px: 6,
                py: 2,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: '16px',
                textTransform: 'none',
                borderWidth: '2px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  borderColor: 'white',
                  background: 'rgba(255, 255, 255, 0.15)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)',
                },
              }}
            >
              Get Started
            </Button>
          </Stack>
        </Container>
      </Box>

      {/* Features Section */}
      <Box sx={{ 
        py: { xs: 8, md: 12 },
        background: 'linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)',
        position: 'relative',
      }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <Typography
              variant="h3"
              component="h2"
              fontWeight="800"
              gutterBottom
              className="slide-up"
              sx={{ 
                mb: 3,
                background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: { xs: '2rem', md: '3rem' },
              }}
            >
              Why Choose Agent$?
            </Typography>
            <Typography
              variant="h6"
              color="text.secondary"
              sx={{ 
                maxWidth: 600,
                mx: 'auto',
                fontSize: '1.2rem',
                lineHeight: 1.6,
              }}
              className="slide-up"
            >
              Revolutionary features that transform how you buy and sell properties
            </Typography>
          </Box>
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} lg={4} key={index}>
                <Card
                  className="modern-card slide-up"
                  sx={{
                    height: '100%',
                    textAlign: 'center',
                    background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                    border: '1px solid rgba(99, 102, 241, 0.1)',
                    borderRadius: '20px',
                    overflow: 'hidden',
                    position: 'relative',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '4px',
                      background: 'linear-gradient(90deg, #667eea, #764ba2)',
                    },
                    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-12px) scale(1.02)',
                      boxShadow: '0 25px 50px rgba(99, 102, 241, 0.15)',
                      border: '1px solid rgba(99, 102, 241, 0.2)',
                    },
                  }}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <CardContent sx={{ p: 5 }}>
                    <Box 
                      sx={{ 
                        background: 'linear-gradient(135deg, #667eea, #764ba2)',
                        borderRadius: '16px',
                        width: 80,
                        height: 80,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mx: 'auto',
                        mb: 3,
                        color: 'white',
                        boxShadow: '0 8px 24px rgba(99, 102, 241, 0.3)',
                      }}
                    >
                      {React.cloneElement(feature.icon, { sx: { fontSize: 40 } })}
                    </Box>
                    <Typography 
                      variant="h5" 
                      component="h3" 
                      fontWeight="700" 
                      gutterBottom
                      sx={{ 
                        color: '#1e293b',
                        mb: 2,
                        fontSize: '1.3rem',
                      }}
                    >
                      {feature.title}
                    </Typography>
                    <Typography 
                      variant="body1" 
                      color="text.secondary"
                      sx={{ 
                        lineHeight: 1.7,
                        fontSize: '1rem',
                      }}
                    >
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
      <Box sx={{ 
        py: { xs: 8, md: 12 },
        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%)',
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 70% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
          pointerEvents: 'none',
        },
      }}>
        <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography 
              variant="h3" 
              component="h2" 
              fontWeight="800" 
              gutterBottom
              className="slide-up"
              sx={{
                fontSize: { xs: '2rem', md: '3rem' },
                mb: 3,
                background: 'linear-gradient(45deg, #ffffff 30%, #f0f9ff 90%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                letterSpacing: '-0.02em',
              }}
            >
              Ready to revolutionize your property experience?
            </Typography>
            <Typography 
              variant="h6" 
              paragraph
              className="slide-up"
              sx={{
                opacity: 0.95,
                lineHeight: 1.6,
                fontSize: '1.2rem',
                mb: 4,
                maxWidth: 600,
                mx: 'auto',
              }}
            >
              Join thousands of users who have already discovered a better way to buy and sell properties. 
              Experience the future today.
            </Typography>
            <Box className="slide-up">
              <Button
                component={Link}
                to="/login"
                variant="contained"
                size="large"
                sx={{ 
                  background: 'linear-gradient(45deg, #ffffff 30%, #f8fafc 90%)',
                  color: '#4f46e5',
                  mt: 2, 
                  px: 6, 
                  py: 2,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderRadius: '16px',
                  textTransform: 'none',
                  boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'translateY(-3px)',
                    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                    background: 'linear-gradient(45deg, #f8fafc 30%, #ffffff 90%)',
                  },
                }}
              >
                Start Your Journey
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>
    </Box>
  )
}