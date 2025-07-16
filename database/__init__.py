"""
Auto Applyer - Database Package

This package provides comprehensive database functionality including:
- SQLAlchemy models for all application data
- Database connection management
- Migration system
- User management and authentication
- Job application tracking
- Data backup and restore
"""

import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

from .connection import DatabaseManager, get_db_session, init_database
from .models import User, JobApplication, Resume, SearchHistory, UserPreferences, ApplicationStatus
from .utilities import DatabaseUtils, BackupManager
from .migrations import MigrationManager

# Database file path
DB_PATH = Path('data/auto_applyer.db')

@contextmanager
def get_sqlite_connection():
    """Get a SQLite connection for development mode."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
    finally:
        conn.close()

# Unified DB backend selection
if os.getenv('ENVIRONMENT', 'development') == 'production':
    from .cloud_driver import fetchall, fetchone, execute
    def get_db_backend():
        return 'cloud'
else:
    # Development mode: use simple SQLite
    def fetchall(query, params=None):
        with get_sqlite_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.fetchall()
    
    def fetchone(query, params=None):
        with get_sqlite_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.fetchone()
    
    def execute(query, params=None):
        with get_sqlite_connection() as conn:
            cursor = conn.execute(query, params or ())
            conn.commit()
            # Return last inserted row ID for INSERT operations
            if query.strip().upper().startswith('INSERT'):
                return cursor.lastrowid
            return cursor
    
    def get_db_backend():
        return 'sqlite'

# Package version
__version__ = "1.0.0"

# Export main components
__all__ = [
    # Connection management
    'DatabaseManager',
    'get_db_session',
    'init_database',
    
    # Models
    'User',
    'JobApplication', 
    'Resume',
    'SearchHistory',
    'UserPreferences',
    'ApplicationStatus',
    
    # Utilities
    'DatabaseUtils',
    'BackupManager',
    'MigrationManager'
] 
__all__ += ['fetchall', 'fetchone', 'execute', 'get_db_backend'] 