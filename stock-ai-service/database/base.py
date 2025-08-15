from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Create declarative base for stock AI service using SQLAlchemy 2.0 pattern
class Base(DeclarativeBase):
    pass

# Database URL for stock AI service
DATABASE_URL = os.getenv(
    "STOCK_DATABASE_URL", 
    "postgresql://stock_user:stock_password@localhost/stock_ai"
)

# Create engine for stock AI service
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session for stock AI service"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_tables():
    """Create all tables for stock AI service"""
    Base.metadata.create_all(bind=engine)