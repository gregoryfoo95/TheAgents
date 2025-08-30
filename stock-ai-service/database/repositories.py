from asyncio.log import logger
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc, and_
from datetime import datetime, timezone
import uuid

from .models import (
    StockAnalysisSession,
    AgentAnalysis,
    StockPrediction,
    StockChatMessage,
    StockAnalysisError
)

class BaseRepository:
    """Base repository with common CRUD operations"""
    
    def __init__(self, model_class, db: Session):
        self.model_class = model_class
        self.db = db
    
    def get(self, id: uuid.UUID):
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()
    
    def create(self, **kwargs):
        instance = self.model_class(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def update(self, id: uuid.UUID, **kwargs):
        instance = self.get(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance
    
    def delete(self, id: uuid.UUID):
        instance = self.get(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
        return instance

class StockAnalysisRepository(BaseRepository):
    """Repository for stock analysis sessions"""
    
    def __init__(self, db: Session):
        super().__init__(StockAnalysisSession, db)
    
    def get(self, session_id: uuid.UUID) -> Optional[StockAnalysisSession]:
        return self.db.query(StockAnalysisSession).filter(
            StockAnalysisSession.session_id == session_id
        ).first()
    
    def create_session(
        self, 
        user_id: int,  # Changed from UUID to int
        stock_symbol: str, 
        time_frequency: str,
        workflow_id: uuid.UUID,
        analysis_type: str = "stock",
        portfolio_data: list = None
    ) -> StockAnalysisSession:
        """Create a new stock analysis session"""
        
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔨 Creating session with user_id={user_id}, symbol='{stock_symbol}', type='{analysis_type}'")
        
        session = StockAnalysisSession(
            user_id=user_id,
            stock_symbol=stock_symbol.upper() if stock_symbol else "PORTFOLIO",
            time_frequency=time_frequency,
            workflow_id=workflow_id,
            status="pending",
            analysis_type=analysis_type,
            portfolio_data=portfolio_data
        )
        
        logger.info(f"📋 Session object created with ID: {session.session_id}")
        
        try:
            logger.info(f"➕ Adding session to database...")
            self.db.add(session)
            
            logger.info(f"🔄 Flushing to ensure immediate visibility...")
            self.db.flush()  # Ensure immediate visibility
            
            logger.info(f"✅ Session after flush - ID: {session.session_id}")
            
            logger.info(f"💾 Committing transaction...")
            self.db.commit()
            
            logger.info(f"🔄 Refreshing session from database...")
            self.db.refresh(session)
            
            logger.info(f"🎉 Session creation completed! Final ID: {session.session_id}")
            
            # Let's immediately try to query it back to verify
            test_query = self.db.query(StockAnalysisSession).filter(
                StockAnalysisSession.session_id == session.session_id
            ).first()
            logger.info(f"🔍 Verification query result: {test_query is not None}")
            
            return session
            
        except Exception as e:
            logger.error(f"💥 Error during session creation: {type(e).__name__}: {str(e)}")
            self.db.rollback()
            raise
    
    def update_session_status(
        self,
        session_id: uuid.UUID,
        status: str,
        confidence_score: Optional[float] = None,
        completed_at: Optional[datetime] = None
    ) -> Optional[StockAnalysisSession]:
        """Update session status and completion info"""
        
        session = self.get(session_id)
        logger.info(f"🔄 Updating session {session_id} to status '{status}'")
        if session:
            session.status = status
            if confidence_score is not None:
                session.confidence_score = confidence_score
            if completed_at:
                session.completed_at = completed_at
            
            self.db.commit()
            self.db.refresh(session)
            
        return session
    
    def get_user_sessions(
        self, 
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[StockAnalysisSession]:
        """Get user's stock analysis sessions"""
        
        return (
            self.db.query(StockAnalysisSession)
            .filter(StockAnalysisSession.user_id == user_id)
            .order_by(desc(StockAnalysisSession.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    def get_session_with_details(
        self,
        session_id: uuid.UUID
    ) -> Optional[StockAnalysisSession]:
        """Get session with all related data"""
        
        import logging
        from sqlalchemy import text
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔍 Repository: get_session_with_details called with session_id: {session_id}")
        logger.info(f"📊 Session ID type: {type(session_id)}")
        
        try:
            # First, let's try a direct raw SQL query to see what's in the database
            logger.info(f"🔍 Testing raw SQL query to check if session exists...")
            raw_result = self.db.execute(
                text("SELECT session_id, stock_symbol, status, created_at FROM stock_analysis_sessions WHERE session_id = :session_id"),
                {"session_id": session_id}
            ).fetchone()
            logger.info(f"🧪 Raw SQL result: {raw_result}")
            
            # Let's also check what sessions exist in total
            logger.info(f"🔍 Checking total sessions in database...")
            count_result = self.db.execute(text("SELECT COUNT(*) FROM stock_analysis_sessions")).fetchone()
            logger.info(f"📊 Total sessions in database: {count_result[0] if count_result else 'Unknown'}")
            
            # Show recent sessions
            recent_sessions = self.db.execute(
                text("SELECT session_id, stock_symbol, status, created_at FROM stock_analysis_sessions ORDER BY created_at DESC LIMIT 3")
            ).fetchall()
            logger.info(f"📋 Recent sessions in database:")
            for session in recent_sessions:
                logger.info(f"   - {session[0]} | {session[1]} | {session[2]} | {session[3]}")
            
            # Now try the original SQLAlchemy query
            logger.info(f"🗄️ Executing SQLAlchemy query...")
            
            # Build the query step by step for debugging
            base_query = self.db.query(StockAnalysisSession)
            logger.info(f"📝 Base query created")
            
            filtered_query = base_query.filter(StockAnalysisSession.session_id == session_id)
            logger.info(f"📝 Filter applied for session_id: {session_id}")
            
            # Let's see what SQL this generates
            logger.info(f"🔍 Generated SQL: {str(filtered_query)}")
            
            result = (
                self.db.query(StockAnalysisSession)
                .options(
                    selectinload(StockAnalysisSession.agent_analyses),
                    selectinload(StockAnalysisSession.predictions),
                    selectinload(StockAnalysisSession.chat_messages),
                    selectinload(StockAnalysisSession.errors)
                )
                .filter(StockAnalysisSession.session_id == session_id)
                .first()
            )
            logger.info(f"✅ Database query completed. Result: {result is not None}")
            if result:
                logger.info(f"📋 Found session: ID={result.session_id}, Status={result.status}, Symbol={result.stock_symbol}")
            else:
                logger.warning(f"❌ No session found with ID: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"💥 Database query failed with exception: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
            raise
    
    def get_by_workflow_id(self, workflow_id: uuid.UUID) -> Optional[StockAnalysisSession]:
        """Get session by workflow ID"""
        
        return (
            self.db.query(StockAnalysisSession)
            .filter(StockAnalysisSession.workflow_id == workflow_id)
            .first()
        )

class AgentAnalysisRepository(BaseRepository):
    """Repository for agent analysis results"""
    
    def __init__(self, db: Session):
        super().__init__(AgentAnalysis, db)
    
    def create_analysis(
        self,
        session_id: uuid.UUID,
        agent_type: str,
        agent_name: str,
        analysis_text: str,
        processing_time_ms: Optional[int] = None
    ) -> AgentAnalysis:
        """Create a new agent analysis"""
        
        analysis = AgentAnalysis(
            session_id=session_id,
            agent_type=agent_type,
            agent_name=agent_name,
            analysis_text=analysis_text,
            processing_time_ms=processing_time_ms
        )
        
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def get_session_analyses(
        self,
        session_id: uuid.UUID
    ) -> List[AgentAnalysis]:
        """Get all analyses for a session"""
        
        return (
            self.db.query(AgentAnalysis)
            .filter(AgentAnalysis.session_id == session_id)
            .order_by(AgentAnalysis.created_at)
            .all()
        )

class StockPredictionRepository(BaseRepository):
    """Repository for stock predictions"""
    
    def __init__(self, db: Session):
        super().__init__(StockPrediction, db)
    
    def create_predictions(
        self,
        session_id: uuid.UUID,
        predictions: List[Dict[str, Any]]
    ) -> List[StockPrediction]:
        """Create multiple prediction points"""
        
        prediction_objects = []
        
        for i, pred in enumerate(predictions):
            prediction = StockPrediction(
                session_id=session_id,
                prediction_date=datetime.fromisoformat(pred['date'].replace('Z', '+00:00')),
                predicted_price=float(pred['price']),
                prediction_order=i + 1
            )
            prediction_objects.append(prediction)
        
        self.db.add_all(prediction_objects)
        self.db.commit()
        
        for pred in prediction_objects:
            self.db.refresh(pred)
            
        return prediction_objects
    
    def get_session_predictions(
        self,
        session_id: uuid.UUID
    ) -> List[StockPrediction]:
        """Get all predictions for a session"""
        
        return (
            self.db.query(StockPrediction)
            .filter(StockPrediction.session_id == session_id)
            .order_by(StockPrediction.prediction_order)
            .all()
        )

class StockChatMessageRepository(BaseRepository):
    """Repository for chat messages"""
    
    def __init__(self, db: Session):
        super().__init__(StockChatMessage, db)
    
    def create_message(
        self,
        session_id: uuid.UUID,
        message_type: str,
        content: str,
        sender_type: str,
        message_metadata: Optional[Dict[str, Any]] = None
    ) -> StockChatMessage:
        """Create a new chat message"""
        
        message = StockChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            sender_type=sender_type,
            message_metadata=message_metadata
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_session_messages(
        self,
        session_id: uuid.UUID,
        limit: int = 50
    ) -> List[StockChatMessage]:
        """Get chat messages for a session"""
        
        return (
            self.db.query(StockChatMessage)
            .filter(StockChatMessage.session_id == session_id)
            .order_by(StockChatMessage.created_at)
            .limit(limit)
            .all()
        )

class StockAnalysisErrorRepository(BaseRepository):
    """Repository for error logging"""
    
    def __init__(self, db: Session):
        super().__init__(StockAnalysisError, db)
    
    def log_error(
        self,
        session_id: Optional[uuid.UUID],
        error_type: str,
        error_message: str,
        agent_type: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> StockAnalysisError:
        """Log an error"""
        
        error = StockAnalysisError(
            session_id=session_id,
            agent_type=agent_type,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace
        )
        
        self.db.add(error)
        self.db.commit()
        self.db.refresh(error)
        return error