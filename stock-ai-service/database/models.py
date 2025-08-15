from sqlalchemy import Column, String, Integer, DateTime, Text, DECIMAL, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base
import uuid

class StockAnalysisSession(Base):
    """Stock analysis sessions - owned by Stock AI service"""
    __tablename__ = "stock_analysis_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)  # Reference to main backend user (no FK)
    # Analysis can be for single stock or portfolio
    analysis_type = Column(String(20), default="stock")  # "stock" or "portfolio"
    stock_symbol = Column(String(50))  # For single stock or portfolio summary
    portfolio_data = Column(JSONB)  # For portfolio analysis: [{"symbol": "AAPL", "allocation": 30.0}, ...]
    time_frequency = Column(String(10), nullable=False)
    workflow_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    confidence_score = Column(DECIMAL(3,2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships within stock AI service
    agent_analyses = relationship("AgentAnalysis", back_populates="session", cascade="all, delete-orphan")
    predictions = relationship("StockPrediction", back_populates="session", cascade="all, delete-orphan")
    chat_messages = relationship("StockChatMessage", back_populates="session", cascade="all, delete-orphan")
    errors = relationship("StockAnalysisError", back_populates="session", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", name="chk_status"),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="chk_confidence"),
    )

class AgentAnalysis(Base):
    """Agent analysis results"""
    __tablename__ = "agent_analyses"
    
    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("stock_analysis_sessions.session_id", ondelete="CASCADE"), nullable=False)
    agent_type = Column(String(50), nullable=False)
    agent_name = Column(String(100), nullable=False)
    analysis_text = Column(Text, nullable=False)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("StockAnalysisSession", back_populates="agent_analyses")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("agent_type IN ('finance_guru', 'geopolitics_guru', 'legal_guru', 'quant_dev', 'financial_analyst')", name="chk_agent_type"),
    )

class StockPrediction(Base):
    """Stock price predictions"""
    __tablename__ = "stock_predictions"
    
    prediction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("stock_analysis_sessions.session_id", ondelete="CASCADE"), nullable=False)
    prediction_date = Column(DateTime(timezone=True), nullable=False)
    predicted_price = Column(DECIMAL(10,2), nullable=False)
    prediction_order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("StockAnalysisSession", back_populates="predictions")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("predicted_price > 0", name="chk_price_positive"),
    )

class StockChatMessage(Base):
    """Chat messages for stock analysis sessions"""
    __tablename__ = "stock_chat_messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("stock_analysis_sessions.session_id", ondelete="CASCADE"), nullable=False)
    message_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    sender_type = Column(String(20), nullable=False)
    message_metadata = Column(JSONB)  # Renamed from metadata to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("StockAnalysisSession", back_populates="chat_messages")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("message_type IN ('user_query', 'agent_response', 'system_message', 'prediction_result')", name="chk_message_type"),
        CheckConstraint("sender_type IN ('user', 'ai_agent', 'system')", name="chk_sender_type"),
    )

class StockAnalysisError(Base):
    """Error logs for stock analysis"""
    __tablename__ = "stock_analysis_errors"
    
    error_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("stock_analysis_sessions.session_id", ondelete="CASCADE"))
    agent_type = Column(String(50))
    error_type = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("StockAnalysisSession", back_populates="errors")

# Portfolio Management Models
class Portfolio(Base):
    """User portfolios managed by Stock-AI Service"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to user from auth service
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    stocks = relationship("PortfolioStock", back_populates="portfolio", cascade="all, delete-orphan")
    analysis_sessions = relationship("PortfolioAnalysisSession", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', user_id={self.user_id})>"

class PortfolioStock(Base):
    """Stocks within portfolios with allocation percentages"""
    __tablename__ = "portfolio_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), nullable=False)
    allocation_percentage = Column(DECIMAL(5, 2), nullable=False)  # 0.00 to 100.00
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="stocks")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("allocation_percentage >= 0 AND allocation_percentage <= 100", name="chk_allocation_range"),
    )
    
    def __repr__(self):
        return f"<PortfolioStock(portfolio_id={self.portfolio_id}, symbol='{self.symbol}', allocation={self.allocation_percentage}%)>"

class PortfolioAnalysisSession(Base):
    """Portfolio analysis sessions linking portfolios to analysis results"""
    __tablename__ = "portfolio_analysis_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    analysis_session_id = Column(UUID(as_uuid=True), ForeignKey("stock_analysis_sessions.session_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="analysis_sessions")
    analysis_session = relationship("StockAnalysisSession")
    
    def __repr__(self):
        return f"<PortfolioAnalysisSession(portfolio_id={self.portfolio_id}, session_id={self.analysis_session_id})>"