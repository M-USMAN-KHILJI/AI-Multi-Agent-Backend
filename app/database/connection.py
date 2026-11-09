import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

# Normalize PostgreSQL scheme for SQLAlchemy
database_url = settings.DATABASE_URL
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+psycopg2://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create engine
engine = None
SessionLocal = None

if database_url:
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("SQLAlchemy database engine initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")
else:
    logger.warning("DATABASE_URL is not set. Database operations will be disabled.")

Base = declarative_base()

def get_db():
    """
    FastAPI dependency yielding database session per request.
    """
    if SessionLocal is None:
        raise RuntimeError("Database is not configured. Please set DATABASE_URL.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

