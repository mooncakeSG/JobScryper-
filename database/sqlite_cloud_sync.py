"""
Auto Applyer - SQLite Cloud Sync Utility

Handles synchronization between local SQLite database and SQLite Cloud
using their API-based approach.
"""

import os
import json
import requests
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import hashlib

from utils.logging_config import get_logger
from utils.errors import DatabaseError, ConfigurationError

logger = get_logger(__name__)


class SQLiteCloudSync:
    """Handles synchronization with SQLite Cloud using their API."""
    
    def __init__(self, api_key: str, database_name: str, region: str = 'us-east-1'):
        """
        Initialize SQLite Cloud sync.
        
        Args:
            api_key: SQLite Cloud API key
            database_name: Name of the database in SQLite Cloud
            region: SQLite Cloud region
        """
        self.api_key = api_key
        self.database_name = database_name
        self.region = region
        self.base_url = f"https://api.sqlitecloud.io/v1"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make API request to SQLite Cloud."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"SQLite Cloud API request failed: {e}")
            raise DatabaseError(f"SQLite Cloud API error: {e}")
    
    def create_database(self) -> bool:
        """Create a new database in SQLite Cloud."""
        try:
            data = {
                'name': self.database_name,
                'region': self.region
            }
            
            result = self._make_request('POST', 'databases', data)
            logger.info(f"Created database {self.database_name} in SQLite Cloud")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            return False
    
    def list_databases(self) -> List[Dict]:
        """List all databases in SQLite Cloud."""
        try:
            result = self._make_request('GET', 'databases')
            return result.get('databases', [])
        except Exception as e:
            logger.error(f"Failed to list databases: {e}")
            return []
    
    def upload_database(self, local_db_path: str) -> bool:
        """Upload local SQLite database to SQLite Cloud."""
        try:
            if not Path(local_db_path).exists():
                raise FileNotFoundError(f"Local database file not found: {local_db_path}")
            
            # Read the database file
            with open(local_db_path, 'rb') as f:
                db_content = f.read()
            
            # Upload to SQLite Cloud
            files = {'file': (f'{self.database_name}.db', db_content, 'application/octet-stream')}
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            url = f"{self.base_url}/databases/{self.database_name}/upload"
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            
            logger.info(f"Successfully uploaded database to SQLite Cloud")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload database: {e}")
            return False
    
    def download_database(self, local_db_path: str) -> bool:
        """Download database from SQLite Cloud to local file."""
        try:
            url = f"{self.base_url}/databases/{self.database_name}/download"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save to local file
            with open(local_db_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Successfully downloaded database from SQLite Cloud")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download database: {e}")
            return False
    
    def sync_tables(self, local_db_path: str) -> bool:
        """Sync table structure and data between local and cloud databases."""
        try:
            # Get local database schema
            local_schema = self._get_local_schema(local_db_path)
            
            # Get cloud database schema
            cloud_schema = self._get_cloud_schema()
            
            # Compare and sync
            if local_schema != cloud_schema:
                logger.info("Schema differences detected, syncing...")
                return self._sync_schema(local_db_path, local_schema, cloud_schema)
            
            logger.info("Database schemas are in sync")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync tables: {e}")
            return False
    
    def _get_local_schema(self, db_path: str) -> Dict[str, Any]:
        """Get schema from local SQLite database."""
        schema = {}
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                schema[table_name] = {
                    'columns': [col[1] for col in columns],
                    'types': [col[2] for col in columns]
                }
            
            conn.close()
            return schema
            
        except Exception as e:
            logger.error(f"Failed to get local schema: {e}")
            return {}
    
    def _get_cloud_schema(self) -> Dict[str, Any]:
        """Get schema from SQLite Cloud database."""
        try:
            result = self._make_request('GET', f'databases/{self.database_name}/schema')
            return result.get('schema', {})
        except Exception as e:
            logger.error(f"Failed to get cloud schema: {e}")
            return {}
    
    def _sync_schema(self, local_db_path: str, local_schema: Dict, cloud_schema: Dict) -> bool:
        """Sync schema between local and cloud databases."""
        try:
            # For now, we'll upload the local database to ensure consistency
            # In a more sophisticated implementation, you'd compare and merge schemas
            return self.upload_database(local_db_path)
            
        except Exception as e:
            logger.error(f"Failed to sync schema: {e}")
            return False
    
    def backup_database(self, backup_name: str = None) -> bool:
        """Create a backup of the cloud database."""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            data = {
                'name': backup_name,
                'database': self.database_name
            }
            
            result = self._make_request('POST', 'backups', data)
            logger.info(f"Created backup: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all backups for the database."""
        try:
            result = self._make_request('GET', f'databases/{self.database_name}/backups')
            return result.get('backups', [])
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore database from a backup."""
        try:
            data = {
                'backup': backup_name
            }
            
            result = self._make_request('POST', f'databases/{self.database_name}/restore', data)
            logger.info(f"Restored database from backup: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database."""
        try:
            result = self._make_request('GET', f'databases/{self.database_name}')
            return result
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}


