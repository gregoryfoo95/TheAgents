from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import logging
import os
from datetime import datetime, timezone

from config import settings
from agents.orchestrator import StockAnalysisOrchestrator
from database.base import get_db, create_tables
from database.repositories import (
    StockAnalysisRepository,
    AgentAnalysisRepository,
    StockPredictionRepository,
    StockChatMessageRepository,
    StockAnalysisErrorRepository
)
from sqlalchemy.orm import Session
from fastapi import Depends
from controllers.portfolio_controller import create_portfolio_endpoints

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Stock AI Analysis Service",
    description="Multi-agent AI service for comprehensive stock market analysis",
    version="1.0.0"
)

# Add CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = StockAnalysisOrchestrator()

# Add portfolio management endpoints
create_portfolio_endpoints(app)

class StockAnalysisRequest(BaseModel):
    symbol: str
    time_frequency: str = "1M"
    user_id: int  # User ID from main backend (changed to int)
    user_context: Optional[str] = None


class PortfolioAnalysisRequest(BaseModel):
    user_id: int  # User ID from main backend
    portfolio_data: List[Dict[str, Any]]  # [{"symbol": "AAPL", "allocation": 30.0}, ...]
    time_frequency: str = "1M"
    analysis_type: str = "portfolio"

class AgentAnalysisResponse(BaseModel):
    agent_type: str
    agent_name: str 
    analysis: str
    confidence: float
    key_factors: List[str]
    processing_time_ms: int

class PredictionPoint(BaseModel):
    date: str
    price: float

class StockAnalysisResponse(BaseModel):
    symbol: str
    workflow_id: str
    prediction: Dict
    analysis: Dict[str, str]
    confidence_score: float
    factors_considered: List[str]
    processing_summary: Dict[str, Any]
    
class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    current_step: str
    status: str
    errors: List[str]
    warnings: List[str]

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "stock-ai-analysis",
        "version": "1.0.0",
        "agents": ["finance_guru", "geopolitics_guru", "legal_guru", "quant_dev", "financial_analyst"]
    }

@app.get("/agents/description") 
async def get_agents_description():
    """Get description of the multi-agent workflow"""
    return {
        "workflow_description": orchestrator.get_workflow_description(),
        "agents": [
            {
                "name": "Finance Guru",
                "type": "finance_guru", 
                "description": "Analyzes financial metrics, valuation, and market fundamentals"
            },
            {
                "name": "Geopolitics Guru",
                "type": "geopolitics_guru",
                "description": "Evaluates global events and geopolitical risks impact"
            },
            {
                "name": "Legal Guru", 
                "type": "legal_guru",
                "description": "Assesses regulatory compliance and legal risk factors"
            },
            {
                "name": "Quant Dev",
                "type": "quant_dev", 
                "description": "Performs technical analysis and statistical modeling"
            },
            {
                "name": "Financial Analyst",
                "type": "financial_analyst",
                "description": "Consolidates expert insights into final predictions"
            }
        ]
    }

