#!/usr/bin/env python3
"""
Simple test for create_user function
"""

import sys
sys.path.append('backend')
from db import create_user, cloud_db_connection
import hashlib

def test_create_user_simple():
    """Simple test for create_user function"""
    print("🔍 Simple test for create_user function...")
    
    username = "simple_test_user"
    email = "simple_test@example.com"
    password = "simple_test_pass"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        print(f"Creating user: {username}")
        user_id = create_user(username, email, password_hash)
        print(f"create_user returned: {user_id}")
        
        if user_id:
            print("✅ User created successfully")
            
            # Check if user exists
            with cloud_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if user:
                    print(f"✅ User found in database: {user}")
                else:
                    print("❌ User not found in database")
        else:
            print("❌ create_user returned None")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_user_simple() 