class DatabaseSyncManager:
    """Manages database synchronization between local and SQLite Cloud."""
    
    def __init__(self, local_db_path: str, api_key: str, database_name: str, region: str = 'us-east-1'):
        """
        Initialize database sync manager.
        
        Args:
            local_db_path: Path to local SQLite database
            api_key: SQLite Cloud API key
            database_name: Name of the database in SQLite Cloud
            region: SQLite Cloud region
        """
        self.local_db_path = local_db_path
        self.cloud_sync = SQLiteCloudSync(api_key, database_name, region)
        self.last_sync = None
    
    def initialize_cloud_database(self) -> bool:
        """Initialize the cloud database if it doesn't exist."""
        try:
            # Check if database exists
            databases = self.cloud_sync.list_databases()
            db_exists = any(db['name'] == self.cloud_sync.database_name for db in databases)
            
            if not db_exists:
                logger.info("Creating new database in SQLite Cloud...")
                return self.cloud_sync.create_database()
            else:
                logger.info("Database already exists in SQLite Cloud")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize cloud database: {e}")
            return False
    
    def sync_to_cloud(self) -> bool:
        """Sync local database to SQLite Cloud."""
        try:
            if not Path(self.local_db_path).exists():
                logger.warning("Local database file not found, skipping sync")
                return False
            
            logger.info("Syncing local database to SQLite Cloud...")
            success = self.cloud_sync.upload_database(self.local_db_path)
            
            if success:
                self.last_sync = datetime.now()
                logger.info("Database sync completed successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to sync to cloud: {e}")
            return False
    
    def sync_from_cloud(self) -> bool:
        """Sync database from SQLite Cloud to local."""
        try:
            logger.info("Syncing database from SQLite Cloud...")
            success = self.cloud_sync.download_database(self.local_db_path)
            
            if success:
                self.last_sync = datetime.now()
                logger.info("Database sync from cloud completed successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to sync from cloud: {e}")
            return False
    
    def auto_sync(self, force: bool = False) -> bool:
        """Automatically sync based on last sync time."""
        try:
            # Sync every hour by default
            sync_interval = timedelta(hours=1)
            
            if force or self.last_sync is None or (datetime.now() - self.last_sync) > sync_interval:
                return self.sync_to_cloud()
            else:
                logger.debug("Skipping sync - too soon since last sync")
                return True
                
        except Exception as e:
            logger.error(f"Auto sync failed: {e}")
            return False
    
    def create_backup(self, backup_name: str = None) -> bool:
        """Create a backup of the cloud database."""
        return self.cloud_sync.backup_database(backup_name)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status."""
        return {
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'local_db_exists': Path(self.local_db_path).exists(),
            'cloud_db_info': self.cloud_sync.get_database_info(),
            'backups': self.cloud_sync.list_backups()
        }


# Utility functions for easy integration
def get_sync_manager(api_key: str, database_name: str = 'auto_applyer', region: str = 'us-east-1') -> DatabaseSyncManager:
    """Get a database sync manager instance."""
    local_db_path = Path('data/auto_applyer_production.db')
    return DatabaseSyncManager(str(local_db_path), api_key, database_name, region)


def sync_database_to_cloud(api_key: str, database_name: str = 'auto_applyer') -> bool:
    """Quick function to sync database to SQLite Cloud."""
    sync_manager = get_sync_manager(api_key, database_name)
    return sync_manager.sync_to_cloud()


def sync_database_from_cloud(api_key: str, database_name: str = 'auto_applyer') -> bool:
    """Quick function to sync database from SQLite Cloud."""
    sync_manager = get_sync_manager(api_key, database_name)
    return sync_manager.sync_from_cloud() 