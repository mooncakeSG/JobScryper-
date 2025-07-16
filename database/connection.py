"""
Auto Applyer - Database Connection Management

Handles database connections, session management, and initialization
for both SQLite (development) and PostgreSQL (production) databases.
"""

import os
import logging
from typing import Optional, Generator, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path

from .models import Base
from utils.errors import DatabaseError, ConfigurationError
from utils.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseConfig:
    """Database configuration management."""
    
    def __init__(self, environment: str = None):
        """
        Initialize database configuration.
        
        Args:
            environment: Environment name (development, testing, production)
        """
        self.environment = environment or os.getenv('ENVIRONMENT', 'development')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration based on environment."""
        # Use DATABASE_URL from environment if set
        env_database_url = os.getenv('DATABASE_URL')
        if env_database_url:
            return {
                'database_url': env_database_url,
                'echo': False,
                'pool_pre_ping': True,
                'connect_args': {
                    'check_same_thread': False,
                    'isolation_level': None
                }
            }
        
        if self.environment == 'testing':
            return {
                'database_url': 'sqlite:///:memory:',
                'echo': False,
                'pool_pre_ping': True,
                'connect_args': {
                    'check_same_thread': False,
                    'isolation_level': None
                }
            }
        
        elif self.environment == 'development':
            # SQLite for development
            db_path = Path('data/auto_applyer.db')
            db_path.parent.mkdir(exist_ok=True)
            
            return {
                'database_url': f'sqlite:///{db_path}',
                'echo': os.getenv('DATABASE_ECHO', 'false').lower() == 'true',
                'pool_pre_ping': True,
                'connect_args': {
                    'check_same_thread': False
                }
            }
        
        elif self.environment == 'production':
            # SQLite Cloud for production (sqlitecloud.io) - Direct connection approach
            sqlite_cloud_config = {
                'host': os.getenv('SQLITE_CLOUD_HOST', ''),
                'port': os.getenv('SQLITE_CLOUD_PORT', '8860'),
                'database': os.getenv('SQLITE_CLOUD_DATABASE', 'auto_applyer'),
                'api_key': os.getenv('SQLITE_CLOUD_API_KEY', ''),
            }
            
            # Validate required SQLite Cloud config
            if not all([sqlite_cloud_config['host'], sqlite_cloud_config['api_key']]):
                raise ConfigurationError(
                    "Production SQLite Cloud requires SQLITE_CLOUD_HOST and SQLITE_CLOUD_API_KEY environment variables"
                )
            
            # SQLite Cloud connection URL format: sqlitecloud://host:port/database?apikey=key
            database_url = (
                f"sqlitecloud://{sqlite_cloud_config['host']}:{sqlite_cloud_config['port']}"
                f"/{sqlite_cloud_config['database']}?apikey={sqlite_cloud_config['api_key']}"
            )
            
            return {
                'database_url': database_url,
                'echo': False,
                'pool_size': int(os.getenv('DATABASE_POOL_SIZE', '10')),
                'max_overflow': int(os.getenv('DATABASE_MAX_OVERFLOW', '20')),
                'pool_pre_ping': True,
                'pool_recycle': int(os.getenv('DATABASE_POOL_RECYCLE', '3600')),
                'connect_args': {
                    'connect_timeout': int(os.getenv('DATABASE_TIMEOUT', '30')),
                    'application_name': 'auto_applyer'
                }
            }
        
        else:
            raise ConfigurationError(f"Unknown environment: {self.environment}")


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, config: DatabaseConfig = None):
        """
        Initialize database manager.
        
        Args:
            config: Database configuration object
        """
        self.config = config or DatabaseConfig()
        self.engine: Optional[Engine] = None
        self.session_factory: Optional[sessionmaker] = None
        self.scoped_session_factory: Optional[scoped_session] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the database engine and session factory."""
        try:
            logger.info(f"Initializing database for environment: {self.config.environment}")
            
            # Create engine
            self.engine = create_engine(
                self.config.config['database_url'],
                **{k: v for k, v in self.config.config.items() if k != 'database_url'}
            )
            
            # Set up SQLite optimizations if using SQLite
            if self.config.config['database_url'].startswith('sqlite'):
                self._setup_sqlite_optimizations()
            
            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            # Create scoped session factory for thread-safe access
            self.scoped_session_factory = scoped_session(self.session_factory)
            
            # Test connection
            self._test_connection()
            
            self._initialized = True
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def _setup_sqlite_optimizations(self) -> None:
        """Set up SQLite-specific optimizations."""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for performance and reliability."""
            cursor = dbapi_connection.cursor()
            
            # Performance optimizations
            cursor.execute("PRAGMA journal_mode=WAL")      # Write-Ahead Logging
            cursor.execute("PRAGMA synchronous=NORMAL")    # Balanced durability/performance
            cursor.execute("PRAGMA cache_size=10000")      # Larger cache
            cursor.execute("PRAGMA temp_store=memory")     # Temp tables in memory
            cursor.execute("PRAGMA mmap_size=268435456")   # Memory-mapped I/O (256MB)
            
            # Foreign key support
            cursor.execute("PRAGMA foreign_keys=ON")
            
            cursor.close()
    
    def _test_connection(self) -> None:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.debug("Database connection test successful")
        except Exception as e:
            raise DatabaseError(f"Database connection test failed: {e}")
    
    def create_tables(self, drop_existing: bool = False) -> None:
        """
        Create database tables.
        
        Args:
            drop_existing: Whether to drop existing tables first
        """
        if not self._initialized:
            raise DatabaseError("DatabaseManager not initialized")
        
        try:
            if drop_existing:
                logger.warning("Dropping existing database tables")
                Base.metadata.drop_all(self.engine)
            
            logger.info("Creating database tables")
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise DatabaseError(f"Failed to create tables: {e}")
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy session object
        """
        if not self._initialized:
            raise DatabaseError("DatabaseManager not initialized")
        
        return self.session_factory()
    
    def get_scoped_session(self) -> scoped_session:
        """
        Get a scoped session (thread-safe).
        
        Returns:
            Scoped session object
        """
        if not self._initialized:
            raise DatabaseError("DatabaseManager not initialized")
        
        return self.scoped_session_factory
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        
        Yields:
            Database session
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def close(self) -> None:
        """Close all database connections."""
        if self.scoped_session_factory:
            self.scoped_session_factory.remove()
        
        if self.engine:
            self.engine.dispose()
        
        self._initialized = False
        logger.info("Database connections closed")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        try:
            with self.session_scope() as session:
                # Get table information
                if self.config.config['database_url'].startswith('sqlite'):
                    result = session.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """))
                    tables = [row[0] for row in result]
                    
                    # Get database size for SQLite
                    db_size_result = session.execute(text("PRAGMA page_count"))
                    page_count = db_size_result.scalar()
                    
                    page_size_result = session.execute(text("PRAGMA page_size"))
                    page_size = page_size_result.scalar()
                    
                    db_size = (page_count * page_size) if page_count and page_size else 0
                    
                else:
                    # PostgreSQL
                    result = session.execute(text("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """))
                    tables = [row[0] for row in result]
                    
                    # Get database size for PostgreSQL
                    size_result = session.execute(text(
                        f"SELECT pg_size_pretty(pg_database_size('{self.config.config['database_url'].split('/')[-1]}'))"
                    ))
                    db_size = size_result.scalar()
                
                # Determine database type
                if self.config.config['database_url'].startswith('sqlite+sqlitecloud'):
                    database_type = "sqlite_cloud"
                elif self.config.config['database_url'].startswith('sqlite'):
                    database_type = "sqlite"
                else:
                    database_type = "postgresql"
                
                return {
                    "status": "connected",
                    "environment": self.config.environment,
                    "database_type": database_type,
                    "tables": tables,
                    "table_count": len(tables),
                    "database_size": db_size,
                    "engine_info": {
                        "pool_size": getattr(self.engine.pool, 'size', None),
                        "checked_out": getattr(self.engine.pool, 'checkedout', None),
                        "overflow": getattr(self.engine.pool, 'overflow', None),
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def init_database(environment: str = None, drop_existing: bool = False) -> DatabaseManager:
    """
    Initialize the global database manager.
    
    Args:
        environment: Environment name
        drop_existing: Whether to drop existing tables
        
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    
    config = DatabaseConfig(environment)
    _db_manager = DatabaseManager(config)
    _db_manager.initialize()
    
    # Create tables if they don't exist
    _db_manager.create_tables(drop_existing=drop_existing)
    
    return _db_manager


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance, initializing if needed."""
    global _db_manager
    if '_db_manager' not in globals() or _db_manager is None:
        _db_manager = DatabaseManager()
    if not _db_manager._initialized:
        _db_manager.initialize()
    return _db_manager


def get_db_session() -> Session:
    """
    Get a new database session.
    
    Returns:
        SQLAlchemy session
    """
    return get_database_manager().get_session()


@contextmanager
def db_session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around database operations.
    
    Yields:
        Database session
    """
    with get_database_manager().session_scope() as session:
        yield session


# Cleanup function for application shutdown
def cleanup_database() -> None:
    """Clean up database connections on application shutdown."""
    global _db_manager
    
    if _db_manager:
        _db_manager.close()
        _db_manager = None 