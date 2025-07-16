#!/usr/bin/env python3
"""
Final test of SQLite Cloud database schema
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection

def test_cloud_schema_final():
    """Final test of SQLite Cloud database schema"""
    print("🔍 Final testing of SQLite Cloud database schema...")
    
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("All tables:")
            for table in tables:
                print(f"  {table[0]}")
            print()
            
            # Get detailed table info for users
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("Users table columns (PRAGMA):")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            print()
            
            # Try to get column names from a query
            cursor.execute("SELECT * FROM users LIMIT 0")
            column_names = [description[0] for description in cursor.description]
            print("Users table columns (from query):")
            for i, name in enumerate(column_names):
                print(f"  {i}: {name}")
            print()
            
            # Get sample data
            cursor.execute("SELECT * FROM users LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                print(f"Sample user data:")
                for i, value in enumerate(sample):
                    col_name = column_names[i] if i < len(column_names) else f"col_{i}"
                    print(f"  {col_name}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                print(f"Number of columns: {len(sample)}")
            else:
                print("No users found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cloud_schema_final() 