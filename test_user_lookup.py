#!/usr/bin/env python3
"""
Test user lookup functionality
"""

import sys
sys.path.append('backend')
from db import fetch_user_by_username_or_email

def test_user_lookup():
    """Test user lookup functionality"""
    print("🔍 Testing user lookup...")
    
    username = "error_test_user"
    
    try:
        # Test user lookup
        user = fetch_user_by_username_or_email(username)
        if user:
            print(f"✅ User found: {user[1]}")  # username
            print(f"User data length: {len(user)}")
            print(f"User data: {user}")
            
            # Check if we have enough fields for login
            if len(user) >= 20:
                print("✅ User data has enough fields for login")
            else:
                print(f"❌ User data has only {len(user)} fields, need at least 20")
        else:
            print("❌ User not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_lookup() 