#!/usr/bin/env python3
"""
Detailed test of SQLite Cloud database schema
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection

def test_cloud_schema_detailed():
    """Detailed test of SQLite Cloud database schema"""
    print("🔍 Detailed testing of SQLite Cloud database schema...")
    
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("Users table columns:")
            for i, col in enumerate(columns):
                print(f"  {i}: {col[1]} ({col[2]}) - nullable: {col[3]}, default: {col[4]}, pk: {col[5]}")
            print()
            
            # Get sample data with column names
            cursor.execute("SELECT * FROM users LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                print(f"Sample user data:")
                for i, value in enumerate(sample):
                    col_name = columns[i][1] if i < len(columns) else f"col_{i}"
                    print(f"  {col_name}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
                print(f"Number of columns: {len(sample)}")
            else:
                print("No users found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cloud_schema_detailed() 