@app.post("/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest, db: Session = Depends(get_db)):
    """Run comprehensive multi-agent stock analysis"""
    
    try:
        logger.info(f"Starting analysis for {request.symbol} with timeframe {request.time_frequency}")
        
        # Validate inputs
        if not request.symbol or len(request.symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid stock symbol")
        
        valid_frequencies = ['1D', '1W', '1M', '3M', '6M', '1Y']
        if request.time_frequency not in valid_frequencies:
            raise HTTPException(status_code=400, detail=f"Invalid time frequency. Use one of: {valid_frequencies}")
        
        # Initialize repositories
        session_repo = StockAnalysisRepository(db)
        analysis_repo = AgentAnalysisRepository(db)
        prediction_repo = StockPredictionRepository(db)
        message_repo = StockChatMessageRepository(db)
        error_repo = StockAnalysisErrorRepository(db)
        
        # Create database session first
        import uuid
        workflow_id = uuid.uuid4()
        
        db_session = session_repo.create_session(
            user_id=request.user_id,  # Now using int directly
            stock_symbol=request.symbol,
            time_frequency=request.time_frequency,
            workflow_id=workflow_id
        )
        
        # Log initial user query
        message_repo.create_message(
            session_id=db_session.session_id,
            message_type="user_query",
            content=f"Analyze {request.symbol} for {request.time_frequency} timeframe",
            sender_type="user",
            message_metadata={
                "symbol": request.symbol,
                "time_frequency": request.time_frequency,
                "user_context": request.user_context
            }
        )
        
        # Update status to processing
        session_repo.update_session_status(
            session_id=db_session.session_id,
            status="processing"
        )
        
        try:
            # Run multi-agent analysis
            final_state = await orchestrator.analyze_stock(
                symbol=request.symbol,
                time_frequency=request.time_frequency,
                user_context=request.user_context
            )
            
            # Check for analysis completion
            if not final_state.get('analysis_result'):
                error_msg = "; ".join(final_state.get('errors', ['Analysis failed to complete']))
                
                # Log errors to database
                for error in final_state.get('errors', []):
                    error_repo.log_error(
                        session_id=db_session.session_id,
                        error_type="analysis_error",
                        error_message=error
                    )
                
                # Update session as failed
                session_repo.update_session_status(
                    session_id=db_session.session_id,
                    status="failed",
                    completed_at=datetime.now(timezone.utc)
                )
                
                raise HTTPException(status_code=500, detail=f"Analysis failed: {error_msg}")
            
            result = final_state['analysis_result']
            
            # Save agent analyses to database
            if final_state.get('finance_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="finance_guru",
                    agent_name="Finance Guru",
                    analysis_text=final_state['finance_analysis'].analysis,
                    processing_time_ms=final_state['finance_analysis'].processing_time_ms
                )
            
            if final_state.get('geopolitics_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="geopolitics_guru", 
                    agent_name="Geopolitics Guru",
                    analysis_text=final_state['geopolitics_analysis'].analysis,
                    processing_time_ms=final_state['geopolitics_analysis'].processing_time_ms
                )
            
            if final_state.get('legal_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="legal_guru",
                    agent_name="Legal Guru", 
                    analysis_text=final_state['legal_analysis'].analysis,
                    processing_time_ms=final_state['legal_analysis'].processing_time_ms
                )
            
            if final_state.get('quant_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="quant_dev",
                    agent_name="Quant Dev",
                    analysis_text=final_state['quant_analysis'].analysis,
                    processing_time_ms=final_state['quant_analysis'].processing_time_ms
                )
            
            if final_state.get('final_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="financial_analyst",
                    agent_name="Financial Analyst",
                    analysis_text=final_state['final_analysis'].analysis,
                    processing_time_ms=final_state['final_analysis'].processing_time_ms
                )
            
            # Save predictions to database
            if result.prediction and "predictions" in result.prediction:
                prediction_repo.create_predictions(
                    session_id=db_session.session_id,
                    predictions=result.prediction["predictions"]
                )
            
            # Save completion message
            message_repo.create_message(
                session_id=db_session.session_id,
                message_type="prediction_result",
                content="Stock analysis completed successfully",
                sender_type="ai_agent",
                message_metadata={
                    "confidence_score": result.confidence_score,
                    "factors_considered": result.factors_considered
                }
            )
            
            # Update session as completed
            session_repo.update_session_status(
                session_id=db_session.session_id,
                status="completed",
                confidence_score=result.confidence_score,
                completed_at=datetime.now(timezone.utc)
            )
            
            # Gather processing summary
            processing_summary = {
                "total_agents": 5,
                "successful_analyses": sum([
                    1 for agent in ['finance_analysis', 'geopolitics_analysis', 'legal_analysis', 'quant_analysis', 'final_analysis']
                    if final_state.get(agent) is not None
                ]),
                "total_processing_time_ms": sum([
                    final_state[agent].processing_time_ms 
                    for agent in ['finance_analysis', 'geopolitics_analysis', 'legal_analysis', 'quant_analysis', 'final_analysis']
                    if final_state.get(agent) is not None
                ]),
                "errors": final_state.get('errors', []),
                "warnings": final_state.get('warnings', [])
            }
            
            return StockAnalysisResponse(
                symbol=result.symbol,
                workflow_id=final_state['workflow_id'],
                prediction=result.prediction,
                analysis=result.agent_analyses,
                confidence_score=result.confidence_score,
                factors_considered=result.factors_considered,
                processing_summary=processing_summary
            )
            
        except HTTPException:
            raise
        except Exception as e:
            # Log error to database
            error_repo.log_error(
                session_id=db_session.session_id,
                error_type="workflow_error",
                error_message=str(e)
            )
            
            # Update session as failed
            session_repo.update_session_status(
                session_id=db_session.session_id,
                status="failed",
                completed_at=datetime.now(timezone.utc)
            )
            
            raise HTTPException(status_code=500, detail=f"Analysis workflow failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal analysis error: {str(e)}")


@app.post("/analyze-portfolio", response_model=StockAnalysisResponse)
async def analyze_portfolio(request: PortfolioAnalysisRequest, db: Session = Depends(get_db)):
    """Run comprehensive multi-agent portfolio analysis"""
    
    try:
        logger.info(f"Starting portfolioStarting portfolio analysis for user {request.user_id} with {len(request.portfolio_data)} stocks")
        
        # Validate inputs
        if not request.portfolio_data or len(request.portfolio_data) == 0:
            raise HTTPException(status_code=400, detail="Portfolio data is required")
        
        # Validate total allocation
        total_allocation = sum(stock.get("allocation", 0) for stock in request.portfolio_data)
        if not (99.0 <= total_allocation <= 101.0):
            raise HTTPException(status_code=400, detail=f"Portfolio allocations must sum to 100%, got {total_allocation}%")
        
        valid_frequencies = ['1D', '1W', '1M', '3M', '6M', '1Y']
        if request.time_frequency not in valid_frequencies:
            raise HTTPException(status_code=400, detail=f"Invalid time frequency. Use one of: {valid_frequencies}")
        
        # Initialize repositories
        session_repo = StockAnalysisRepository(db)
        analysis_repo = AgentAnalysisRepository(db)
        prediction_repo = StockPredictionRepository(db)
        message_repo = StockChatMessageRepository(db)
        error_repo = StockAnalysisErrorRepository(db)
        
        # Create database session for portfolio analysis
        import uuid
        workflow_id = uuid.uuid4()
        
        # Create summary of portfolio for database storage
        portfolio_symbols = [stock["symbol"] for stock in request.portfolio_data]
        portfolio_summary = f"Portfolio: {', '.join(portfolio_symbols[:3])}{'...' if len(portfolio_symbols) > 3 else ''}"
        
        db_session = session_repo.create_session(
            user_id=request.user_id,
            stock_symbol=portfolio_summary,  # Use portfolio summary instead of single symbol
            time_frequency=request.time_frequency,
            workflow_id=workflow_id,
            analysis_type="portfolio",
            portfolio_data=request.portfolio_data
        )
        
        # Log initial portfolio analysis request
        portfolio_details = f"Portfolio with {len(request.portfolio_data)} stocks: " + \
                          ", ".join([f"{s['symbol']}({s['allocation']}%)" for s in request.portfolio_data])
        
        message_repo.create_message(
            session_id=db_session.session_id,
            message_type="user_query",
            content=f"Analyze portfolio for {request.time_frequency} timeframe",
            sender_type="user",
            message_metadata={
                "portfolio_data": request.portfolio_data,
                "time_frequency": request.time_frequency,
                "analysis_type": request.analysis_type
            }
        )
        
        # Update status to processing
        session_repo.update_session_status(
            session_id=db_session.session_id,
            status="processing"
        )
        
        try:
            # Run multi-agent portfolio analysis
            # For portfolio analysis, we'll analyze each stock and then consolidate
            portfolio_context = {
                "portfolio_data": request.portfolio_data,
                "analysis_type": "portfolio",
                "total_stocks": len(request.portfolio_data)
            }
            
            final_state = await orchestrator.analyze_portfolio(
                portfolio_data=request.portfolio_data,
                time_frequency=request.time_frequency,
                user_context=portfolio_context
            )
            
            # Check for analysis completion
            if not final_state.get('analysis_result'):
                error_msg = "; ".join(final_state.get('errors', ['Portfolio analysis failed to complete']))
                
                # Log errors to database
                for error in final_state.get('errors', []):
                    error_repo.log_error(
                        session_id=db_session.session_id,
                        error_type="analysis_error",
                        error_message=error
                    )
                
                # Update session as failed
                session_repo.update_session_status(
                    session_id=db_session.session_id,
                    status="failed",
                    completed_at=datetime.now(timezone.utc)
                )
                
                raise HTTPException(status_code=500, detail=f"Portfolio analysis failed: {error_msg}")
            
            result = final_state['analysis_result']
            
            # Save agent analyses to database (same as stock analysis)
            if final_state.get('finance_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="finance_guru",
                    agent_name="Finance Guru",
                    analysis_text=final_state['finance_analysis'].analysis,
                    processing_time_ms=final_state['finance_analysis'].processing_time_ms
                )
            
            if final_state.get('geopolitics_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="geopolitics_guru", 
                    agent_name="Geopolitics Guru",
                    analysis_text=final_state['geopolitics_analysis'].analysis,
                    processing_time_ms=final_state['geopolitics_analysis'].processing_time_ms
                )
            
            if final_state.get('legal_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="legal_guru",
                    agent_name="Legal Guru", 
                    analysis_text=final_state['legal_analysis'].analysis,
                    processing_time_ms=final_state['legal_analysis'].processing_time_ms
                )
            
            if final_state.get('quant_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="quant_dev",
                    agent_name="Quant Dev",
                    analysis_text=final_state['quant_analysis'].analysis,
                    processing_time_ms=final_state['quant_analysis'].processing_time_ms
                )
            
            if final_state.get('final_analysis'):
                analysis_repo.create_analysis(
                    session_id=db_session.session_id,
                    agent_type="financial_analyst",
                    agent_name="Financial Analyst",
                    analysis_text=final_state['final_analysis'].analysis,
                    processing_time_ms=final_state['final_analysis'].processing_time_ms
                )
            
            # Save portfolio predictions to database
            if result.prediction and "predictions" in result.prediction:
                prediction_repo.create_predictions(
                    session_id=db_session.session_id,
                    predictions=result.prediction["predictions"]
                )
            
            # Save completion message
            message_repo.create_message(
                session_id=db_session.session_id,
                message_type="prediction_result",
                content="Portfolio analysis completed successfully",
                sender_type="ai_agent",
                message_metadata={
                    "confidence_score": result.confidence_score,
                    "factors_considered": result.factors_considered,
                    "portfolio_summary": portfolio_details
                }
            )
            
            # Update session as completed
            session_repo.update_session_status(
                session_id=db_session.session_id,
                status="completed",
                confidence_score=result.confidence_score,
                completed_at=datetime.now(timezone.utc)
            )
            
            # Gather processing summary
            processing_summary = {
                "total_agents": 5,
                "successful_analyses": sum([
                    1 for agent in ['finance_analysis', 'geopolitics_analysis', 'legal_analysis', 'quant_analysis', 'final_analysis']
                    if final_state.get(agent) is not None
                ]),
                "total_processing_time_ms": sum([
                    final_state[agent].processing_time_ms 
                    for agent in ['finance_analysis', 'geopolitics_analysis', 'legal_analysis', 'quant_analysis', 'final_analysis']
                    if final_state.get(agent) is not None
                ]),
                "errors": final_state.get('errors', []),
                "warnings": final_state.get('warnings', []),
                "portfolio_stocks": len(request.portfolio_data)
            }
            
            return StockAnalysisResponse(
                symbol=portfolio_summary,
                workflow_id=str(workflow_id),
                prediction=result.prediction,
                analysis=result.agent_analyses,
                confidence_score=result.confidence_score,
                factors_considered=result.factors_considered,
                processing_summary=processing_summary
            )
            
        except HTTPException:
            raise
        except Exception as e:
            # Log error to database
            error_repo.log_error(
                session_id=db_session.session_id,
                error_type="workflow_error",
                error_message=str(e)
            )
            
            # Update session as failed
            session_repo.update_session_status(
                session_id=db_session.session_id,
                status="failed",
                completed_at=datetime.now(timezone.utc)
            )
            
            raise HTTPException(status_code=500, detail=f"Portfolio analysis workflow failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal portfolio analysis error: {str(e)}")


@app.get("/workflow/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """Get status of a running analysis workflow"""
    
    try:
        state = await orchestrator.get_workflow_state(workflow_id)
        
        # Determine status
        if state.get('completed_at'):
            if state.get('analysis_result'):
                status = "completed"
            else:
                status = "failed"
        else:
            status = "running"
        
        return WorkflowStatusResponse(
            workflow_id=workflow_id,
            current_step=state.get('current_step', 'unknown'),
            status=status,
            errors=state.get('errors', []),
            warnings=state.get('warnings', [])
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/agents/{agent_type}/info")
async def get_agent_info(agent_type: str):
    """Get information about a specific agent"""
    
    agent_info = {
        "finance_guru": {
            "name": "Finance Guru",
            "description": "Senior financial analyst specializing in equity research, valuation, and fundamental analysis",
            "capabilities": [
                "Financial metrics analysis",
                "Valuation assessment", 
                "Revenue and earnings trend analysis",
                "Competitive positioning",
                "Investment recommendations"
            ]
        },
        "geopolitics_guru": {
            "name": "Geopolitics Guru", 
            "description": "Expert in geopolitical risk analysis and global market impact assessment",
            "capabilities": [
                "Global events impact analysis",
                "Trade policy implications",
                "Regulatory risk assessment",
                "Currency impact evaluation",
                "Supply chain disruption analysis"
            ]
        },
        "legal_guru": {
            "name": "Legal Guru",
            "description": "Corporate law and regulatory compliance specialist",
            "capabilities": [
                "Regulatory compliance assessment",
                "Legal risk evaluation",
                "Industry regulation analysis", 
                "Litigation risk assessment",
                "ESG compliance review"
            ]
        },
        "quant_dev": {
            "name": "Quant Dev",
            "description": "Quantitative analyst and technical analysis expert",
            "capabilities": [
                "Technical indicator analysis",
                "Statistical modeling",
                "Price pattern recognition",
                "Volatility assessment",
                "Risk metrics calculation"
            ]
        },
        "financial_analyst": {
            "name": "Financial Analyst", 
            "description": "Senior analyst responsible for consolidating multi-expert insights",
            "capabilities": [
                "Multi-source analysis synthesis",
                "Final prediction generation",
                "Confidence score assignment", 
                "Risk assessment consolidation",
                "Investment recommendation"
            ]
        }
    }
    
    if agent_type not in agent_info:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    return agent_info[agent_type]

@app.get("/sessions/{session_id}")
async def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """Get detailed session data from stock AI service database"""
    
    try:
        session_repo = StockAnalysisRepository(db)
        session = session_repo.get_session_with_details(uuid.UUID(session_id))
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert to response format
        agent_analyses = []
        for analysis in session.agent_analyses:
            agent_analyses.append({
                "agent_type": analysis.agent_type,
                "agent_name": analysis.agent_name,
                "analysis_text": analysis.analysis_text,
                "processing_time_ms": analysis.processing_time_ms
            })
        
        predictions = []
        for prediction in session.predictions:
            predictions.append({
                "date": prediction.prediction_date.isoformat(),
                "price": float(prediction.predicted_price)
            })
        
        chat_messages = []
        for msg in session.chat_messages:
            chat_messages.append({
                "message_type": msg.message_type,
                "content": msg.content,
                "sender_type": msg.sender_type,
                "message_metadata": msg.message_metadata,
                "created_at": msg.created_at.isoformat()
            })
        
        return {
            "session_id": str(session.session_id),
            "user_id": str(session.user_id),
            "stock_symbol": session.stock_symbol,
            "time_frequency": session.time_frequency,
            "workflow_id": str(session.workflow_id),
            "status": session.status,
            "confidence_score": float(session.confidence_score) if session.confidence_score else None,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "agent_analyses": agent_analyses,
            "predictions": predictions,
            "chat_messages": chat_messages
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get session details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """Get user's analysis sessions from stock AI service database"""
    
    try:
        session_repo = StockAnalysisRepository(db)
        sessions = session_repo.get_user_sessions(
            user_id=uuid.UUID(user_id),
            limit=limit,
            offset=offset
        )
        
        result = []
        for session in sessions:
            result.append({
                "session_id": str(session.session_id),
                "stock_symbol": session.stock_symbol,
                "time_frequency": session.time_frequency,
                "status": session.status,
                "confidence_score": float(session.confidence_score) if session.confidence_score else None,
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            })
        
        return result
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        logger.error(f"Failed to get user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Add lifespan event to create tables
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    try:
        await create_tables()
        logger.info("Stock AI service database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, debug=settings.debug)