from typing import Dict, List, Any, Optional, TypedDict
from pydantic import BaseModel
from datetime import datetime, timezone

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
    
    # Agent analyses
    finance_analysis: Optional[AgentAnalysis]
    geopolitics_analysis: Optional[AgentAnalysis] 
    legal_analysis: Optional[AgentAnalysis]
    quant_analysis: Optional[AgentAnalysis]
    
    # Final analysis
    final_analysis: Optional[AgentAnalysis]
    
    # Processing state
    current_step: str
    errors: List[str]
    warnings: List[str]
    
    # Results
    analysis_result: Optional[StockAnalysisResult]
    
    # Workflow tracking
    workflow_id: str
    started_at: str
    completed_at: Optional[str]