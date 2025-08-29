import React, { useState, useEffect, useRef } from 'react'
import { keyframes } from '@mui/system'
import { stockService, authService } from '../services/api'
import axios from 'axios'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Paper,
  IconButton,
  Chip,
  CircularProgress,
  Button,
  Avatar,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  Fade,
  Slide,
} from '@mui/material'
import {
  Close as CloseIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  ExpandMore as ExpandMoreIcon,
  Check as CheckIcon,
  Schedule as ScheduleIcon,
  Error as ErrorIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material'
import { TransitionProps } from '@mui/material/transitions'

interface Portfolio {
  id: number
  name: string
  description?: string
  stocks: Array<{
    symbol: string
    allocation_percentage: number
  }>
}

interface Agent {
  id: string
  name: string
  icon: string
  description: string
  status: 'pending' | 'analyzing' | 'completed' | 'error'
  analysis?: string
  processingTime?: number
}

interface AnalysisStep {
  id: string
  timestamp: Date
  type: 'user_message' | 'agent_start' | 'agent_complete' | 'system_message' | 'final_result'
  agentId?: string
  content: string
  analysis?: string
}

interface PortfolioAnalysisModalProps {
  open: boolean
  onClose: () => void
  portfolio: Portfolio | null
  timeFrequency: string
  isAnalyzing: boolean
  onStartAnalysis: () => void
}

const Transition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement<any, any>
  },
  ref: React.Ref<unknown>
) {
  return <Slide direction="up" ref={ref} {...props} />
})

