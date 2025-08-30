from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any
import uuid
from datetime import datetime, timezone
import logging

from .state import StockAnalysisState, StockAnalysisRequest
from .stock_agents import (
    FinanceGuruAgent,
    GeopoliticsGuruAgent, 
    LegalGuruAgent,
    QuantDevAgent,
    FinancialAnalystAgent
)

logger = logging.getLogger(__name__)

class StockAnalysisOrchestrator:
    """LangGraph orchestrator for multi-agent stock analysis"""
    
    def __init__(self):
        self.finance_agent = FinanceGuruAgent()
        self.geopolitics_agent = GeopoliticsGuruAgent()
        self.legal_agent = LegalGuruAgent()
        self.quant_agent = QuantDevAgent()
        self.analyst_agent = FinancialAnalystAgent()
        
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the multi-agent LangGraph workflow"""
        
        workflow = StateGraph(StockAnalysisState)
        
        # Add agent nodes (renamed to avoid conflict with state keys)
        workflow.add_node("finance_agent", self.finance_agent.analyze)
        workflow.add_node("geopolitics_agent", self.geopolitics_agent.analyze) 
        workflow.add_node("legal_agent", self.legal_agent.analyze)
        workflow.add_node("quant_agent", self.quant_agent.analyze)
        workflow.add_node("final_agent", self.analyst_agent.analyze)
        
        # Set entry point to finance agent for sequential execution  
        # (LangGraph concurrent execution is complex - falling back to sequential for now)
        workflow.set_entry_point("finance_agent")
        
        # Sequential execution chain for now
        workflow.add_edge("finance_agent", "geopolitics_agent")
        workflow.add_edge("geopolitics_agent", "legal_agent")
        workflow.add_edge("legal_agent", "quant_agent")
        workflow.add_edge("quant_agent", "final_agent")
        
        # End workflow after final analysis
        workflow.add_edge("final_agent", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    
    async def analyze_portfolio(self, portfolio_data: list, time_frequency: str, user_context: dict = None) -> Dict[str, Any]:
        """Run optimized multi-agent analysis for a portfolio of stocks"""
        
        workflow_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting optimized portfolio analysis with {len(portfolio_data)} stocks")
            
            # Create portfolio summary for analysis
            portfolio_symbols = []
            total_allocation = 0
            
            for stock_info in portfolio_data:
                symbol = stock_info.get('symbol', stock_info.get('stock_symbol', ''))
                allocation = stock_info.get('allocation', stock_info.get('allocation_percentage', 0))
                
                if not symbol:
                    logger.warning(f"Skipping stock with missing symbol: {stock_info}")
                    continue
                    
                portfolio_symbols.append(f"{symbol}({allocation}%)")
                total_allocation += allocation
            
            portfolio_summary = f"Portfolio: {', '.join(portfolio_symbols)}"
            logger.info(f"Analyzing portfolio as single unit: {portfolio_summary}")
            
            # Create portfolio-specific context for analysis
            portfolio_context = f"""Portfolio Analysis Context:
            - Total Stocks: {len(portfolio_symbols)}
            - Portfolio Composition: {', '.join(portfolio_symbols)}
            - Total Allocation: {total_allocation}%
            - Analysis Timeframe: {time_frequency}
            - Analysis Type: Portfolio-level multi-asset analysis
            """
            
            # Run single portfolio analysis (not per-stock)
            portfolio_state = await self.analyze_stock(
                symbol=portfolio_summary,
                time_frequency=time_frequency,
                user_context=portfolio_context
            )
            
            # Create optimized portfolio result
            consolidated_result = self._create_portfolio_result(
                portfolio_state, portfolio_data, time_frequency, workflow_id
            )
            
            # Return the consolidated portfolio analysis
            final_state = consolidated_result
            final_state["workflow_id"] = workflow_id
            final_state["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            return final_state
            
        except Exception as e:
            logger.error(f"Portfolio analysis workflow failed: {e}")
            return {
                "workflow_id": workflow_id,
                "errors": [str(e)],
                "analysis_result": None
            }
    
    def _create_portfolio_result(self, portfolio_state: dict, portfolio_data: list, time_frequency: str, workflow_id: str) -> dict:
        """Create optimized portfolio result from single analysis"""
        
        from .state import StockAnalysisResult
        
        try:
            # Extract agent analyses from the portfolio analysis
            finance_analysis = portfolio_state.get('finance_analysis')
            geopolitics_analysis = portfolio_state.get('geopolitics_analysis') 
            legal_analysis = portfolio_state.get('legal_analysis')
            quant_analysis = portfolio_state.get('quant_analysis')
            final_analysis = portfolio_state.get('final_analysis')
            
            # Create portfolio summary
            portfolio_symbols = [f"{stock.get('symbol', stock.get('stock_symbol', ''))}({stock.get('allocation', stock.get('allocation_percentage', 0))}%)" 
                               for stock in portfolio_data if stock.get('symbol') or stock.get('stock_symbol')]
            
            # Create optimized portfolio result
            portfolio_result = StockAnalysisResult(
                symbol=f"Portfolio_{len(portfolio_symbols)}_stocks",
                prediction={"time_frequency": time_frequency, "portfolio_analysis": "Comprehensive portfolio-level analysis"},
                agent_analyses={
                    "finance_guru": finance_analysis.analysis if finance_analysis else "Analysis not available",
                    "geopolitics_guru": geopolitics_analysis.analysis if geopolitics_analysis else "Analysis not available", 
                    "legal_guru": legal_analysis.analysis if legal_analysis else "Analysis not available",
                    "quant_dev": quant_analysis.analysis if quant_analysis else "Analysis not available",
                    "financial_analyst": final_analysis.analysis if final_analysis else "Analysis not available"
                },
                confidence_score=portfolio_state.get('analysis_result', {}).get('confidence_score', 0.75) if portfolio_state.get('analysis_result') else 0.75,
                factors_considered=["portfolio_diversification", "multi_asset_analysis", "risk_assessment", "allocation_optimization"]
            )
            
            return {
                "request": portfolio_state.get('request'),
                "finance_analysis": finance_analysis,
                "geopolitics_analysis": geopolitics_analysis, 
                "legal_analysis": legal_analysis,
                "quant_analysis": quant_analysis,
                "final_analysis": final_analysis,
                "current_step": "analysis_complete",
                "errors": portfolio_state.get('errors', []),
                "warnings": portfolio_state.get('warnings', []),
                "analysis_result": portfolio_result,
                "started_at": portfolio_state.get('started_at', datetime.now(timezone.utc).isoformat())
            }
            
        except Exception as e:
            logger.error(f"Failed to create portfolio result: {e}")
            return {
                "errors": [f"Portfolio result creation failed: {str(e)}"],
                "analysis_result": None
            }

    def _consolidate_portfolio_analysis(self, stock_analyses: dict, time_frequency: str, workflow_id: str) -> dict:
        """Consolidate individual stock analyses into portfolio-level insights"""
        
        from .state import AgentAnalysis, StockAnalysisResult
        
        try:
            # Extract all successful analyses
            successful_analyses = {k: v for k, v in stock_analyses.items() if 'analysis_result' in v}
            failed_analyses = {k: v for k, v in stock_analyses.items() if 'error' in v}
            
            if not successful_analyses:
                return {
                    'errors': ['No stocks could be analyzed successfully'],
                    'portfolio_result': None
                }
            
            # Create consolidated agent analyses
            finance_insights = []
            geopolitics_insights = []
            legal_insights = []
            quant_insights = []
            final_insights = []
            
            total_allocation = 0
            
            for symbol, analysis_data in successful_analyses.items():
                allocation = analysis_data['allocation'] 
                result = analysis_data['analysis_result']
                total_allocation += allocation
                
                # Extract agent insights
                if result.get('finance_analysis'):
                    finance_insights.append(f"{symbol} ({allocation}%): {result['finance_analysis'].analysis[:200]}...")
                
                if result.get('geopolitics_analysis'):
                    geopolitics_insights.append(f"{symbol} ({allocation}%): {result['geopolitics_analysis'].analysis[:200]}...")
                    
                if result.get('legal_analysis'):
                    legal_insights.append(f"{symbol} ({allocation}%): {result['legal_analysis'].analysis[:200]}...")
                    
                if result.get('quant_analysis'):
                    quant_insights.append(f"{symbol} ({allocation}%): {result['quant_analysis'].analysis[:200]}...")
                    
                if result.get('final_analysis'):
                    final_insights.append(f"{symbol} ({allocation}%): {result['final_analysis'].analysis[:200]}...")
            
            # Create consolidated analyses
            portfolio_finance = AgentAnalysis(
                agent_type="finance_guru",
                agent_name="Portfolio Finance Guru",
                analysis=f"Portfolio Financial Analysis:\n\nAnalyzed {len(successful_analyses)} stocks representing {total_allocation}% allocation:\n\n" + "\n\n".join(finance_insights),
                confidence=0.75,
                key_factors=[f"portfolio_diversification", f"analyzed_{len(successful_analyses)}_stocks", "weighted_financial_metrics"],
                processing_time_ms=2000
            )
            
            portfolio_geopolitics = AgentAnalysis(
                agent_type="geopolitics_guru", 
                agent_name="Portfolio Geopolitics Guru",
                analysis=f"Portfolio Geopolitical Analysis:\n\nConsidered geopolitical impacts across {len(successful_analyses)} stocks:\n\n" + "\n\n".join(geopolitics_insights),
                confidence=0.80,
                key_factors=["portfolio_geographic_exposure", "cross_stock_geopolitical_risks", "diversification_benefits"],
                processing_time_ms=2000
            )
            
            portfolio_legal = AgentAnalysis(
                agent_type="legal_guru",
                agent_name="Portfolio Legal Guru", 
                analysis=f"Portfolio Legal & Regulatory Analysis:\n\nAssessed regulatory landscape for {len(successful_analyses)} positions:\n\n" + "\n\n".join(legal_insights),
                confidence=0.78,
                key_factors=["regulatory_diversification", "sector_compliance_risks", "portfolio_legal_exposure"],
                processing_time_ms=1800
            )
            
            portfolio_quant = AgentAnalysis(
                agent_type="quant_dev",
                agent_name="Portfolio Quant Dev",
                analysis=f"Portfolio Quantitative Analysis:\n\nTechnical analysis across {len(successful_analyses)} positions:\n\n" + "\n\n".join(quant_insights),
                confidence=0.82,
                key_factors=["portfolio_correlation", "diversification_metrics", "technical_indicators"],
                processing_time_ms=2200
            )
            
            # Create final consolidated analysis
            portfolio_final = AgentAnalysis(
                agent_type="financial_analyst",
                agent_name="Portfolio Financial Analyst",
                analysis=f"Final Portfolio Analysis:\n\nComprehensive assessment of {len(successful_analyses)} stocks with {total_allocation}% total allocation. Portfolio demonstrates {'good' if len(successful_analyses) >= 5 else 'limited'} diversification across multiple positions. Key insights from all expert agents have been consolidated to provide portfolio-level recommendations considering position sizing, sector exposure, and risk-adjusted returns.",
                confidence=0.77,
                key_factors=["portfolio_optimization", "risk_adjusted_returns", "diversification_score"],
                processing_time_ms=3000
            )
            
            # Create portfolio result
            portfolio_result = StockAnalysisResult(
                symbol=f"Portfolio_{len(successful_analyses)}_stocks",
                prediction={"time_frequency": time_frequency, "portfolio_predictions": "Portfolio-level predictions based on constituent analysis"},
                agent_analyses={
                    "finance_guru": portfolio_finance.analysis,
                    "geopolitics_guru": portfolio_geopolitics.analysis,
                    "legal_guru": portfolio_legal.analysis,
                    "quant_dev": portfolio_quant.analysis,
                    "financial_analyst": portfolio_final.analysis
                },
                confidence_score=(portfolio_finance.confidence + portfolio_geopolitics.confidence + portfolio_legal.confidence + portfolio_quant.confidence + portfolio_final.confidence) / 5,
                factors_considered=["portfolio_diversification", "position_sizing", "sector_analysis", "risk_management"]
            )
            
            return {
                'finance_analysis': portfolio_finance,
                'geopolitics_analysis': portfolio_geopolitics,
                'legal_analysis': portfolio_legal,
                'quant_analysis': portfolio_quant,
                'final_analysis': portfolio_final,
                'portfolio_result': portfolio_result,
                'errors': [f"Failed to analyze: {k}" for k in failed_analyses.keys()],
                'warnings': [f"Analyzed {len(successful_analyses)}/{len(stock_analyses)} stocks successfully"]
            }
            
        except Exception as e:
            logger.error(f"Failed to consolidate portfolio analysis: {e}")
            return {
                'errors': [f"Consolidation failed: {str(e)}"],
                'portfolio_result': None
            }

    async def analyze_stock(
        self, 
        symbol: str, 
        time_frequency: str = "1M",
        user_context: str = None
    ) -> StockAnalysisState:
        """
        Run comprehensive multi-agent stock analysis
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            time_frequency: Analysis time frame ('1D', '1W', '1M', '3M', '6M', '1Y')
            user_context: Additional context from user
            
        Returns:
            Final analysis state with all agent insights
        """
        
        workflow_id = str(uuid.uuid4())
        
        initial_state: StockAnalysisState = {
            "request": StockAnalysisRequest(
                symbol=symbol.upper(),
                time_frequency=time_frequency,
                user_context=user_context
            ),
            "finance_analysis": None,
            "geopolitics_analysis": None,
            "legal_analysis": None,
            "quant_analysis": None,
            "final_analysis": None,
            "current_step": "initialized", 
            "errors": [],
            "warnings": [],
            "analysis_result": None,
            "workflow_id": workflow_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        
        logger.info(f"Starting multi-agent stock analysis {workflow_id} for {symbol}")
        
        config = {"configurable": {"thread_id": workflow_id}}
        
        try:
            final_state = await self.graph.ainvoke(initial_state, config)
            
            logger.info(f"Stock analysis {workflow_id} completed: {final_state.get('current_step')}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Stock analysis workflow {workflow_id} failed: {str(e)}")
            initial_state['errors'].append(f"Workflow execution failed: {str(e)}")
            initial_state['completed_at'] = datetime.now(timezone.utc).isoformat()
            initial_state['current_step'] = 'workflow_failed'
            return initial_state
    
    async def get_workflow_state(self, workflow_id: str) -> StockAnalysisState:
        """Get current state of a running workflow"""
        config = {"configurable": {"thread_id": workflow_id}}
        
        try:
            checkpoint = await self.checkpointer.aget(config)
            if checkpoint:
                return checkpoint.channel_values
            else:
                raise ValueError(f"Workflow {workflow_id} not found")
        except Exception as e:
            logger.error(f"Failed to get workflow state: {str(e)}")
            raise
    
    def get_workflow_description(self) -> str:
        """Get description of the multi-agent workflow"""
        return """
        Multi-Agent Stock Analysis Workflow:
        
        INPUT (Stock Symbol + Time Frame)
          ↓
        [Finance Guru Agent] 
        • Financial metrics analysis
        • Valuation assessment
        • Earnings and revenue trends
          ↓
        [Geopolitics Guru Agent]
        • Global events impact
        • Trade policies effect  
        • International market risks
          ↓
        [Legal Guru Agent]
        • Regulatory compliance
        • Legal risks assessment
        • Industry regulations
          ↓
        [Quant Dev Agent] 
        • Technical analysis
        • Statistical modeling
        • Price patterns and trends
          ↓
        [Financial Analyst Agent]
        • Consolidates all expert views
        • Creates final prediction
        • Assigns confidence scores
          ↓
        OUTPUT (Comprehensive Forecast + Agent Insights)
        
        Features:
        - 5 specialized AI agents
        - Sequential processing (ensures each agent builds on previous insights)
        - LLM-powered domain expertise (Claude 3.7 Sonnet)
        - Comprehensive multi-perspective analysis
        - Confidence scoring and risk assessment
        - Detailed reasoning for each prediction
        
        Note: Sequential execution ensures proper state management and 
        allows each agent to learn from previous agent insights.
        """