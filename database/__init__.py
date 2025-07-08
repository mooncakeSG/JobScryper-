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

from .connection import DatabaseManager, get_db_session, init_database
from .models import User, JobApplication, Resume, SearchHistory, UserPreferences, ApplicationStatus
from .utilities import DatabaseUtils, BackupManager
from .migrations import MigrationManager

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