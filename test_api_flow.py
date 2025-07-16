#!/usr/bin/env python3
"""
Test the exact API registration flow
"""

import sys
sys.path.append('backend')
from db import fetch_user_by_username_or_email, create_user, cloud_db_connection
import hashlib

def test_api_flow():
    """Test the exact API registration flow"""
    print("🔍 Testing exact API registration flow...")
    
    username = "api_flow_test_user2"
    password = "api_flow_test_pass"
    email = "api_flow_test2@example.com"
    
    try:
        # Step 1: Check if user already exists (like the API does)
        existing_user = fetch_user_by_username_or_email(username)
        if existing_user:
            print(f"User {username} already exists")
            return
        
        # Step 2: Hash password (like the API does)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Step 3: Create user (like the API does)
        user_id = create_user(username, email, password_hash)
        print(f"create_user returned: {user_id}")
        
        if not user_id:
            print("❌ create_user returned None")
            return
        
        # Step 4: Check if user was actually created
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                print(f"✅ User found in database: {user}")
            else:
                print("❌ User not found in database")
            
            # Check total count
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            print(f"Total users: {count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_flow() 