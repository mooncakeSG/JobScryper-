"""
Database connection utilities for Auto Applyer
Supports both SQLite (local development) and PostgreSQL (cloud deployment)
"""

import os
import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator, Optional
from urllib.parse import urlparse
import psycopg2
import psycopg2.extras
from fastapi import HTTPException

# Try to import psycopg2 for PostgreSQL support
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors"""
    pass

class DatabaseNotSupportedError(Exception):
    """Exception raised when database type is not supported"""
    pass

@contextmanager
def cloud_db_connection() -> Generator:
    """
    Context manager for database connections.
    Yields the connection object (not the cursor).
    Usage:
        with cloud_db_connection() as conn:
            conn.execute(...)
            conn.commit()
    """
    connection = None
    cursor = None
    
    try:
        # Always use SQLite Cloud
        database_url = "sqlitecloud://czdyoyrynz.g4.sqlite.cloud:8860/auto-applyer?apikey=3KWvb3v84ZydV0FLHM6PDL2taY9NyOdaZiZ7QnPQKNM"
        logger.info("Using SQLite Cloud database")
        
        # Parse the database URL
        parsed_url = urlparse(database_url)
        db_type = parsed_url.scheme.lower()
        
        if db_type == "sqlite":
            # SQLite connection
            db_path = parsed_url.path.lstrip('/')
            if not db_path:
                db_path = "auto_applyer.db"
            
            logger.debug(f"Connecting to SQLite database: {db_path}")
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row  # Enable dict-like access
            
        elif db_type in ["postgresql", "postgres"]:
            # PostgreSQL connection
            if not PSYCOPG2_AVAILABLE:
                raise DatabaseNotSupportedError(
                    "PostgreSQL support requires psycopg2. "
                    "Install with: pip install psycopg2-binary"
                )
            
            # Extract connection parameters from URL
            host = parsed_url.hostname or "localhost"
            port = parsed_url.port or 5432
            database = parsed_url.path.lstrip('/') or "auto_applyer"
            username = parsed_url.username or "postgres"
            password = parsed_url.password or ""
            
            logger.debug(f"Connecting to PostgreSQL database: {database} on {host}:{port}")
            
            connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            
        elif db_type == "sqlitecloud":
            # SQLite Cloud connection
            try:
                import sqlitecloud
                logger.debug(f"Connecting to SQLite Cloud database: {database_url}")
                connection = sqlitecloud.connect(database_url)
                # SQLite Cloud doesn't support row_factory, so we'll handle it differently
            except ImportError:
                raise DatabaseNotSupportedError(
                    "SQLite Cloud support requires sqlitecloud. "
                    "Install with: pip install sqlitecloud"
                )
            
        else:
            raise DatabaseNotSupportedError(
                f"Unsupported database type: {db_type}. "
                "Supported types: sqlite, postgresql, postgres, sqlitecloud"
            )
        
        logger.debug("Database connection established successfully")
        yield connection
        
        # Commit changes if connection is still open
        if connection:
            if hasattr(connection, 'closed'):
                # PostgreSQL connection
                if not connection.closed:
                    connection.commit()
                    logger.debug("Database changes committed")
            else:
                # SQLite connection
                connection.commit()
                logger.debug("Database changes committed")
            
    except (sqlite3.Error, psycopg2.Error, Exception) as e:
        # Database-specific errors
        error_msg = f"Database error: {str(e)}"
        logger.error(error_msg)
        if connection:
            if hasattr(connection, 'closed'):
                # PostgreSQL connection
                if not connection.closed:
                    connection.rollback()
                    logger.debug("Database changes rolled back")
            else:
                # SQLite connection
                connection.rollback()
                logger.debug("Database changes rolled back")
        raise DatabaseConnectionError(error_msg) from e
        
    except HTTPException:
        # Re-raise HTTPException without wrapping it
        raise
        
    except Exception as e:
        # Other errors (network, configuration, etc.)
        error_msg = f"Connection error: {str(e)}"
        logger.error(error_msg)
        if connection:
            if hasattr(connection, 'closed'):
                # PostgreSQL connection
                if not connection.closed:
                    connection.rollback()
                    logger.debug("Database changes rolled back")
            else:
                # SQLite connection
                connection.rollback()
                logger.debug("Database changes rolled back")
        raise DatabaseConnectionError(error_msg) from e
        
    finally:
        # Clean up resources
        try:
            if connection:
                # Handle different connection types
                if hasattr(connection, 'closed'):
                    # PostgreSQL connection
                    if not connection.closed:
                        connection.close()
                        logger.debug("Database connection closed")
                else:
                    # SQLite connection
                    connection.close()
                    logger.debug("Database connection closed")
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")

def fetch_user_by_username_or_email(identifier: str) -> Optional[tuple]:
    """
    Fetch user by username or email.
    
    Args:
        identifier: Username or email to search for
        
    Returns:
        tuple: User data (id, username, email, ...) or None if not found
    """
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            # Try to find user by username or email
            cursor.execute("""
                SELECT id, username, password_hash, email, is_active, is_verified, 
                       created_at, resume_text
                FROM users 
                WHERE username = ? OR email = ?
            """, (identifier, identifier))
            
            result = cursor.fetchone()
            return result if result else None
            
    except Exception as e:
        logger.error(f"Error fetching user {identifier}: {str(e)}")
        return None

def create_user(username: str, email: str, password_hash: str) -> Optional[int]:
    """
    Create a new user in the database.
    
    Args:
        username: Username for the new user
        email: Email for the new user
        password_hash: Hashed password
        
    Returns:
        int: User ID if successful, None otherwise
    """
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, created_at, is_verified, is_active)
                VALUES (?, ?, ?, datetime('now'), 0, 1)
            """, (username, email, password_hash))
            
            return cursor.lastrowid
            
    except Exception as e:
        logger.error(f"Error creating user {username}: {str(e)}")
        return None

