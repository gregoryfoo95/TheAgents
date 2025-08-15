import React, { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Paper,
  Chip,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Fab,
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Add as AddIcon,
  PlayArrow as PlayArrowIcon,
  Delete as DeleteIcon,
  Folder as FolderIcon,
} from '@mui/icons-material'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useStockAnalysis } from '../hooks/useStockAnalysis'
import { usePortfolio, Portfolio } from '../hooks/usePortfolio'
import { useAuth } from '../contexts/AuthContext'
import { PortfolioForm } from '../components/PortfolioForm'
import toast from 'react-hot-toast'

interface StockPrediction {
  symbol: string
  prediction: {
    time_frequency: string
    predictions: Array<{
      date: string
      price: number
    }>
  }
  analysis: {
    finance_guru: string
    geopolitics_guru: string
    legal_guru: string
    quant_dev: string
    financial_analyst: string
  }
  confidence_score: number
  workflow_id: string
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`stock-tabpanel-${index}`}
      aria-labelledby={`stock-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export const StockPredictorPage: React.FC = () => {
  const { user } = useAuth()
  const {
    createAnalysis,
    analysisStatus,
    getAnalysisDetails,
    getSupportedSymbols,
    getTimeFrequencies,
    isCreating,
    createError,
    isPolling,
    stopPolling
  } = useStockAnalysis()

  const {
    portfolios,
    analyzePortfolio,
    deletePortfolio,
    isAnalyzing,
    isPolling: isPortfolioPolling,
    analysisStatus: portfolioAnalysisStatus,
    getAnalysisResults
  } = usePortfolio()

  const [stockSymbol, setStockSymbol] = useState('')
  const [timeFrequency, setTimeFrequency] = useState('1M')
  const [prediction, setPrediction] = useState<StockPrediction | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [tabValue, setTabValue] = useState(0)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null)
  const [showPortfolioForm, setShowPortfolioForm] = useState(false)
  
  const supportedSymbols = getSupportedSymbols.data
  const timeFrequencies = getTimeFrequencies.data

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handlePortfolioAnalysis = async (portfolio: Portfolio) => {
    if (!user) {
      setError('Please log in to analyze portfolios')
      toast.error('Please log in first')
      return
    }

    setError(null)
    setPrediction(null)
    setSelectedPortfolio(portfolio)
    
    try {
      await analyzePortfolio.mutateAsync({
        portfolio_id: portfolio.id,
        time_frequency: timeFrequency,
        analysis_type: 'portfolio'
      })
      
      toast.success(`Analysis started for ${portfolio.name}! This may take a few moments...`)
      setTabValue(2) // Switch to results tab
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      toast.error('Failed to start portfolio analysis')
    }
  }

  const handleDeletePortfolio = async (portfolioId: number, portfolioName: string) => {
    if (window.confirm(`Are you sure you want to delete "${portfolioName}"? This action cannot be undone.`)) {
      try {
        await deletePortfolio.mutateAsync(portfolioId)
        toast.success('Portfolio deleted successfully')
      } catch (err) {
        toast.error('Failed to delete portfolio')
      }
    }
  }

  // Handle analysis status updates
  useEffect(() => {
    if (analysisStatus.data) {
      const status = analysisStatus.data.status
      
      if (status === 'completed') {
        // Analysis completed, fetch full results
        if (currentSessionId) {
          const analysisQuery = getAnalysisDetails(currentSessionId)
          analysisQuery.refetch().then((result) => {
            if (result.data) {
              // Convert to prediction format - handle new microservice response
              const analysisData = result.data
              const predictionData: StockPrediction = {
                symbol: analysisData.stock_symbol,
                prediction: {
                  time_frequency: analysisData.time_frequency,
                  predictions: analysisData.predictions || []
                },
                analysis: analysisData.agent_analyses?.reduce((acc: any, analysis: any) => {
                  acc[analysis.agent_type] = analysis.analysis_text
                  return acc
                }, {}) || {},
                confidence_score: analysisData.confidence_score || 0,
                workflow_id: analysisData.workflow_id || analysisData.session_id
              }
              setPrediction(predictionData)
              setTabValue(1) // Switch to results tab
              stopPolling()
              toast.success('Stock analysis completed!')
            }
          })
        }
      } else if (status === 'failed') {
        setError('Analysis failed. Please try again.')
        stopPolling()
        toast.error('Stock analysis failed')
      }
    }
  }, [analysisStatus.data, currentSessionId, getAnalysisDetails, stopPolling])

  // Handle create analysis errors
  useEffect(() => {
    if (createError) {
      setError(createError.message || 'Failed to start analysis')
      toast.error('Failed to start stock analysis')
    }
  }, [createError])

  const handlePredict = async () => {
    if (!user) {
      setError('Please log in to use stock analysis')
      toast.error('Please log in first')
      return
    }

    if (!stockSymbol.trim()) {
      setError('Please enter a stock symbol')
      return
    }

    setError(null)
    setPrediction(null)
    
    try {
      const result = await createAnalysis.mutateAsync({
        symbol: stockSymbol.toUpperCase(),
        time_frequency: timeFrequency,
      })
      
      setCurrentSessionId(result.session_id)
      toast.success('Analysis started! This may take a few moments...')
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const frequencyOptions = timeFrequencies?.frequencies || [
    { label: '1 Day', value: '1D' },
    { label: '1 Week', value: '1W' },
    { label: '1 Month', value: '1M' },
    { label: '3 Months', value: '3M' },
    { label: '6 Months', value: '6M' },
    { label: '1 Year', value: '1Y' },
  ]

  // Show current analysis status
  const currentStatus = analysisStatus.data?.status
  const currentStep = analysisStatus.data?.current_step

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          sx={{ display: 'flex', alignItems: 'center', gap: 2 }}
        >
          <TrendingUpIcon fontSize="large" color="primary" />
          Stock Market Predictor
        </Typography>
        <Typography variant="h6" color="text.secondary" paragraph>
          Get AI-powered stock predictions using multi-agent analysis from Finance, Geopolitics, Legal, and Quantitative experts
        </Typography>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            label="Portfolios"
            icon={<FolderIcon />}
            iconPosition="start"
            id="portfolio-tab-0"
          />
          <Tab
            label="Single Stock"
            icon={<SearchIcon />}
            iconPosition="start"
            id="stock-tab-1"
          />
          <Tab
            label="Results"
            icon={<AssessmentIcon />}
            iconPosition="start"
            id="results-tab-2"
            disabled={!prediction}
          />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {/* Portfolio Management Tab */}
        <Grid container spacing={4}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5">Your Portfolios</Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowPortfolioForm(true)}
              >
                Create Portfolio
              </Button>
            </Box>

            {portfolios.isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : portfolios.data && portfolios.data.length > 0 ? (
              <Grid container spacing={3}>
                {portfolios.data.map((portfolio) => (
                  <Grid item xs={12} md={6} key={portfolio.id}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                          <Typography variant="h6">{portfolio.name}</Typography>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeletePortfolio(portfolio.id, portfolio.name)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                        
                        {portfolio.description && (
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {portfolio.description}
                          </Typography>
                        )}

                        <Typography variant="subtitle2" sx={{ mb: 1 }}>
                          Holdings ({portfolio.stocks.length} stocks):
                        </Typography>
                        
                        <Box sx={{ mb: 2 }}>
                          {portfolio.stocks.map((stock, index) => (
                            <Chip
                              key={index}
                              label={`${stock.symbol} (${stock.allocation_percentage}%)`}
                              size="small"
                              sx={{ mr: 1, mb: 1 }}
                              variant="outlined"
                            />
                          ))}
                        </Box>

                        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                          <Button
                            variant="contained"
                            size="small"
                            startIcon={<PlayArrowIcon />}
                            onClick={() => handlePortfolioAnalysis(portfolio)}
                            disabled={isAnalyzing}
                            fullWidth
                          >
                            {isAnalyzing ? 'Analyzing...' : 'Analyze Portfolio'}
                          </Button>
                        </Box>
                        
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                          Created: {new Date(portfolio.created_at).toLocaleDateString()}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <FolderIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Portfolios Yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Create your first portfolio to start analyzing multiple stocks together with our AI agents.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowPortfolioForm(true)}
                >
                  Create Your First Portfolio
                </Button>
              </Paper>
            )}
          </Grid>
        </Grid>

        {/* Time Frequency Selection for Portfolio Analysis */}
        <Box sx={{ mt: 4 }}>
          <Card sx={{ bgcolor: 'primary.50' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                Analysis Settings
              </Typography>
              
              <Typography variant="subtitle2" gutterBottom>
                Prediction Time Frame
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                {frequencyOptions.map((option) => (
                  <Chip
                    key={option.value}
                    label={option.label}
                    onClick={() => setTimeFrequency(option.value)}
                    color={timeFrequency === option.value ? 'primary' : 'default'}
                    variant={timeFrequency === option.value ? 'filled' : 'outlined'}
                  />
                ))}
              </Box>

              <Typography variant="body2" color="text.secondary">
                Portfolio analysis uses the same 5 AI agents but considers the interactions and correlations between all stocks in your portfolio for more comprehensive insights.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {/* Single Stock Analysis Tab */}
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Stock Analysis Request
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <TextField
                    fullWidth
                    label="Stock Symbol"
                    placeholder="e.g., AAPL, GOOGL, TSLA"
                    value={stockSymbol}
                    onChange={(e) => setStockSymbol(e.target.value.toUpperCase())}
                    sx={{ mb: 2 }}
                    disabled={isCreating || isPolling}
                  />
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Prediction Time Frame
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 3 }}>
                    {frequencyOptions.map((option) => (
                      <Chip
                        key={option.value}
                        label={option.label}
                        onClick={() => setTimeFrequency(option.value)}
                        color={timeFrequency === option.value ? 'primary' : 'default'}
                        variant={timeFrequency === option.value ? 'filled' : 'outlined'}
                        disabled={isCreating || isPolling}
                      />
                    ))}
                  </Box>

                  {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      {error}
                    </Alert>
                  )}

                  {(isCreating || isPolling) && (
                    <Box sx={{ mb: 2 }}>
                      <Alert severity="info" sx={{ mb: 1 }}>
                        {isCreating ? 'Starting analysis...' : 
                         currentStatus === 'processing' ? `Processing: ${currentStep || 'Running agents'}` :
                         'Analysis in progress...'}
                      </Alert>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={16} />
                        <Typography variant="body2" color="text.secondary">
                          This may take 1-2 minutes
                        </Typography>
                      </Box>
                    </Box>
                  )}

                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    onClick={handlePredict}
                    disabled={isCreating || isPolling || !stockSymbol.trim()}
                    startIcon={(isCreating || isPolling) ? <CircularProgress size={20} /> : <TrendingUpIcon />}
                  >
                    {isCreating ? 'Starting Analysis...' : 
                     isPolling ? 'Analyzing...' : 
                     'Get AI Prediction'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ bgcolor: 'primary.50' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary">
                  How It Works
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" paragraph>
                    Our AI system uses multiple specialized agents to analyze your stock:
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Chip label="🏦 Finance Guru - Market & Financial Analysis" variant="outlined" size="small" />
                    <Chip label="🌍 Geopolitics Guru - Global Events Impact" variant="outlined" size="small" />
                    <Chip label="⚖️ Legal Guru - Regulatory & Compliance" variant="outlined" size="small" />
                    <Chip label="📊 Quant Dev - Technical Analysis" variant="outlined" size="small" />
                    <Chip label="📈 Financial Analyst - Final Consolidation" variant="outlined" size="small" />
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary">
                  Each agent provides specialized insights that are then consolidated into a comprehensive prediction with confidence scores and detailed analysis.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {prediction && (
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h5">
                      {prediction.symbol} Prediction
                    </Typography>
                    <Chip 
                      label={`Confidence: ${(prediction.confidence_score * 100).toFixed(1)}%`}
                      color={prediction.confidence_score > 0.7 ? 'success' : prediction.confidence_score > 0.5 ? 'warning' : 'error'}
                      variant="filled"
                    />
                  </Box>

                  <Box sx={{ height: 400, mb: 3 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={prediction.prediction.predictions}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="date" 
                          tick={{ fontSize: 12 }}
                          angle={-45}
                          textAnchor="end"
                          height={80}
                        />
                        <YAxis 
                          tick={{ fontSize: 12 }}
                          domain={['dataMin - 5', 'dataMax + 5']}
                        />
                        <Tooltip 
                          formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
                          labelStyle={{ color: '#000' }}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="price" 
                          stroke="#1976d2" 
                          strokeWidth={2}
                          dot={{ r: 4 }}
                          activeDot={{ r: 6 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>

                  <Typography variant="body2" color="text.secondary">
                    Time Frequency: {prediction.prediction.time_frequency} | 
                    Workflow ID: {prediction.workflow_id}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Agent Analysis
              </Typography>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>🏦 Finance Guru Analysis</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    {prediction.analysis.finance_guru}
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>🌍 Geopolitics Guru Analysis</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    {prediction.analysis.geopolitics_guru}
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>⚖️ Legal Guru Analysis</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    {prediction.analysis.legal_guru}
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>📊 Quant Dev Analysis</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    {prediction.analysis.quant_dev}
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>📈 Financial Analyst Summary</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    {prediction.analysis.financial_analyst}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      {/* Portfolio Form Dialog */}
      <PortfolioForm
        open={showPortfolioForm}
        onClose={() => setShowPortfolioForm(false)}
        onSuccess={() => {
          setShowPortfolioForm(false)
          portfolios.refetch()
        }}
      />
    </Container>
  )
}