const pulse = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
`

const agents: Agent[] = [
  {
    id: 'finance_guru',
    name: 'Finance Guru',
    icon: '🏦',
    description: 'Analyzing financial metrics, valuation, and market fundamentals',
    status: 'pending'
  },
  {
    id: 'geopolitics_guru', 
    name: 'Geopolitics Guru',
    icon: '🌍',
    description: 'Evaluating global events and geopolitical risks impact',
    status: 'pending'
  },
  {
    id: 'legal_guru',
    name: 'Legal Guru', 
    icon: '⚖️',
    description: 'Assessing regulatory compliance and legal risk factors',
    status: 'pending'
  },
  {
    id: 'quant_dev',
    name: 'Quant Dev',
    icon: '📊',
    description: 'Performing technical analysis and statistical modeling',
    status: 'pending'
  },
  {
    id: 'financial_analyst',
    name: 'Financial Analyst',
    icon: '📈', 
    description: 'Consolidating expert insights into final predictions',
    status: 'pending'
  }
]

export const PortfolioAnalysisModal: React.FC<PortfolioAnalysisModalProps> = ({
  open,
  onClose,
  portfolio,
  timeFrequency,
  isAnalyzing,
  onStartAnalysis
}) => {
  const [currentAgents, setCurrentAgents] = useState<Agent[]>(agents)
  const [analysisSteps, setAnalysisSteps] = useState<AnalysisStep[]>([])
  const [currentAgentIndex, setCurrentAgentIndex] = useState(-1)
  const [showFinalResult, setShowFinalResult] = useState(false)
  const [finalAnalysis, setFinalAnalysis] = useState<any>(null)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Auto scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [analysisSteps])

  // Real portfolio analysis API integration
  useEffect(() => {
    if (!isAnalyzing || !portfolio) return

    // Reset state
    setCurrentAgents(agents.map(agent => ({ ...agent, status: 'pending' })))
    setAnalysisSteps([])
    setCurrentAgentIndex(-1) 
    setShowFinalResult(false)
    setFinalAnalysis(null)
    setAnalysisError(null)

    // Add initial user message
    const initialMessage: AnalysisStep = {
      id: `msg-${Date.now()}`,
      timestamp: new Date(),
      type: 'user_message',
      content: `Please analyze my portfolio "${portfolio.name}" with ${portfolio.stocks.length} stocks for a ${timeFrequency} timeframe.`
    }
    setAnalysisSteps([initialMessage])

    // Add system message and start analysis immediately
    setTimeout(() => {
      const systemMessage: AnalysisStep = {
        id: `system-${Date.now()}`,
        timestamp: new Date(),
        type: 'system_message',
        content: `🤖 Starting comprehensive multi-agent portfolio analysis...`
      }
      setAnalysisSteps(prev => [...prev, systemMessage])

      // Show all agents as analyzing and call API
      setCurrentAgents(prev => prev.map(agent => ({ ...agent, status: 'analyzing' })))
      
      const analyzingMessage: AnalysisStep = {
        id: `analyzing-${Date.now()}`,
        timestamp: new Date(),
        type: 'system_message',
        content: `🔄 Our 5 AI experts are analyzing your portfolio. This may take 1-2 minutes...`
      }
      setAnalysisSteps(prev => [...prev, analyzingMessage])

      // Make API call
      runPortfolioAnalysis()
    }, 500)

    const runPortfolioAnalysis = async () => {
      try {
        // Use the existing API service with proper gateway routing
        let result
        if (portfolio.id) {
          // Portfolio is saved in database, use ID-based method
          result = await stockService.analyzePortfolio(portfolio.id, timeFrequency)
        } else {
          // Portfolio is not saved, make direct API call with portfolio data
          // Get user from auth service
          const user = await authService.getCurrentUser()
          
          // Create API gateway URL
          const API_GATEWAY_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
          
          // Make direct API call through gateway
          const response = await axios.post(`${API_GATEWAY_URL}/stock/analyze-portfolio`, {
            user_id: user.id,
            portfolio_data: portfolio.stocks.map(stock => ({
              symbol: stock.symbol,
              allocation: stock.allocation_percentage
            })),
            time_frequency: timeFrequency,
            analysis_type: 'portfolio'
          }, {
            headers: {
              'Content-Type': 'application/json',
            },
            withCredentials: true
          })
          
          result = response.data
        }
        
        // Analysis complete - update all agents to completed
        setCurrentAgents(prev => prev.map(agent => ({ ...agent, status: 'completed' })))
        
        // Store results and show completion
        setFinalAnalysis(result)
        setShowFinalResult(true)
        
        const completionMessage: AnalysisStep = {
          id: `complete-${Date.now()}`,
          timestamp: new Date(),
          type: 'final_result',
          content: `✅ Portfolio analysis complete! All 5 AI experts have finished their analysis. Confidence Score: ${(result.analysis_result?.confidence_score * 100).toFixed(1)}%`
        }
        setAnalysisSteps(prev => [...prev, completionMessage])

      } catch (error) {
        console.error('Portfolio analysis failed:', error)
        setAnalysisError(error instanceof Error ? error.message : 'Analysis failed')
        
        // Set all agents to error status
        setCurrentAgents(prev => prev.map(agent => ({ ...agent, status: 'error' })))
        
        const errorMessage: AnalysisStep = {
          id: `error-${Date.now()}`,
          timestamp: new Date(),
          type: 'system_message',
          content: `❌ Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`
        }
        setAnalysisSteps(prev => [...prev, errorMessage])
      }
    }
  }, [isAnalyzing, portfolio, timeFrequency])

  const getAgentStatus = (status: Agent['status']) => {
    switch (status) {
      case 'analyzing':
        return { color: 'primary', icon: <CircularProgress size={16} /> }
      case 'completed':
        return { color: 'success', icon: <CheckIcon fontSize="small" /> }
      case 'error':
        return { color: 'error', icon: <ErrorIcon fontSize="small" /> }
      default:
        return { color: 'default', icon: <ScheduleIcon fontSize="small" /> }
    }
  }

  const handleStartAnalysis = () => {
    onStartAnalysis()
  }

  const handleClose = () => {
    // Reset all state
    setCurrentAgents(agents.map(agent => ({ ...agent, status: 'pending' })))
    setAnalysisSteps([])
    setCurrentAgentIndex(-1)
    setShowFinalResult(false)
    setFinalAnalysis(null)
    setAnalysisError(null)
    onClose()
  }

  if (!portfolio) return null

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      TransitionComponent={Transition}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: '80vh', maxHeight: '800px' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TrendingUpIcon color="primary" />
          <Typography variant="h6">
            Portfolio Analysis: {portfolio.name}
          </Typography>
        </Box>
        <IconButton onClick={handleClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers sx={{ p: 0, display: 'flex', flexDirection: 'column', height: '100%' }}>
        {/* Portfolio Overview */}
        <Card sx={{ m: 2, mb: 1, bgcolor: 'primary.50' }}>
          <CardContent sx={{ py: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">
                  {portfolio.stocks.length} stocks • {timeFrequency} analysis
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {portfolio.stocks.map(s => `${s.symbol} (${s.allocation_percentage}%)`).join(', ')}
                </Typography>
              </Box>
              <Chip 
                label={isAnalyzing ? 'Analyzing...' : 'Ready'} 
                color={isAnalyzing ? 'primary' : 'default'}
                icon={isAnalyzing ? <CircularProgress size={16} /> : <AssessmentIcon />}
              />
            </Box>
          </CardContent>
        </Card>

        {/* Agent Status Panel */}
        <Card sx={{ m: 2, mt: 1, mb: 1 }}>
          <CardContent sx={{ py: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              AI Agent Status:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {currentAgents.map((agent, index) => {
                const status = getAgentStatus(agent.status)
                return (
                  <Chip
                    key={agent.id}
                    label={`${agent.icon} ${agent.name}`}
                    size="small"
                    variant={agent.status === 'analyzing' ? 'filled' : 'outlined'}
                    color={status.color as any}
                    icon={status.icon}
                    sx={{ 
                      transition: 'all 0.3s ease',
                      ...(agent.status === 'analyzing' && {
                        animation: `${pulse} 2s infinite`
                      })
                    }}
                  />
                )
              })}
            </Box>
          </CardContent>
        </Card>

        {/* Chat Messages */}
        <Box sx={{ 
          flexGrow: 1, 
          overflow: 'auto',
          px: 2,
          pb: 1
        }}>
          {analysisSteps.length === 0 && !isAnalyzing && (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center',
              color: 'text.secondary'
            }}>
              <BotIcon sx={{ fontSize: 64, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Ready to Analyze Portfolio
              </Typography>
              <Typography variant="body2" sx={{ mb: 3, maxWidth: 400 }}>
                Our 5 AI experts are ready to provide comprehensive analysis of your portfolio. 
                Click "Start Analysis" to begin the multi-agent assessment.
              </Typography>
              <Button
                variant="contained"
                size="large"
                startIcon={<TimelineIcon />}
                onClick={handleStartAnalysis}
                sx={{ px: 4 }}
              >
                Start Analysis
              </Button>
            </Box>
          )}

          {analysisSteps.map((step) => (
            <Fade in key={step.id} timeout={500}>
              <Box sx={{ mb: 2 }}>
                {step.type === 'user_message' && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                    <Paper 
                      sx={{ 
                        p: 2, 
                        bgcolor: 'primary.main', 
                        color: 'white',
                        maxWidth: '80%',
                        borderRadius: '18px 18px 4px 18px'
                      }}
                    >
                      <Typography variant="body2">{step.content}</Typography>
                      <Typography variant="caption" sx={{ opacity: 0.8, display: 'block', mt: 0.5 }}>
                        {step.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {step.type === 'system_message' && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                    <Paper sx={{ p: 1.5, bgcolor: 'grey.100', maxWidth: '90%' }}>
                      <Typography variant="body2" color="text.secondary" textAlign="center">
                        {step.content}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {(step.type === 'agent_start' || step.type === 'agent_complete') && (
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                      <BotIcon sx={{ fontSize: 18 }} />
                    </Avatar>
                    <Paper 
                      sx={{ 
                        p: 2, 
                        bgcolor: step.type === 'agent_complete' ? 'success.50' : 'grey.50',
                        maxWidth: '80%',
                        flexGrow: 1,
                        borderRadius: '4px 18px 18px 18px'
                      }}
                    >
                      <Typography variant="body2" sx={{ fontWeight: step.type === 'agent_complete' ? 'bold' : 'normal' }}>
                        {step.content}
                      </Typography>
                      {step.analysis && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                          {step.analysis}
                        </Typography>
                      )}
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                        {step.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {step.type === 'final_result' && (
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'success.main', width: 32, height: 32 }}>
                      <CheckIcon sx={{ fontSize: 18 }} />
                    </Avatar>
                    <Paper 
                      sx={{ 
                        p: 2, 
                        bgcolor: 'success.50',
                        border: '2px solid',
                        borderColor: 'success.main',
                        maxWidth: '80%',
                        flexGrow: 1,
                        borderRadius: '4px 18px 18px 18px'
                      }}
                    >
                      <Typography variant="body2" fontWeight="bold">
                        {step.content}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                        {step.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </Box>
                )}
              </Box>
            </Fade>
          ))}
          
          <div ref={chatEndRef} />
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button onClick={handleClose} variant="outlined">
          {showFinalResult ? 'Close' : 'Cancel'}
        </Button>
        {!isAnalyzing && analysisSteps.length === 0 && (
          <Button
            variant="contained"
            startIcon={<TimelineIcon />}
            onClick={handleStartAnalysis}
          >
            Start Analysis
          </Button>
        )}
        {showFinalResult && (
          <Button
            variant="contained"
            startIcon={<AssessmentIcon />}
            onClick={() => {
              // Create a new window with detailed results
              if (finalAnalysis) {
                const newWindow = window.open('', '_blank')
                if (newWindow) {
                  const htmlContent = `
                    <html>
                      <head><title>Portfolio Analysis Results - ${portfolio?.name}</title></head>
                      <body style="font-family: Arial, sans-serif; padding: 20px; max-width: 1200px; margin: 0 auto;">
                        <h1>📊 Portfolio Analysis: ${portfolio?.name}</h1>
                        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                          <h3>Summary</h3>
                          <p><strong>Confidence Score:</strong> ${(finalAnalysis.analysis_result?.confidence_score * 100).toFixed(1)}%</p>
                          <p><strong>Analysis Time:</strong> ${new Date().toLocaleString()}</p>
                          <p><strong>Portfolio:</strong> ${portfolio?.stocks.map(s => `${s.symbol} (${s.allocation_percentage}%)`).join(', ')}</p>
                        </div>
                        
                        ${['finance_analysis', 'geopolitics_analysis', 'legal_analysis', 'quant_analysis', 'final_analysis'].map(key => {
                          const analysis = finalAnalysis[key]
                          if (!analysis) return ''
                          return `
                            <div style="margin: 30px 0; border-left: 4px solid #1976d2; padding-left: 20px;">
                              <h2>${analysis.agent_name}</h2>
                              <p><strong>Confidence:</strong> ${(analysis.confidence * 100).toFixed(1)}%</p>
                              <p><strong>Processing Time:</strong> ${analysis.processing_time_ms}ms</p>
                              <p><strong>Key Factors:</strong> ${analysis.key_factors.join(', ')}</p>
                              <div style="background: white; padding: 15px; border-radius: 4px; margin-top: 10px;">
                                ${analysis.analysis.replace(/\n/g, '<br>')}
                              </div>
                            </div>
                          `
                        }).join('')}
                        
                        <div style="margin-top: 40px; text-align: center; color: #666;">
                          Generated by Stock AI Analysis Service
                        </div>
                      </body>
                    </html>
                  `
                  newWindow.document.open()
                  newWindow.document.write(htmlContent)
                  newWindow.document.close()
                }
              }
            }}
          >
            View Detailed Results
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}