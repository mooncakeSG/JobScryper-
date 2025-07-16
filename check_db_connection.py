#!/usr/bin/env python3
"""
Check database connection details
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection
import os

def check_db_connection():
    """Check database connection details"""
    print("🔍 Checking database connection...")
    
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check database file path
            cursor.execute("PRAGMA database_list")
            databases = cursor.fetchall()
            print("Database files:")
            for db in databases:
                print(f"  {db[1]}: {db[2]}")
            
            # Check current database
            cursor.execute("PRAGMA database_list")
            current_db = cursor.fetchone()
            print(f"Current database: {current_db[2] if current_db else 'Unknown'}")
            
            # Check if we can write to the database
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            print(f"Current user count: {count}")
            
            # Try to insert a test record
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", 
                         ("test_connection", "test@connection.com", "test_hash"))
            conn.commit()
            print("✅ Successfully inserted test record")
            
            # Check if the record was inserted
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("test_connection",))
            test_count = cursor.fetchone()[0]
            print(f"Test record count: {test_count}")
            
            # Clean up test record
            cursor.execute("DELETE FROM users WHERE username = ?", ("test_connection",))
            conn.commit()
            print("✅ Successfully deleted test record")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_db_connection() 