import React, { memo } from 'react'
import { Box, Container, Grid, Typography, Button, Divider } from '@mui/material'
import { Link } from 'react-router-dom'

const FOOTER_LINKS = {
  buyers: [
    { name: 'Browse Properties', href: '/properties' },
    { name: 'Find Lawyers', href: '/lawyers' },
  ],
  sellers: [
    { name: 'List Your Property', href: '/login' },
    { name: 'Legal Support', href: '/lawyers' },
  ]
}

const COMPANY_NAME = 'Agent$'
const COMPANY_DESCRIPTION = 'The modern way to buy and sell properties without agents. Powered by AI valuations and smart recommendations.'
const COPYRIGHT_YEAR = '2024'

export const Footer: React.FC = memo(() => {
  return (
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
              {COMPANY_NAME}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {COMPANY_DESCRIPTION}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              For Buyers
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {FOOTER_LINKS.buyers.map((link) => (
                <Button
                  key={link.name}
                  component={Link}
                  to={link.href}
                  variant="text"
                  size="small"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  {link.name}
                </Button>
              ))}
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              For Sellers
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {FOOTER_LINKS.sellers.map((link) => (
                <Button
                  key={link.name}
                  component={Link}
                  to={link.href}
                  variant="text"
                  size="small"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  {link.name}
                </Button>
              ))}
            </Box>
          </Grid>
        </Grid>
        <Divider sx={{ my: 3 }} />
        <Typography variant="body2" color="text.secondary" align="center">
          © {COPYRIGHT_YEAR} {COMPANY_NAME}. All rights reserved.
        </Typography>
      </Container>
    </Box>
  )
})