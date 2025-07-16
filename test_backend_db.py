#!/usr/bin/env python3
"""
Test to check which database the backend is connecting to
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection
import os

def test_backend_db():
    """Test to check which database the backend is connecting to"""
    print("🔍 Testing backend database connection...")
    
    # Check environment variable
    database_url = os.environ.get("DATABASE_URL")
    print(f"DATABASE_URL: {database_url}")
    
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get database info
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()
            print(f"SQLite version: {version}")
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables: {[table[0] for table in tables]}")
            
            # Check users table
            if tables and any('users' in table[0] for table in tables):
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()
                print(f"User count: {count[0]}")
                
                # Get sample users
                cursor.execute("SELECT id, username, email FROM users LIMIT 3")
                users = cursor.fetchall()
                print("Sample users:")
                for user in users:
                    print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
            else:
                print("No users table found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backend_db() 