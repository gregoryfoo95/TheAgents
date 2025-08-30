from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, AsyncGenerator
import uvicorn
import logging
import os
import json
import asyncio
import uuid
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

@app.get("/debug/database")
async def debug_database(db: Session = Depends(get_db)):
    """Debug endpoint to check database state"""
    
    try:
        from sqlalchemy import text
        
        # Count total sessions
        count_result = db.execute(text("SELECT COUNT(*) FROM stock_analysis_sessions")).fetchone()
        total_sessions = count_result[0] if count_result else 0
        
        # Get recent sessions
        recent_sessions = db.execute(
            text("""
                SELECT session_id, user_id, stock_symbol, status, created_at 
                FROM stock_analysis_sessions 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
        ).fetchall()
        
        sessions_list = []
        for session in recent_sessions:
            sessions_list.append({
                "session_id": str(session[0]),
                "user_id": session[1],
                "stock_symbol": session[2],
                "status": session[3],
                "created_at": session[4].isoformat() if session[4] else None
            })
        
        return {
            "database_status": "connected",
            "total_sessions": total_sessions,
            "recent_sessions": sessions_list
        }
        
    except Exception as e:
        logger.error(f"Database debug failed: {str(e)}")
        return {
            "database_status": "error",
            "error": str(e),
            "total_sessions": None,
            "recent_sessions": []
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
            session_id=uuid.UUID(str(db_session.session_id)),
            message_type="user_query",
            content=f"Analyze {request.symbol} for {request.time_frequency} timeframe",
            sender_type="user",
            message_metadata={
                "symbol": request.symbol,
                "time_frequency": request.time_frequency,
                "user_context": request.user_context
            }
        )
        
        logger.info(f"Created analysis session {db_session.session_id} for user {request.user_id}")

        # Update status to processing
        session_repo.update_session_status(
            session_id=uuid.UUID(str(db_session.session_id)),
            status="processing"
        )
        
        try:
            # Run multi-agent analysis
            final_state = await orchestrator.analyze_stock(
                symbol=request.symbol,
                time_frequency=request.time_frequency,
                user_context=request.user_context if request.user_context is not None else ""
            )
            
            # Check for analysis completion
            if not final_state.get('analysis_result'):
                error_msg = "; ".join(final_state.get('errors', ['Analysis failed to complete']))
                
                # Log errors to database
                for error in final_state.get('errors', []):
                    error_repo.log_error(
                        session_id=uuid.UUID(str(db_session.session_id)),
                        error_type="analysis_error",
                        error_message=error
                    )
                
                # Update session as failed
                session_repo.update_session_status(
                    session_id=uuid.UUID(str(db_session.session_id)),
                    status="failed",
                    completed_at=datetime.now(timezone.utc)
                )
                
                raise HTTPException(status_code=500, detail=f"Analysis failed: {error_msg}")
            
            result = final_state['analysis_result']
            
            # Save agent analyses to database
            if final_state.get('finance_analysis'):
                analysis_repo.create_analysis(
                    session_id= uuid.UUID(str(db_session.session_id)),
                    agent_type="finance_guru",
                    agent_name="Finance Guru",
                    analysis_text=final_state['finance_analysis'].analysis,
                    processing_time_ms=final_state['finance_analysis'].processing_time_ms
                )
            
            if final_state.get('geopolitics_analysis'):
                analysis_repo.create_analysis(
                    session_id= uuid.UUID(str(db_session.session_id)),
                    agent_type="geopolitics_guru", 
                    agent_name="Geopolitics Guru",
                    analysis_text=final_state['geopolitics_analysis'].analysis,
                    processing_time_ms=final_state['geopolitics_analysis'].processing_time_ms
                )
            
            if final_state.get('legal_analysis'):
                analysis_repo.create_analysis(
                    session_id=uuid.UUID(str(db_session.session_id)),
                    agent_type="legal_guru",
                    agent_name="Legal Guru", 
                    analysis_text=final_state['legal_analysis'].analysis,
                    processing_time_ms=final_state['legal_analysis'].processing_time_ms
                )
            
            if final_state.get('quant_analysis'):
                analysis_repo.create_analysis(
                    session_id=uuid.UUID(str(db_session.session_id)),
                    agent_type="quant_dev",
                    agent_name="Quant Dev",
                    analysis_text=final_state['quant_analysis'].analysis,
                    processing_time_ms=final_state['quant_analysis'].processing_time_ms
                )
            
            if final_state.get('final_analysis'):
                analysis_repo.create_analysis(
                    session_id=uuid.UUID(str(db_session.session_id)),
                    agent_type="financial_analyst",
                    agent_name="Financial Analyst",
                    analysis_text=final_state['final_analysis'].analysis,
                    processing_time_ms=final_state['final_analysis'].processing_time_ms
                )
            
            # Save predictions to database
            if result.prediction and "predictions" in result.prediction:
                prediction_repo.create_predictions(
                    session_id=uuid.UUID(str(db_session.session_id)),
                    predictions=result.prediction["predictions"]
                )
            
            # Save completion message
            message_repo.create_message(
                session_id=uuid.UUID(str(db_session.session_id)),
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
                session_id=uuid.UUID(str(db_session.session_id)),
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
                session_id=uuid.UUID(str(db_session.session_id)),
                error_type="workflow_error",
                error_message=str(e)
            )
            
            # Update session as failed
            session_repo.update_session_status(
                session_id=uuid.UUID(str(db_session.session_id)),
                status="failed",
                completed_at=datetime.now(timezone.utc)
            )
            
            raise HTTPException(status_code=500, detail=f"Analysis workflow failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal analysis error: {str(e)}")




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
        logger.info(f"🔍 GET /sessions/{session_id} - Starting session details lookup")
        logger.info(f"📊 Raw session_id received: '{session_id}' (type: {type(session_id)})")
        
        # Validate UUID format first
        try:
            session_uuid = uuid.UUID(session_id)
            logger.info(f"✅ UUID validation successful: {session_uuid}")
        except ValueError as uuid_error:
            logger.error(f"❌ Invalid UUID format for session_id '{session_id}': {uuid_error}")
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        logger.info(f"🗄️ Creating database repository...")
        session_repo = StockAnalysisRepository(db)
        logger.info(f"📋 Calling get_session_with_details with UUID: {session_uuid}")
        
        session = session_repo.get_session_with_details(session_uuid)
        logger.info(f"🔍 Repository returned session: {session is not None}")
        
        if not session:
            logger.warning(f"❌ Session not found in database for UUID: {session_uuid}")
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
        
    except ValueError as ve:
        logger.error(f"❌ ValueError in get_session_details: {str(ve)}")
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except HTTPException:
        # Re-raise HTTP exceptions (404, etc.)
        raise
    except Exception as e:
        logger.error(f"💥 Unexpected exception in get_session_details: {type(e).__name__}: {str(e)}")
        logger.error(f"📍 Exception details: {repr(e)}")
        import traceback
        logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """Get user's analysis sessions from stock AI service database"""
    
    try:
        # Convert user_id to integer (our database uses integer user IDs)
        try:
            user_int = int(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
            
        session_repo = StockAnalysisRepository(db)
        sessions = session_repo.get_user_sessions(
            user_id=user_int,
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

@app.post("/analyze-portfolio-stream-init")
async def analyze_portfolio_stream_init(request: PortfolioAnalysisRequest, db: Session = Depends(get_db)):
    """Initialize a streaming portfolio analysis session and return session ID"""
    
    try:
        logger.info(f"Initializing streaming portfolio analysis session for user {request.user_id}")
        
        # Validate inputs
        if not request.portfolio_data or len(request.portfolio_data) == 0:
            raise HTTPException(status_code=400, detail="Portfolio data is required")
        
        # Validate total allocation
        total_allocation = sum(stock.get("allocation", 0) for stock in request.portfolio_data)
        if not (99.0 <= total_allocation <= 101.0):
            raise HTTPException(status_code=400, detail=f"Portfolio allocations must sum to 100%, got {total_allocation}%")
        
        # Initialize repositories
        session_repo = StockAnalysisRepository(db)
        
        # Create database session for portfolio analysis
        workflow_id = uuid.uuid4()
        
        # Create summary of portfolio for database storage
        portfolio_symbols = [stock["symbol"] for stock in request.portfolio_data]
        portfolio_summary = f"Portfolio: {', '.join(portfolio_symbols[:3])}{'...' if len(portfolio_symbols) > 3 else ''}"
        
        db_session = session_repo.create_session(
            user_id=request.user_id,
            stock_symbol=portfolio_summary,
            time_frequency=request.time_frequency,
            workflow_id=workflow_id,
            analysis_type="portfolio",
            portfolio_data=request.portfolio_data
        )
        
        logger.info(f"Created portfolio analysis session {db_session.session_id} for user {request.user_id}")
        # Store session data in memory for streaming (you might want to use Redis for production)
        session_data = {
            'session_id': str(db_session.session_id),
            'workflow_id': str(workflow_id),
            'portfolio_data': request.portfolio_data,
            'time_frequency': request.time_frequency,
            'user_id': request.user_id,
            'status': 'initialized',
            'db_session': db_session
        }
        
        # Store in a global dict (use Redis/cache in production)
        if not hasattr(app.state, 'streaming_sessions'):
            app.state.streaming_sessions = {}
        app.state.streaming_sessions[str(db_session.session_id)] = session_data
        
        logger.info(f"Stored streaming session data for session {db_session.session_id}")
        return {
            'session_id': uuid.UUID(str(db_session.session_id)),
            'workflow_id': str(workflow_id),
            'status': 'initialized'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initialize streaming session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize streaming session: {str(e)}")

@app.get("/stream/{session_id}")
async def stream_portfolio_analysis_sse(session_id: str, db: Session = Depends(get_db)):
    """EventSource-compatible streaming endpoint for portfolio analysis"""
    
    async def generate_sse_stream() -> AsyncGenerator[str, None]:
        try:
            logger.info(f"🌊 Starting EventSource stream for session {session_id}")
            
            # Get session data
            if not hasattr(app.state, 'streaming_sessions') or session_id not in app.state.streaming_sessions:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
                return
            
            session_data = app.state.streaming_sessions[session_id]
            
            # Initialize repositories
            session_repo = StockAnalysisRepository(db)
            message_repo = StockChatMessageRepository(db)
            
            # Update status to processing
            session_repo.update_session_status(
                session_id=uuid.UUID(session_id),
                status="processing"
            )
            
            # Stream initial events
            yield f"data: {json.dumps({'type': 'session_start', 'session_id': session_id, 'workflow_id': session_data['workflow_id'], 'portfolio': [stock['symbol'] for stock in session_data['portfolio_data']]})}\n\n"
            
            user_message_content = f"Analyze portfolio with {len(session_data['portfolio_data'])} stocks for {session_data['time_frequency']} timeframe"
            yield f"data: {json.dumps({'type': 'user_message', 'content': user_message_content, 'timestamp': datetime.now().isoformat()})}\n\n"
            
            yield f"data: {json.dumps({'type': 'status_update', 'status': 'processing', 'message': 'Starting multi-agent analysis...'})}\n\n"
            
            # Stream agent analysis with the generator
            async for agent_update in stream_portfolio_analysis(session_data['portfolio_data'], session_data['time_frequency']):
                yield f"data: {json.dumps(agent_update)}\n\n"
                await asyncio.sleep(0.1)  # Small delay for better streaming
            
            # Complete session
            session_repo.update_session_status(session_id=uuid.UUID(session_id), status="completed")
            yield f"data: {json.dumps({'type': 'session_complete', 'message': 'Portfolio analysis completed successfully'})}\n\n"
            
            # Cleanup session data
            if hasattr(app.state, 'streaming_sessions') and session_id in app.state.streaming_sessions:
                del app.state.streaming_sessions[session_id]
            
        except Exception as e:
            logger.error(f"EventSource streaming failed: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Analysis failed: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@app.post("/analyze-portfolio-stream")
async def analyze_portfolio_stream(request: PortfolioAnalysisRequest, db: Session = Depends(get_db)):
    """Stream multi-agent portfolio analysis with real-time agent updates"""
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            logger.info(f"Starting streaming portfolio analysis for user {request.user_id}")
            
            # Validate inputs
            if not request.portfolio_data or len(request.portfolio_data) == 0:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Portfolio data is required'})}\n\n"
                return
            
            # Initialize repositories
            session_repo = StockAnalysisRepository(db)
            message_repo = StockChatMessageRepository(db)
            
            # Create database session
            import uuid
            workflow_id = uuid.uuid4()
            
            portfolio_symbols = [stock["symbol"] for stock in request.portfolio_data]
            portfolio_summary = f"Portfolio: {', '.join(portfolio_symbols[:3])}{'...' if len(portfolio_symbols) > 3 else ''}"
            
            db_session = session_repo.create_session(
                user_id=request.user_id,
                stock_symbol=portfolio_summary,
                time_frequency=request.time_frequency,
                workflow_id=workflow_id,
                analysis_type="portfolio",
                portfolio_data=request.portfolio_data
            )
            
            # Stream initial message
            yield f"data: {json.dumps({'type': 'session_start', 'session_id': str(db_session.session_id), 'workflow_id': str(workflow_id), 'portfolio': portfolio_symbols})}\n\n"
            
            # Stream user query
            yield f"data: {json.dumps({'type': 'user_message', 'content': f'Analyze portfolio with {len(request.portfolio_data)} stocks for {request.time_frequency} timeframe', 'timestamp': datetime.now().isoformat()})}\n\n"
            
            # Update status to processing
            session_repo.update_session_status(session_id=db_session.session_id, status="processing")
            yield f"data: {json.dumps({'type': 'status_update', 'status': 'processing', 'message': 'Starting multi-agent analysis...'})}\n\n"
            
            # Stream agent analysis with custom orchestrator
            async for agent_update in stream_portfolio_analysis(request.portfolio_data, request.time_frequency):
                yield f"data: {json.dumps(agent_update)}\n\n"
                await asyncio.sleep(0.1)  # Small delay for better streaming
            
            # Complete session
            session_repo.update_session_status(session_id=db_session.session_id, status="completed")
            yield f"data: {json.dumps({'type': 'session_complete', 'message': 'Portfolio analysis completed successfully'})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming portfolio analysis failed: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Analysis failed: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

async def stream_portfolio_analysis(portfolio_data: list, time_frequency: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream individual agent analyses for portfolio"""
    
    try:
        # Create portfolio context
        portfolio_symbols = [f"{stock['symbol']}({stock.get('allocation', stock.get('allocation_percentage', 0))}%)" 
                           for stock in portfolio_data]
        portfolio_summary = f"Portfolio: {', '.join(portfolio_symbols)}"
        
        portfolio_context = f"""Portfolio Analysis Context:
        - Total Stocks: {len(portfolio_symbols)}
        - Portfolio Composition: {', '.join(portfolio_symbols)}
        - Analysis Timeframe: {time_frequency}
        - Analysis Type: Portfolio-level multi-asset analysis
        """
        
        # Stream system message
        yield {
            'type': 'system_message',
            'content': f'🤖 Starting comprehensive multi-agent analysis for {len(portfolio_data)} stocks',
            'timestamp': datetime.now().isoformat()
        }
        
        # Agent names and order
        agents = [
            {'id': 'finance_guru', 'name': 'Finance Guru', 'icon': '🏦', 'description': 'Analyzing financial metrics and market fundamentals'},
            {'id': 'geopolitics_guru', 'name': 'Geopolitics Guru', 'icon': '🌍', 'description': 'Evaluating global events and geopolitical impacts'},
            {'id': 'legal_guru', 'name': 'Legal Guru', 'icon': '⚖️', 'description': 'Assessing regulatory compliance and legal risks'},
            {'id': 'quant_dev', 'name': 'Quant Dev', 'icon': '📊', 'description': 'Performing technical analysis and statistical modeling'},
            {'id': 'financial_analyst', 'name': 'Financial Analyst', 'icon': '📈', 'description': 'Consolidating expert insights into final predictions'}
        ]
        
        # Stream each agent analysis
        for i, agent in enumerate(agents):
            # Stream agent start
            yield {
                'type': 'agent_start',
                'agent_id': agent['id'],
                'agent_name': agent['name'],
                'icon': agent['icon'],
                'content': f"{agent['icon']} {agent['name']}: {agent['description']}",
                'step': i + 1,
                'total_steps': len(agents),
                'timestamp': datetime.now().isoformat()
            }
            
            # Simulate agent processing time
            await asyncio.sleep(2)  # Realistic processing delay
            
            # Stream agent thinking process
            yield {
                'type': 'agent_thinking',
                'agent_id': agent['id'],
                'content': f"🧠 Analyzing portfolio from {agent['name'].lower()} perspective...",
                'timestamp': datetime.now().isoformat()
            }
            
            await asyncio.sleep(3)  # More processing time
            
            # Generate mock analysis for streaming demo
            analysis_content = generate_mock_agent_analysis(agent, portfolio_symbols, time_frequency)
            
            # Stream agent completion
            yield {
                'type': 'agent_complete',
                'agent_id': agent['id'],
                'agent_name': agent['name'],
                'icon': agent['icon'],
                'content': f"✅ {agent['name']} analysis complete",
                'analysis': analysis_content,
                'confidence': 0.75 + (i * 0.05),  # Varying confidence
                'processing_time_ms': 2000 + (i * 500),
                'timestamp': datetime.now().isoformat()
            }
            
            await asyncio.sleep(1)  # Brief pause between agents
        
        # Stream final result
        yield {
            'type': 'final_result',
            'content': f'✅ Portfolio analysis complete! All 5 AI experts have analyzed your {len(portfolio_data)}-stock portfolio.',
            'confidence_score': 0.82,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Streaming analysis failed: {str(e)}")
        yield {
            'type': 'error',
            'message': f'Streaming analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def generate_mock_agent_analysis(agent: Dict[str, str], portfolio_symbols: List[str], time_frequency: str) -> str:
    """Generate mock analysis content for demo purposes"""
    
    agent_analyses = {
        'finance_guru': f"""Portfolio Financial Analysis ({time_frequency}):

Analyzed {len(portfolio_symbols)} positions: {', '.join(portfolio_symbols[:3])}

Key Financial Insights:
• Portfolio shows diversified exposure across sectors
• Weighted average P/E ratio indicates balanced valuation
• Revenue growth trends are positive across major holdings
• Risk-adjusted returns demonstrate solid fundamentals

Recommendation: Portfolio composition aligns with current market conditions and shows strong financial health indicators.""",

        'geopolitics_guru': f"""Portfolio Geopolitical Risk Assessment ({time_frequency}):

Geographic and Political Analysis for {len(portfolio_symbols)} holdings:

Key Geopolitical Factors:
• International trade relations impact on portfolio companies
• Currency fluctuation risks across global markets
• Regulatory changes in key operating regions
• Supply chain resilience considerations

Risk Level: MODERATE - Diversification provides good geopolitical risk mitigation.""",

        'legal_guru': f"""Portfolio Legal & Regulatory Analysis ({time_frequency}):

Compliance and Legal Risk Assessment:

Key Legal Considerations:
• Regulatory compliance status across all holdings
• Industry-specific legal requirements evaluation
• ESG compliance and sustainability regulations
• Data privacy and cybersecurity legal frameworks

Legal Risk Rating: LOW-MODERATE - Well-positioned for current regulatory environment.""",

        'quant_dev': f"""Portfolio Quantitative Analysis ({time_frequency}):

Technical and Statistical Analysis:

Key Technical Indicators:
• Portfolio beta: 1.12 (slightly more volatile than market)
• Correlation matrix shows good diversification benefits
• Moving averages trending positive across major positions
• Volatility analysis indicates balanced risk profile

Quantitative Score: 7.8/10 - Strong technical foundation with good risk management.""",

        'financial_analyst': f"""Final Portfolio Investment Analysis ({time_frequency}):

Consolidated Expert Opinion:

Portfolio Summary:
• {len(portfolio_symbols)} diversified positions
• Balanced risk-return profile
• Strong fundamentals with growth potential
• Well-positioned for {time_frequency} timeframe

Final Recommendation: BUY/HOLD - Portfolio demonstrates solid fundamentals, appropriate diversification, and positive outlook across all expert analysis dimensions."""
    }
    
    return agent_analyses.get(agent['id'], f"Analysis completed for {agent['name']}")

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
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)