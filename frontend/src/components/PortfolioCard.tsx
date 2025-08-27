import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Button,
  Paper,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  PlayArrow as PlayArrowIcon,
  TrendingUp as TrendingUpIcon,
  AccountBalance as AccountBalanceIcon,
} from '@mui/icons-material'
import { CircularProgress } from '@mui/material'

interface PortfolioStock {
  symbol: string
  allocation_percentage: number
}

interface Portfolio {
  id: number
  name: string
  description?: string
  stocks: PortfolioStock[]
  created_at: string
  updated_at: string
  is_active: boolean
  stats?: {
    total_stocks: number
    total_allocation: number
    largest_position: {
      symbol: string
      allocation: number
    }
    smallest_position: {
      symbol: string
      allocation: number
    }
  }
}

interface PortfolioCardProps {
  portfolio: Portfolio
  onAnalyze: (portfolio: Portfolio) => void
  onDelete: (portfolioId: number, portfolioName: string) => void
  isAnalyzing: boolean
}

export const PortfolioCard: React.FC<PortfolioCardProps> = ({
  portfolio,
  onAnalyze,
  onDelete,
  isAnalyzing,
}) => {
  const totalAllocation = portfolio.stocks.reduce(
    (sum, stock) => sum + stock.allocation_percentage,
    0
  )

  const largestPosition = portfolio.stocks.reduce((max, stock) =>
    stock.allocation_percentage > max.allocation_percentage ? stock : max
  )

  const getPortfolioTypeIcon = (name: string) => {
    if (name.toLowerCase().includes('tech') || name.toLowerCase().includes('innovation')) {
      return '🚀'
    } else if (name.toLowerCase().includes('dividend')) {
      return '💰'
    } else if (name.toLowerCase().includes('esg') || name.toLowerCase().includes('sustainable')) {
      return '🌱'
    } else if (name.toLowerCase().includes('etf') || name.toLowerCase().includes('balanced')) {
      return '⚖️'
    } else if (name.toLowerCase().includes('fintech')) {
      return '💳'
    }
    return '📊'
  }

  const getPortfolioTypeColor = (name: string) => {
    if (name.toLowerCase().includes('tech') || name.toLowerCase().includes('innovation')) {
      return 'primary'
    } else if (name.toLowerCase().includes('dividend')) {
      return 'success'
    } else if (name.toLowerCase().includes('esg') || name.toLowerCase().includes('sustainable')) {
      return 'success'
    } else if (name.toLowerCase().includes('etf') || name.toLowerCase().includes('balanced')) {
      return 'info'
    } else if (name.toLowerCase().includes('fintech')) {
      return 'secondary'
    }
    return 'default'
  }

  return (
    <Card 
      elevation={2}
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        '&:hover': {
          elevation: 4,
          transform: 'translateY(-2px)',
          transition: 'all 0.2s ease-in-out'
        }
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <span style={{ fontSize: '1.2em' }}>{getPortfolioTypeIcon(portfolio.name)}</span>
              {portfolio.name}
            </Typography>
            
            {portfolio.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {portfolio.description}
              </Typography>
            )}
          </Box>
          
          <IconButton
            size="small"
            color="error"
            onClick={() => onDelete(portfolio.id, portfolio.name)}
            sx={{ ml: 1 }}
          >
            <DeleteIcon />
          </IconButton>
        </Box>

        {/* Portfolio Stats */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
            <Paper elevation={0} sx={{ bgcolor: 'grey.100', px: 1, py: 0.5, borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Stocks: <strong>{portfolio.stocks.length}</strong>
              </Typography>
            </Paper>
            <Paper elevation={0} sx={{ bgcolor: 'grey.100', px: 1, py: 0.5, borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Allocation: <strong>{totalAllocation.toFixed(1)}%</strong>
              </Typography>
            </Paper>
          </Box>
          
          <Typography variant="caption" color="text.secondary">
            Top holding: <strong>{largestPosition.symbol} ({largestPosition.allocation_percentage}%)</strong>
          </Typography>
        </Box>

        {/* Stock Holdings */}
        <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <AccountBalanceIcon sx={{ fontSize: 16 }} />
          Holdings:
        </Typography>
        
        <Box sx={{ mb: 2, maxHeight: 120, overflowY: 'auto' }}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {portfolio.stocks
              .sort((a, b) => b.allocation_percentage - a.allocation_percentage)
              .map((stock, index) => (
                <Chip
                  key={index}
                  label={`${stock.symbol} ${stock.allocation_percentage}%`}
                  size="small"
                  variant="outlined"
                  color={index === 0 ? getPortfolioTypeColor(portfolio.name) as any : 'default'}
                  sx={{ 
                    fontSize: '0.75rem',
                    height: 24,
                    '& .MuiChip-label': {
                      px: 0.75
                    }
                  }}
                />
              ))}
          </Box>
        </Box>

        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
          Created: {new Date(portfolio.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          })}
        </Typography>
      </CardContent>

      {/* Action Button */}
      <Box sx={{ p: 2, pt: 0 }}>
        <Button
          variant="contained"
          fullWidth
          startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
          onClick={() => onAnalyze(portfolio)}
          disabled={isAnalyzing}
          color={getPortfolioTypeColor(portfolio.name) as any}
          sx={{ py: 1 }}
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Portfolio'}
        </Button>
      </Box>
    </Card>
  )
}