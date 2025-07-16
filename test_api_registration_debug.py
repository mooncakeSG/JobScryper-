#!/usr/bin/env python3
"""
Debug API registration flow step by step
"""

import sys
sys.path.append('backend')
from db import fetch_user_by_username_or_email, create_user
import hashlib

def test_api_registration_debug():
    """Debug API registration flow step by step"""
    print("🔍 Debugging API registration flow...")
    
    username = "debug_api_user"
    password = "debug_api_pass"
    email = "debug_api@example.com"
    
    try:
        # Step 1: Check if user already exists
        print("Step 1: Checking if user exists...")
        existing_user = fetch_user_by_username_or_email(username)
        if existing_user:
            print(f"❌ User {username} already exists")
            return
        print("✅ User does not exist")
        
        # Step 2: Hash password
        print("Step 2: Hashing password...")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"✅ Password hashed: {password_hash[:20]}...")
        
        # Step 3: Create user
        print("Step 3: Creating user...")
        user_id = create_user(username, email, password_hash)
        print(f"create_user returned: {user_id}")
        
        if user_id:
            print("✅ User created successfully")
            
            # Step 4: Verify user was created
            print("Step 4: Verifying user creation...")
            created_user = fetch_user_by_username_or_email(username)
            if created_user:
                print(f"✅ User verified: {created_user[1]}")  # username
            else:
                print("❌ User not found after creation")
        else:
            print("❌ create_user returned None")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_registration_debug() 