from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models.property import Base

# Create database engine
engine = create_engine(
    settings.property_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Property service database tables created successfully")