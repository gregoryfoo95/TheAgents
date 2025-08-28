from typing import Dict, List, Any, Optional, TypedDict, Annotated
from pydantic import BaseModel
from datetime import datetime, timezone
from langgraph.graph import add_messages
from operator import add

class StockAnalysisRequest(BaseModel):
    symbol: str
    time_frequency: str
    user_context: Optional[str] = None

class AgentAnalysis(BaseModel):
    agent_type: str
    agent_name: str
    analysis: str
    confidence: float
    key_factors: List[str]
    processing_time_ms: int

class PredictionPoint(BaseModel):
    date: str
    price: float

class StockAnalysisResult(BaseModel):
    symbol: str
    prediction: Dict[str, Any]
    agent_analyses: Dict[str, str]
    confidence_score: float
    factors_considered: List[str]

class StockAnalysisState(TypedDict):
    """State for the stock analysis workflow"""
    # Input data
    request: StockAnalysisRequest
    
    # Agent analyses - each agent updates its own key (no concurrent conflicts)
    finance_analysis: Optional[AgentAnalysis]
    geopolitics_analysis: Optional[AgentAnalysis] 
    legal_analysis: Optional[AgentAnalysis]
    quant_analysis: Optional[AgentAnalysis]
    
    # Final analysis
    final_analysis: Optional[AgentAnalysis]
    
    # Processing state
    current_step: str
    errors: Annotated[List[str], add]  # Allow concurrent error additions
    warnings: Annotated[List[str], add]  # Allow concurrent warning additions
    
    # Results
    analysis_result: Optional[StockAnalysisResult]
    
    # Workflow tracking
    workflow_id: str
    started_at: str
    completed_at: Optional[str]