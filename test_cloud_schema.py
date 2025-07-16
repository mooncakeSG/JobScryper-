#!/usr/bin/env python3
"""
Test the actual schema of SQLite Cloud database
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection

def test_cloud_schema():
    """Test the actual schema of SQLite Cloud database"""
    print("🔍 Testing SQLite Cloud database schema...")
    
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("Users table columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            print()
            
            # Get sample data
            cursor.execute("SELECT * FROM users LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                print(f"Sample user data: {sample}")
                print(f"Number of columns: {len(sample)}")
            else:
                print("No users found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cloud_schema() 