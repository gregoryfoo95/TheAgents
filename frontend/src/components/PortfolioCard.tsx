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
  CircularProgress,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  PlayArrow as PlayArrowIcon,
  AccountBalance as AccountBalanceIcon,
} from '@mui/icons-material'
import { Portfolio } from '../hooks/usePortfolio'

interface PortfolioCardProps {
  portfolio: Portfolio
  onAnalyze: (portfolio: Portfolio) => void
  onDelete: (portfolioId: number, portfolioName: string) => void
  isAnalyzing: boolean
  onOpenModal?: (portfolio: Portfolio) => void
}

export const PortfolioCard: React.FC<PortfolioCardProps> = ({
  portfolio,
  onAnalyze,
  onDelete,
  isAnalyzing,
  onOpenModal,
}) => {
  const totalAllocation = portfolio.stocks?.reduce(
    (sum, stock) => sum + stock.allocation_percentage,
    0
  ) || 0

  const largestPosition = portfolio.stocks?.reduce((max, stock) =>
    stock.allocation_percentage > max.allocation_percentage ? stock : max
  ) || { symbol: 'N/A', allocation_percentage: 0 }

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

 type MuiColor = 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning';

  const getPortfolioTypeColor = (name: string): MuiColor => {
    const n = name.toLowerCase();
    if (n.includes('tech') || n.includes('innovation')) return 'primary';
    if (n.includes('dividend')) return 'success';
    if (n.includes('esg') || n.includes('sustainable')) return 'success';
    if (n.includes('etf') || n.includes('balanced')) return 'info';
    if (n.includes('fintech')) return 'secondary';
    return 'info'; // <— safe fallback
  };

  return (
    <Card 
      elevation={2}
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        '&:hover': {
          boxShadow: (theme) => theme.palette.mode === 'light'
            ? '0 8px 25px rgba(20, 184, 166, 0.15)'
            : '0 8px 25px rgba(20, 184, 166, 0.3)',
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
            <Paper elevation={0} sx={{ 
              bgcolor: (theme) => theme.palette.mode === 'light' ? 'grey.100' : 'grey.800', 
              px: 1, py: 0.5, borderRadius: 1 
            }}>
              <Typography variant="caption" color="text.secondary">
                Stocks: <strong>{portfolio.stocks?.length || 0}</strong>
              </Typography>
            </Paper>
            <Paper elevation={0} sx={{ 
              bgcolor: (theme) => theme.palette.mode === 'light' ? 'grey.100' : 'grey.800', 
              px: 1, py: 0.5, borderRadius: 1 
            }}>
              <Typography variant="caption" color="text.secondary">
                Allocation: <strong>{totalAllocation.toFixed(1)}%</strong>
              </Typography>
            </Paper>
          </Box>
          
          {largestPosition ? (
            <Typography variant="caption" color="text.secondary">
              Top holding: <strong>{largestPosition.symbol} ({largestPosition.allocation_percentage}%)</strong>
            </Typography>
          ) : (
            <Typography variant="caption" color="text.secondary">
              No holdings yet
            </Typography>
          )}
        </Box>

        {/* Stock Holdings */}
        <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <AccountBalanceIcon sx={{ fontSize: 16 }} />
          Holdings:
        </Typography>
        
        <Box sx={{ mb: 2, maxHeight: 120, overflowY: 'auto' }}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {(portfolio.stocks || [])
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
          onClick={() => onOpenModal ? onOpenModal(portfolio) : onAnalyze(portfolio)}
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