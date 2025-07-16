"""
Database connection pooling for better performance
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
import threading
from queue import Queue, Empty
import time

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """Connection pool for database connections"""
    
    def __init__(self, max_connections=10, timeout=30):
        self.max_connections = max_connections
        self.timeout = timeout
        self.connections = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            # Try to get an existing connection
            connection = self.connections.get(timeout=1)
            logger.debug("Reused existing database connection")
            return connection
        except Empty:
            # Create new connection if pool is empty
            with self.lock:
                if self.active_connections < self.max_connections:
                    connection = self._create_connection()
                    self.active_connections += 1
                    logger.debug(f"Created new database connection. Active: {self.active_connections}")
                    return connection
                else:
                    # Wait for a connection to become available
                    logger.debug("Waiting for available database connection")
                    connection = self.connections.get(timeout=self.timeout)
                    return connection
    
    def return_connection(self, connection):
        """Return a connection to the pool"""
        try:
            # Reset connection state
            if hasattr(connection, 'rollback'):
                connection.rollback()
            self.connections.put(connection, timeout=1)
            logger.debug("Returned database connection to pool")
        except Exception as e:
            logger.warning(f"Failed to return connection to pool: {e}")
            self._close_connection(connection)
    
    def _create_connection(self):
        """Create a new database connection"""
        database_url = "sqlitecloud://czdyoyrynz.g4.sqlite.cloud:8860/auto-applyer?apikey=3KWvb3v84ZydV0FLHM6PDL2taY9NyOdaZiZ7QnPQKNM"
        
        parsed_url = urlparse(database_url)
        db_type = parsed_url.scheme.lower()
        
        if db_type == "sqlitecloud":
            try:
                import sqlitecloud
                connection = sqlitecloud.connect(database_url)
                return connection
            except ImportError:
                raise Exception("SQLite Cloud support requires sqlitecloud package")
        else:
            raise Exception(f"Unsupported database type: {db_type}")
    
    def _close_connection(self, connection):
        """Close a database connection"""
        try:
            if connection:
                if hasattr(connection, 'closed'):
                    if not connection.closed:
                        connection.close()
                else:
                    connection.close()
                with self.lock:
                    self.active_connections -= 1
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")

# Global connection pool
_connection_pool = None

def get_connection_pool():
    """Get the global connection pool"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = DatabaseConnectionPool()
    return _connection_pool

@contextmanager
def cloud_db_connection() -> Generator:
    """
    Context manager for database connections with pooling.
    Yields the connection object (not the cursor).
    """
    pool = get_connection_pool()
    connection = None
    
    try:
        connection = pool.get_connection()
        logger.debug("Using SQLite Cloud database (pooled)")
        yield connection
        
        # Commit changes if connection is still open
        if connection:
            if hasattr(connection, 'closed'):
                if not connection.closed:
                    connection.commit()
            else:
                connection.commit()
            
    except Exception as e:
        # Rollback on error
        if connection:
            try:
                if hasattr(connection, 'closed'):
                    if not connection.closed:
                        connection.rollback()
                else:
                    connection.rollback()
            except:
                pass
        raise e
        
    finally:
        # Return connection to pool
        if connection:
            pool.return_connection(connection) 