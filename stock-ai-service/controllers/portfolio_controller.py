from fastapi import HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
import logging

from database.base import get_db
from repositories.portfolio_repository import PortfolioRepository
from services.portfolio_service import PortfolioService, PortfolioStockData

logger = logging.getLogger(__name__)

# Request/Response Models
class PortfolioStockRequest(BaseModel):
    symbol: str
    allocation_percentage: float
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Symbol must be 1-10 characters')
        return v.upper()
    
    @validator('allocation_percentage')
    def validate_allocation(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Allocation must be between 0 and 100')
        return v

class PortfolioCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    stocks: List[PortfolioStockRequest]
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v) > 100:
            raise ValueError('Name must be 1-100 characters')
        return v
    
    @validator('stocks')
    def validate_stocks(cls, v):
        if not v:
            raise ValueError('Portfolio must have at least one stock')
        
        total_allocation = sum(stock.allocation_percentage for stock in v)
        if not 99.0 <= total_allocation <= 101.0:
            raise ValueError(f'Total allocation must be ~100%, got {total_allocation}%')
        
        symbols = [stock.symbol for stock in v]
        if len(symbols) != len(set(symbols)):
            raise ValueError('Duplicate symbols not allowed')
        
        return v

class PortfolioUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    stocks: Optional[List[PortfolioStockRequest]] = None
    
    @validator('stocks')
    def validate_stocks(cls, v):
        if v is not None:
            if not v:
                raise ValueError('Portfolio must have at least one stock')
            
            total_allocation = sum(stock.allocation_percentage for stock in v)
            if not 99.0 <= total_allocation <= 101.0:
                raise ValueError(f'Total allocation must be ~100%, got {total_allocation}%')
            
            symbols = [stock.symbol for stock in v]
            if len(symbols) != len(set(symbols)):
                raise ValueError('Duplicate symbols not allowed')
        
        return v

class PortfolioStockResponse(BaseModel):
    symbol: str
    allocation_percentage: float
    
    class Config:
        from_attributes = True

class PortfolioResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
    stocks: List[PortfolioStockResponse]
    stats: Optional[dict] = None
    
    class Config:
        from_attributes = True

