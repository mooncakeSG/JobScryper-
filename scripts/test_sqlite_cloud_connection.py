#!/usr/bin/env python3
"""
Test SQLite Cloud Connection

Simple script to test the SQLite Cloud connection using your actual credentials.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_sqlite_cloud_connection():
    """Test SQLite Cloud connection with your credentials."""
    
    # Your actual SQLite Cloud credentials
    host = "czdyoyrynz.g4.sqlite.cloud"
    port = "8860"
    database = "auto-applyer"
    api_key = "3KWvb3v84ZydV0FLHM6PDL2taY9NyOdaZiZ7QnPQKNM"
    
    print("🔍 Testing SQLite Cloud Connection")
    print("="*40)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"API Key: {api_key[:10]}...")
    print()
    
    # Set environment variables
    os.environ['SQLITE_CLOUD_HOST'] = host
    os.environ['SQLITE_CLOUD_PORT'] = port
    os.environ['SQLITE_CLOUD_DATABASE'] = database
    os.environ['SQLITE_CLOUD_API_KEY'] = api_key
    os.environ['ENVIRONMENT'] = 'production'
    
    try:
        # Test configuration
        from database.connection import DatabaseConfig
        config = DatabaseConfig('production')
        
        print("✅ Configuration loaded successfully")
        print(f"Connection URL: {config.config['database_url'].replace(api_key, '***')}")
        
        # Test database connection
        from database.connection import DatabaseManager
        db_manager = DatabaseManager(config)
        db_manager.initialize()
        
        print("✅ Database connection successful")
        
        # Test a simple query
        with db_manager.session_scope() as session:
            result = session.execute("SELECT 1 as test")
            test_value = result.scalar()
            if test_value == 1:
                print("✅ Query test successful")
            else:
                print("❌ Query test failed")
                return False
        
        # Get database info
        info = db_manager.get_database_info()
        print(f"✅ Database info retrieved:")
        print(f"   Status: {info['status']}")
        print(f"   Type: {info['database_type']}")
        print(f"   Tables: {info['table_count']}")
        
        db_manager.close()
        print("\n🎉 All tests passed! SQLite Cloud connection is working.")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sqlite_cloud_connection()
    sys.exit(0 if success else 1) 