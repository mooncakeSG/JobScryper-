#!/usr/bin/env python3
"""
Check if the new user was created in the backend database
"""

import sqlite3
import hashlib

def check_new_user():
    """Check if the new user was created in the backend database"""
    print("🔍 Checking new user in backend database...")
    
    try:
        # Connect to backend database
        conn = sqlite3.connect("backend/auto_applyer.db")
        cursor = conn.cursor()
        
        # Get the user we just created
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", ("error_test_user",))
        user = cursor.fetchone()
        
        if user:
            user_id, username, email, password_hash = user
            print(f"User: ID={user_id}, Username={username}, Email={email}")
            print(f"Stored password hash: {password_hash}")
            
            # Test password verification
            test_password = "error_test_pass"
            test_hash = hashlib.sha256(test_password.encode()).hexdigest()
            print(f"Test password hash: {test_hash}")
            
            if password_hash == test_hash:
                print("✅ Password hashes match!")
            else:
                print("❌ Password hashes don't match!")
                print(f"Length comparison: stored={len(password_hash)}, test={len(test_hash)}")
        else:
            print("❌ User not found in backend database")
            
            # List all users to see what's there
            cursor.execute("SELECT id, username, email FROM users ORDER BY id")
            users = cursor.fetchall()
            print(f"All users in backend database: {users}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_new_user() 