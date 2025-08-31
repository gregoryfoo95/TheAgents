import {
    Add as AddIcon,
    Delete as DeleteIcon,
} from '@mui/icons-material'
import {
    Alert,
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Divider,
    IconButton,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography
} from '@mui/material'
import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { PortfolioStock, usePortfolio } from '../hooks'

interface PortfolioFormProps {
  open: boolean
  onClose: () => void
  onSuccess?: () => void
}

export const PortfolioForm: React.FC<PortfolioFormProps> = ({ open, onClose, onSuccess }) => {
  const { createPortfolio, isCreating, createError } = usePortfolio()
  
  const [portfolioName, setPortfolioName] = useState('')
  const [description, setDescription] = useState('')
  const [stocks, setStocks] = useState<Omit<PortfolioStock, 'id' | 'created_at'>[]>([
    { symbol: '', allocation_percentage: 0, shares: undefined, purchase_price: undefined }
  ])
  
  const [errors, setErrors] = useState<{[key: string]: string}>({})

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {}
    
    if (!portfolioName.trim()) {
      newErrors.name = 'Portfolio name is required'
    }
    
    if (stocks.length === 0) {
      newErrors.stocks = 'At least one stock is required'
      return newErrors
    }
    
    let totalAllocation = 0
    stocks.forEach((stock, index) => {
      if (!stock.symbol.trim()) {
        newErrors[`stock_${index}_symbol`] = 'Stock symbol is required'
      }
      if (stock.allocation_percentage <= 0 || stock.allocation_percentage > 100) {
        newErrors[`stock_${index}_allocation`] = 'Allocation must be between 0.01 and 100'
      }
      totalAllocation += stock.allocation_percentage
    })
    
    if (Math.abs(totalAllocation - 100) > 1) {
      newErrors.totalAllocation = `Total allocation must equal 100% (currently ${totalAllocation.toFixed(2)}%)`
    }
    
    setErrors(newErrors)
    return newErrors
  }

  const handleAddStock = () => {
    setStocks([...stocks, { symbol: '', allocation_percentage: 0, shares: undefined, purchase_price: undefined }])
  }

  const handleRemoveStock = (index: number) => {
    if (stocks.length > 1) {
      setStocks(stocks.filter((_, i) => i !== index))
    }
  }

  const handleStockChange = (index: number, field: keyof PortfolioStock, value: string | number) => {
    const updatedStocks = stocks.map((stock, i) => 
      i === index ? { ...stock, [field]: value } : stock
    )
    setStocks(updatedStocks)
    
    // Clear field-specific errors when user starts typing
    if (errors[`stock_${index}_${field}`]) {
      const newErrors = { ...errors }
      delete newErrors[`stock_${index}_${field}`]
      setErrors(newErrors)
    }
  }

  const handleSubmit = async () => {
    const validationErrors = validateForm()
    
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    try {
      await createPortfolio.mutateAsync({
        name: portfolioName.trim(),
        description: description.trim() || undefined,
        stocks: stocks.map(stock => ({
          ...stock,
          symbol: stock.symbol.toUpperCase(),
          shares: stock.shares || undefined,
          purchase_price: stock.purchase_price || undefined
        }))
      })
      
      toast.success('Portfolio created successfully!')
      handleClose()
      onSuccess?.()
    } catch (err) {
      toast.error('Failed to create portfolio')
    }
  }

  const handleClose = () => {
    setPortfolioName('')
    setDescription('')
    setStocks([{ symbol: '', allocation_percentage: 0, shares: undefined, purchase_price: undefined }])
    setErrors({})
    onClose()
  }

  const totalAllocation = stocks.reduce((sum, stock) => sum + (stock.allocation_percentage || 0), 0)

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Portfolio</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 3, mt: 1 }}>
          <TextField
            fullWidth
            label="Portfolio Name"
            value={portfolioName}
            onChange={(e) => setPortfolioName(e.target.value)}
            error={!!errors.name}
            helperText={errors.name}
            sx={{ mb: 2 }}
          />
          
          <TextField
            fullWidth
            label="Description (Optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={2}
            sx={{ mb: 3 }}
          />
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Portfolio Stocks</Typography>
          <Button
            startIcon={<AddIcon />}
            onClick={handleAddStock}
            variant="outlined"
            size="small"
          >
            Add Stock
          </Button>
        </Box>

        <TableContainer 
          component={Paper} 
          sx={{ 
            mb: 2,
            bgcolor: (theme) => theme.palette.mode === 'light' 
              ? 'background.paper' 
              : 'background.paper',
            border: (theme) => `1px solid ${theme.palette.divider}`
          }}
        >
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Stock Symbol</TableCell>
                <TableCell>Allocation %</TableCell>
                <TableCell>Shares (Optional)</TableCell>
                <TableCell>Purchase Price (Optional)</TableCell>
                <TableCell width={60}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {stocks.map((stock, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <TextField
                      size="small"
                      value={stock.symbol}
                      onChange={(e) => handleStockChange(index, 'symbol', e.target.value.toUpperCase())}
                      placeholder="e.g., AAPL"
                      error={!!errors[`stock_${index}_symbol`]}
                      helperText={errors[`stock_${index}_symbol`]}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={stock.allocation_percentage}
                      onChange={(e) => handleStockChange(index, 'allocation_percentage', parseFloat(e.target.value) || 0)}
                      inputProps={{ min: 0.01, max: 100, step: 0.01 }}
                      error={!!errors[`stock_${index}_allocation`]}
                      helperText={errors[`stock_${index}_allocation`]}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={stock.shares || ''}
                      onChange={(e) => handleStockChange(index, 'shares', parseFloat(e.target.value) || undefined)}
                      inputProps={{ min: 0, step: 0.0001 }}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={stock.purchase_price || ''}
                      onChange={(e) => handleStockChange(index, 'purchase_price', parseFloat(e.target.value) || undefined)}
                      inputProps={{ min: 0, step: 0.01 }}
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleRemoveStock(index)}
                      disabled={stocks.length <= 1}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Total Allocation: {totalAllocation.toFixed(2)}%
          </Typography>
          <Typography 
            variant="body2" 
            color={Math.abs(totalAllocation - 100) <= 1 ? 'success.main' : 'error.main'}
          >
            {Math.abs(totalAllocation - 100) <= 1 ? '✓ Balanced' : '⚠ Must equal 100%'}
          </Typography>
        </Box>

        {errors.totalAllocation && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {errors.totalAllocation}
          </Alert>
        )}

        {errors.stocks && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {errors.stocks}
          </Alert>
        )}

        {createError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {createError.message || 'Failed to create portfolio'}
          </Alert>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          disabled={isCreating}
        >
          {isCreating ? 'Creating...' : 'Create Portfolio'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}