#!/usr/bin/env python3
"""
Test create_user with API parameters
"""

import sys
sys.path.append('backend')
from db import create_user, cloud_db_connection
import hashlib

def test_create_user_api_params():
    """Test create_user with API parameters"""
    print("🔍 Testing create_user with API parameters...")
    
    # Use the same parameters as the API
    username = "api_params_test_user"
    password = "api_params_test_pass"
    email = "api_params_test@example.com"
    
    # Hash password the same way as the API
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        # Check if user exists first
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            existing = cursor.fetchone()
            if existing:
                print(f"User {username} already exists with ID {existing[0]}")
                return
        
        # Try to create user
        user_id = create_user(username, email, password_hash)
        print(f"create_user returned: {user_id}")
        
        if user_id:
            print("✅ User created successfully")
            
            # Check if user exists in database
            with cloud_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, email, password_hash FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if user:
                    user_id, username, email, password_hash = user
                    print(f"Found user in database: ID={user_id}, Username={username}, Email={email}")
                    print(f"Password hash: {password_hash[:50]}..." if password_hash else "Password hash: None")
                else:
                    print("❌ User not found in database after creation")
                    
                # Check total count
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                print(f"Total users: {count}")
        else:
            print("❌ create_user returned None")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_user_api_params() 