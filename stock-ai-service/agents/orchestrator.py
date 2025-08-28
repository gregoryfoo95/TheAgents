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
        """Run multi-agent analysis for a portfolio of stocks"""
        
        workflow_id = str(uuid.uuid4())
        
        try:
            # Initialize state for portfolio analysis
            initial_state = StockAnalysisState(
                symbol="PORTFOLIO",  # Special symbol for portfolio
                time_frequency=time_frequency,
                user_context=f"Portfolio analysis with {len(portfolio_data)} stocks",
                workflow_id=workflow_id,
                portfolio_data=portfolio_data,  # Add portfolio data to state
                analysis_type="portfolio"
            )
            
            # Run the workflow
            config = {"configurable": {"thread_id": workflow_id}}
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            return final_state
            
        except Exception as e:
            logger.error(f"Portfolio analysis workflow failed: {e}")
            return {
                "workflow_id": workflow_id,
                "errors": [str(e)],
                "analysis_result": None
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