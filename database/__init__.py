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

from .connection import DatabaseManager, get_db_session, init_database
from .models import User, JobApplication, Resume, SearchHistory, UserPreferences, ApplicationStatus
from .utilities import DatabaseUtils, BackupManager
from .migrations import MigrationManager

# Unified DB backend selection
if os.getenv('ENVIRONMENT', 'development') == 'production':
    from .cloud_driver import fetchall, fetchone, execute
    def get_db_backend():
        return 'cloud'
else:
    from .utilities import DatabaseUtils
    def fetchall(query, params=None):
        # For dev: use SQLAlchemy session
        with DatabaseUtils.get_session() as session:
            result = session.execute(query, params or {})
            return result.fetchall()
    def fetchone(query, params=None):
        with DatabaseUtils.get_session() as session:
            result = session.execute(query, params or {})
            return result.fetchone()
    def execute(query, params=None):
        with DatabaseUtils.get_session() as session:
            result = session.execute(query, params or {})
            session.commit()
            return result
    def get_db_backend():
        return 'sqlalchemy'

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