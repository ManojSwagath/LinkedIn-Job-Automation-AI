"""
Database Connection Manager for AutoAgentHire
Supports both PostgreSQL and SQLite
"""

import os
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import models
from backend.database.models_complete import Base

# Database URL Configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///./data/autoagenthire.db'  # Default to SQLite for development
)

# For SQLite, use check_same_thread=False
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv('DEBUG', 'False').lower() == 'true'
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=os.getenv('DEBUG', 'False').lower() == 'true'
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    try:
        # Ensure data directory exists
        db_path = Path('./data')
        db_path.mkdir(parents=True, exist_ok=True)
        
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        print("Continuing without database initialization...")


def drop_db():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped")


def get_db() -> Generator[Session, None, None]:
    """Get database session (dependency injection for FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class DatabaseManager:
    """Database manager class for advanced operations"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_session(self) -> Session:
        """Create a new database session"""
        return self.SessionLocal()
    
    def init_tables(self):
        """Initialize all database tables"""
        init_db()
    
    def reset_database(self):
        """Reset database (drop and recreate all tables)"""
        drop_db()
        init_db()
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            from sqlalchemy import text
            with self.create_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"❌ Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


# SQLite specific optimizations
if DATABASE_URL.startswith('sqlite'):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Enable foreign keys and WAL mode for SQLite"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