class PortfolioController:
    """Controller for portfolio endpoints"""
    
    @staticmethod
    def _get_service(db: Session) -> PortfolioService:
        """Create portfolio service with repository"""
        repository = PortfolioRepository(db)
        return PortfolioService(repository)
    
    @staticmethod
    def _convert_to_response(portfolio) -> PortfolioResponse:
        """Convert portfolio model to response"""
        stocks_response = [
            PortfolioStockResponse(
                symbol=stock.symbol,
                allocation_percentage=float(stock.allocation_percentage)
            )
            for stock in portfolio.stocks
        ]
        
        # Calculate stats
        service = PortfolioService(None)  # Just for stats calculation
        stats = service.calculate_portfolio_stats(portfolio)
        
        return PortfolioResponse(
            id=portfolio.id,
            user_id=portfolio.user_id,
            name=portfolio.name,
            description=portfolio.description,
            is_active=portfolio.is_active,
            created_at=portfolio.created_at.isoformat(),
            updated_at=portfolio.updated_at.isoformat(),
            stocks=stocks_response,
            stats=stats
        )
    
    @staticmethod
    async def create_portfolio(
        portfolio_request: PortfolioCreateRequest, 
        user_id: int = Query(..., description="User ID"),
        db: Session = Depends(get_db)
    ) -> PortfolioResponse:
        """Create a new portfolio"""
        try:
            service = PortfolioController._get_service(db)
            
            # Convert request stocks to service format
            stocks_data = [
                PortfolioStockData(stock.symbol, stock.allocation_percentage)
                for stock in portfolio_request.stocks
            ]
            
            portfolio = service.create_portfolio(
                user_id=user_id,
                name=portfolio_request.name,
                description=portfolio_request.description,
                stocks=stocks_data
            )
            
            return PortfolioController._convert_to_response(portfolio)
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to create portfolio: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create portfolio: {str(e)}")
    
    @staticmethod
    async def get_user_portfolios(
        user_id: int,
        active_only: bool = Query(True, description="Return only active portfolios"),
        include_stats: bool = Query(False, description="Include portfolio statistics"),
        db: Session = Depends(get_db)
    ) -> List[PortfolioResponse]:
        """Get all portfolios for a user"""
        try:
            service = PortfolioController._get_service(db)
            portfolios = service.get_user_portfolios(user_id, active_only)
            
            response = []
            for portfolio in portfolios:
                portfolio_response = PortfolioController._convert_to_response(portfolio)
                if not include_stats:
                    portfolio_response.stats = None
                response.append(portfolio_response)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get user portfolios: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get portfolios: {str(e)}")
    
    @staticmethod
    async def get_portfolio(
        portfolio_id: int,
        user_id: int = Query(..., description="User ID"),
        db: Session = Depends(get_db)
    ) -> PortfolioResponse:
        """Get a specific portfolio"""
        try:
            service = PortfolioController._get_service(db)
            portfolio = service.get_portfolio(portfolio_id, user_id)
            
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            return PortfolioController._convert_to_response(portfolio)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get portfolio: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")
    
    @staticmethod
    async def update_portfolio(
        portfolio_id: int,
        portfolio_update: PortfolioUpdateRequest,
        user_id: int = Query(..., description="User ID"),
        db: Session = Depends(get_db)
    ) -> PortfolioResponse:
        """Update a portfolio"""
        try:
            service = PortfolioController._get_service(db)
            
            # Convert stocks if provided
            stocks_data = None
            if portfolio_update.stocks is not None:
                stocks_data = [
                    PortfolioStockData(stock.symbol, stock.allocation_percentage)
                    for stock in portfolio_update.stocks
                ]
            
            portfolio = service.update_portfolio(
                portfolio_id=portfolio_id,
                user_id=user_id,
                name=portfolio_update.name,
                description=portfolio_update.description,
                is_active=portfolio_update.is_active,
                stocks=stocks_data
            )
            
            return PortfolioController._convert_to_response(portfolio)
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to update portfolio: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update portfolio: {str(e)}")
    
    @staticmethod
    async def delete_portfolio(
        portfolio_id: int,
        user_id: int = Query(..., description="User ID"),
        db: Session = Depends(get_db)
    ) -> dict:
        """Delete a portfolio"""
        try:
            service = PortfolioController._get_service(db)
            success = service.delete_portfolio(portfolio_id, user_id)
            
            if success:
                return {"message": "Portfolio deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="Portfolio not found")
                
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to delete portfolio: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete portfolio: {str(e)}")

def create_portfolio_endpoints(app):
    """Register portfolio endpoints with the FastAPI app"""
    
    @app.post("/portfolios", response_model=PortfolioResponse, tags=["Portfolios"])
    async def create_portfolio(
        portfolio_request: PortfolioCreateRequest, 
        user_id: int = Query(..., description="User ID"),
        db: Session = Depends(get_db)
    ):
        """Create a new portfolio for a user"""
        return await PortfolioController.create_portfolio(portfolio_request, user_id, db)
    
    @app.get("/users/{user_id}/portfolios", response_model=List[PortfolioResponse], tags=["Portfolios"])
    async def get_user_portfolios(
        user_id: int,
        active_only: bool = Query(True, description="Return only active portfolios"),
        include_stats: bool = Query(False, description="Include portfolio statistics"),
        db: Session = Depends(get_db)
    ):
        """Get all portfolios for a user"""
        return await PortfolioController.get_user_portfolios(user_id, active_only, include_stats, db)
    
    @app.get("/portfolios/{portfolio_id}", response_model=PortfolioResponse, tags=["Portfolios"])
    async def get_portfolio(
        portfolio_id: int,
        user_id: int = Query(..., description="User ID"),
        db: Session = Depends(get_db)
    ):
        """Get a specific portfolio"""
        return await PortfolioController.get_portfolio(portfolio_id, user_id, db)
    
    @app.put("/portfolios/{portfolio_id}", response_model=PortfolioResponse, tags=["Portfolios"])
    async def update_portfolio(
        portfolio_id: int,
        portfolio_update: PortfolioUpdateRequest,
        user_id: int = Query(..., description="User ID"),
        db: Session = Depends(get_db)
    ):
        """Update a portfolio"""
        return await PortfolioController.update_portfolio(portfolio_id, portfolio_update, user_id, db)
    
    @app.delete("/portfolios/{portfolio_id}", tags=["Portfolios"])
    async def delete_portfolio(
        portfolio_id: int,
        user_id: int = Query(..., description="User ID"),
        db: Session = Depends(get_db)
    ):
        """Delete a portfolio"""
        return await PortfolioController.delete_portfolio(portfolio_id, user_id, db)