#!/usr/bin/env python3
"""
Test to find the correct password for demo user
"""

import hashlib
import sys
sys.path.append('backend')
from db import fetch_user_by_username_or_email

def test_demo_password():
    """Test to find the correct password for demo user"""
    print("🔍 Testing demo user password...")
    
    # Get demo user
    demo_user = fetch_user_by_username_or_email("demo")
    if not demo_user:
        print("❌ Demo user not found")
        return
    
    stored_hash = demo_user[3]  # password_hash
    print(f"Stored hash: {stored_hash}")
    
    # Test common passwords
    test_passwords = ["demo", "demo123", "password", "123456", "admin", "test", "user"]
    
    for password in test_passwords:
        test_hash = hashlib.sha256(password.encode()).hexdigest()
        if test_hash == stored_hash:
            print(f"✅ Found password: {password}")
            return password
    
    print("❌ Password not found in common passwords")
    return None

if __name__ == "__main__":
    test_demo_password() 