def update_user_resume_text(user_id: int, resume_text: str) -> bool:
    """
    Update user's resume text.
    
    Args:
        user_id: User ID to update
        resume_text: New resume text
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET resume_text = ?
                WHERE id = ?
            """, (resume_text, user_id))
            
            return cursor.rowcount > 0
            
    except Exception as e:
        logger.error(f"Error updating resume text for user {user_id}: {str(e)}")
        return False

# Initialize database tables if they don't exist
def init_database():
    """Initialize database tables if they don't exist."""
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    resume_text TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    two_fa_enabled BOOLEAN DEFAULT FALSE,
                    two_fa_secret TEXT,
                    backup_codes TEXT,
                    email_verification_code TEXT,
                    email_verification_expires DATETIME,
                    email_verified BOOLEAN DEFAULT FALSE,
                    social_provider TEXT,
                    social_id TEXT,
                    profile_picture TEXT,
                    failed_login_attempts INTEGER DEFAULT 0,
                    password_changed_at DATETIME,
                    last_login DATETIME
                )
            """)
            
            # Create job_applications table (renamed from applications)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    status TEXT DEFAULT 'applied',
                    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    job_url TEXT,
                    interview_date DATETIME,
                    notes TEXT,
                    match_score FLOAT DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create saved_jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_id TEXT,
                    job_url TEXT,
                    job_data TEXT NOT NULL,
                    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create user_preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    preferred_job_titles TEXT,
                    preferred_locations TEXT,
                    preferred_job_types TEXT,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    salary_currency TEXT DEFAULT 'USD',
                    remote_work_preference BOOLEAN DEFAULT FALSE,
                    max_results_per_search INTEGER DEFAULT 50,
                    auto_apply_enabled BOOLEAN DEFAULT FALSE,
                    job_sources TEXT,
                    email_notifications BOOLEAN DEFAULT TRUE,
                    application_reminders BOOLEAN DEFAULT TRUE,
                    daily_job_alerts BOOLEAN DEFAULT FALSE,
                    ai_suggestions_enabled BOOLEAN DEFAULT TRUE,
                    ats_analysis_enabled BOOLEAN DEFAULT TRUE,
                    auto_resume_optimization BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create activities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    activity_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    entity_type TEXT,
                    entity_id INTEGER,
                    activity_metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create password_reset_tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token_hash TEXT UNIQUE NOT NULL,
                    expires_at DATETIME NOT NULL,
                    used_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_applications_user_id ON job_applications(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_id ON saved_jobs(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_hash ON password_reset_tokens(token_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            
            logger.info("Database tables initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise 

# Auto-initialize database when module is imported
if __name__ != "__main__":
    try:
        init_database()
    except Exception as e:
        logger.warning(f"Could not auto-initialize database: {str(e)}") 