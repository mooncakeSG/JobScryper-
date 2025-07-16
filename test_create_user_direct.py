#!/usr/bin/env python3
"""
Test the create_user function directly
"""

import sys
sys.path.append('backend')
from db import create_user, cloud_db_connection
import hashlib

def test_create_user_direct():
    """Test the create_user function directly"""
    print("🔍 Testing create_user function directly...")
    
    # Hash a password
    password = "direct_test_pass"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        # Try to create a user directly
        user_id = create_user("direct_test_user", "direct_test@example.com", password_hash)
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
        else:
            print("❌ create_user returned None")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_user_direct() 