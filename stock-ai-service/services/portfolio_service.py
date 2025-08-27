from typing import List, Optional, Dict, Any
from decimal import Decimal
import logging

from repositories.portfolio_repository import PortfolioRepository
from database.models import Portfolio, PortfolioStock

logger = logging.getLogger(__name__)

class PortfolioStockData:
    """Data class for portfolio stock information"""
    def __init__(self, symbol: str, allocation_percentage: float):
        self.symbol = symbol.upper()
        self.allocation_percentage = allocation_percentage
        
        # Validation
        if not symbol or len(symbol) > 10:
            raise ValueError("Symbol must be 1-10 characters")
        if not 0 <= allocation_percentage <= 100:
            raise ValueError("Allocation must be between 0 and 100")

class PortfolioService:
    """Business logic for portfolio management"""
    
    def __init__(self, repository: PortfolioRepository):
        self.repository = repository
    
    def validate_portfolio_allocation(self, stocks: List[PortfolioStockData]) -> None:
        """Validate that portfolio allocations sum to ~100%"""
        if not stocks:
            raise ValueError("Portfolio must have at least one stock")
        
        total_allocation = sum(stock.allocation_percentage for stock in stocks)
        if not 99.0 <= total_allocation <= 101.0:
            raise ValueError(f"Total allocation must be ~100%, got {total_allocation}%")
        
        # Check for duplicate symbols
        symbols = [stock.symbol for stock in stocks]
        if len(symbols) != len(set(symbols)):
            raise ValueError("Duplicate symbols not allowed")
    
    def create_portfolio(self, user_id: int, name: str, description: Optional[str], 
                        stocks: List[PortfolioStockData]) -> Portfolio:
        """Create a new portfolio with stocks"""
        try:
            # Validate inputs
            if not name or len(name) > 100:
                raise ValueError("Name must be 1-100 characters")
            
            self.validate_portfolio_allocation(stocks)
            
            # Create portfolio
            portfolio = self.repository.create_portfolio(user_id, name, description)
            
            # Add stocks
            for stock_data in stocks:
                self.repository.add_portfolio_stock(
                    portfolio.id, 
                    stock_data.symbol, 
                    stock_data.allocation_percentage
                )
            
            self.repository.commit()
            self.repository.refresh(portfolio)
            
            logger.info(f"Created portfolio '{name}' for user {user_id} with {len(stocks)} stocks")
            return portfolio
            
        except Exception as e:
            self.repository.rollback()
            logger.error(f"Failed to create portfolio: {str(e)}")
            raise
    
    def get_user_portfolios(self, user_id: int, active_only: bool = True) -> List[Portfolio]:
        """Get all portfolios for a user"""
        try:
            portfolios = self.repository.get_user_portfolios(user_id, active_only)
            logger.info(f"Retrieved {len(portfolios)} portfolios for user {user_id}")
            return portfolios
        except Exception as e:
            logger.error(f"Failed to get portfolios for user {user_id}: {str(e)}")
            raise
    
    def get_portfolio(self, portfolio_id: int, user_id: int) -> Optional[Portfolio]:
        """Get a specific portfolio"""
        try:
            portfolio = self.repository.get_portfolio_by_id(portfolio_id, user_id)
            if portfolio:
                logger.info(f"Retrieved portfolio {portfolio_id} for user {user_id}")
            else:
                logger.warning(f"Portfolio {portfolio_id} not found for user {user_id}")
            return portfolio
        except Exception as e:
            logger.error(f"Failed to get portfolio {portfolio_id}: {str(e)}")
            raise
    
    def update_portfolio(self, portfolio_id: int, user_id: int, name: Optional[str] = None,
                        description: Optional[str] = None, is_active: Optional[bool] = None,
                        stocks: Optional[List[PortfolioStockData]] = None) -> Portfolio:
        """Update a portfolio"""
        try:
            # Get existing portfolio
            portfolio = self.repository.get_portfolio_by_id(portfolio_id, user_id)
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            # Validate new stocks if provided
            if stocks is not None:
                self.validate_portfolio_allocation(stocks)
            
            # Validate name if provided
            if name is not None and (not name or len(name) > 100):
                raise ValueError("Name must be 1-100 characters")
            
            # Update basic portfolio information
            self.repository.update_portfolio(portfolio, name, description, is_active)
            
            # Update stocks if provided
            if stocks is not None:
                # Remove existing stocks
                self.repository.remove_all_portfolio_stocks(portfolio_id)
                
                # Add new stocks
                for stock_data in stocks:
                    self.repository.add_portfolio_stock(
                        portfolio_id, 
                        stock_data.symbol, 
                        stock_data.allocation_percentage
                    )
            
            self.repository.commit()
            self.repository.refresh(portfolio)
            
            logger.info(f"Updated portfolio {portfolio_id} for user {user_id}")
            return portfolio
            
        except Exception as e:
            self.repository.rollback()
            logger.error(f"Failed to update portfolio {portfolio_id}: {str(e)}")
            raise
    
    def delete_portfolio(self, portfolio_id: int, user_id: int) -> bool:
        """Soft delete a portfolio"""
        try:
            portfolio = self.repository.get_portfolio_by_id(portfolio_id, user_id)
            if not portfolio:
                raise ValueError("Portfolio not found")
            
            self.repository.soft_delete_portfolio(portfolio)
            self.repository.commit()
            
            logger.info(f"Deleted portfolio {portfolio_id} for user {user_id}")
            return True
            
        except Exception as e:
            self.repository.rollback()
            logger.error(f"Failed to delete portfolio {portfolio_id}: {str(e)}")
            raise
    
    def get_portfolio_for_analysis(self, portfolio: Portfolio) -> List[Dict[str, Any]]:
        """Convert portfolio to analysis format"""
        return [
            {
                "symbol": stock.symbol,
                "allocation": float(stock.allocation_percentage)
            }
            for stock in portfolio.stocks
        ]
    
    def calculate_portfolio_stats(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Calculate basic portfolio statistics"""
        stocks = portfolio.stocks
        if not stocks:
            return {
                "total_stocks": 0,
                "total_allocation": 0.0,
                "largest_position": None,
                "smallest_position": None
            }
        
        allocations = [float(stock.allocation_percentage) for stock in stocks]
        total_allocation = sum(allocations)
        
        largest_stock = max(stocks, key=lambda s: s.allocation_percentage)
        smallest_stock = min(stocks, key=lambda s: s.allocation_percentage)
        
        return {
            "total_stocks": len(stocks),
            "total_allocation": total_allocation,
            "largest_position": {
                "symbol": largest_stock.symbol,
                "allocation": float(largest_stock.allocation_percentage)
            },
            "smallest_position": {
                "symbol": smallest_stock.symbol,
                "allocation": float(smallest_stock.allocation_percentage)
            }
        }