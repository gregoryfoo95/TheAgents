from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import logging

from database.models import Portfolio, PortfolioStock

logger = logging.getLogger(__name__)

class PortfolioRepository:
    """Repository for portfolio database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_portfolio(self, user_id: int, name: str, description: Optional[str] = None) -> Portfolio:
        """Create a new portfolio"""
        portfolio = Portfolio(
            user_id=user_id,
            name=name,
            description=description
        )
        self.db.add(portfolio)
        self.db.flush()  # Get the ID without committing
        return portfolio
    
    def add_portfolio_stock(self, portfolio_id: int, symbol: str, allocation_percentage: float) -> PortfolioStock:
        """Add a stock to a portfolio"""
        portfolio_stock = PortfolioStock(
            portfolio_id=portfolio_id,
            symbol=symbol.upper(),
            allocation_percentage=Decimal(str(allocation_percentage))
        )
        self.db.add(portfolio_stock)
        return portfolio_stock
    
    def get_portfolio_by_id(self, portfolio_id: int, user_id: int) -> Optional[Portfolio]:
        """Get a portfolio by ID for a specific user"""
        return self.db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id
        ).first()
    
    def get_user_portfolios(self, user_id: int, active_only: bool = True) -> List[Portfolio]:
        """Get all portfolios for a user"""
        query = self.db.query(Portfolio).filter(Portfolio.user_id == user_id)
        if active_only:
            query = query.filter(Portfolio.is_active == True)
        return query.order_by(Portfolio.created_at.desc()).all()
    
    def update_portfolio(self, portfolio: Portfolio, name: Optional[str] = None, 
                        description: Optional[str] = None, is_active: Optional[bool] = None) -> Portfolio:
        """Update portfolio basic information"""
        if name is not None:
            portfolio.name = name
        if description is not None:
            portfolio.description = description
        if is_active is not None:
            portfolio.is_active = is_active
        
        self.db.flush()
        return portfolio
    
    def remove_all_portfolio_stocks(self, portfolio_id: int) -> None:
        """Remove all stocks from a portfolio"""
        self.db.query(PortfolioStock).filter(
            PortfolioStock.portfolio_id == portfolio_id
        ).delete()
    
    def soft_delete_portfolio(self, portfolio: Portfolio) -> Portfolio:
        """Soft delete a portfolio by setting is_active to False"""
        portfolio.is_active = False
        self.db.flush()
        return portfolio
    
    def commit(self):
        """Commit the transaction"""
        self.db.commit()
    
    def rollback(self):
        """Rollback the transaction"""
        self.db.rollback()
    
    def refresh(self, portfolio: Portfolio):
        """Refresh portfolio from database"""
        self.db.refresh(portfolio)