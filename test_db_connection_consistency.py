#!/usr/bin/env python3
"""
Test database connection consistency
"""

import sys
sys.path.append('backend')
from db import fetch_user_by_username_or_email, cloud_db_connection
import sqlite3

def test_db_connection_consistency():
    """Test database connection consistency"""
    print("🔍 Testing database connection consistency...")
    
    username = "error_test_user"
    
    try:
        # Test user lookup with the function
        print("1. Testing fetch_user_by_username_or_email...")
        user = fetch_user_by_username_or_email(username)
        if user:
            print(f"✅ User found via function: {user[1]}")
        else:
            print("❌ User not found via function")
        
        # Test direct database connection
        print("\n2. Testing direct database connection...")
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check which database we're using
            cursor.execute("PRAGMA database_list")
            databases = cursor.fetchall()
            print(f"Database files: {databases}")
            
            # Check for user directly
            cursor.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
            user_direct = cursor.fetchone()
            if user_direct:
                print(f"✅ User found via direct query: {user_direct}")
            else:
                print("❌ User not found via direct query")
                
                # List all users
                cursor.execute("SELECT id, username, email FROM users ORDER BY id")
                users = cursor.fetchall()
                print(f"All users in database: {users}")
        
        # Test direct SQLite connection to backend database
        print("\n3. Testing direct SQLite connection to backend database...")
        conn = sqlite3.connect("backend/auto_applyer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
        user_backend = cursor.fetchone()
        if user_backend:
            print(f"✅ User found in backend database: {user_backend}")
        else:
            print("❌ User not found in backend database")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_connection_consistency() 