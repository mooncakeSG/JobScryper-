#!/usr/bin/env python3
"""
Direct test to find demo user password using backend connection
"""

import hashlib
import sys
sys.path.append('backend')
from db import fetch_user_by_username_or_email

def test_demo_password_direct():
    """Direct test to find demo user password"""
    print("🔍 Direct testing of demo user password...")
    
    # Test different usernames
    usernames = ["demo", "testuser", "cloud_test_user"]
    
    for username in usernames:
        print(f"\nTesting username: {username}")
        user = fetch_user_by_username_or_email(username)
        if user:
            print(f"✅ User found: {user[1]}")  # username
            stored_hash = user[3]  # password_hash
            print(f"Stored hash: {stored_hash[:50]}...")
            
            # Test common passwords
            test_passwords = ["demo", "demo123", "password", "123456", "admin", "test", "user", "testpass123"]
            
            for password in test_passwords:
                test_hash = hashlib.sha256(password.encode()).hexdigest()
                if test_hash == stored_hash:
                    print(f"✅ Found password for {username}: {password}")
                    return username, password
            
            print(f"❌ Password not found for {username}")
        else:
            print(f"❌ User {username} not found")
    
    return None, None

if __name__ == "__main__":
    username, password = test_demo_password_direct()
    if username and password:
        print(f"\n🎉 Success! Use username: {username}, password: {password}")
    else:
        print("\n❌ No valid credentials found") 