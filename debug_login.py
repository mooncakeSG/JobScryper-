#!/usr/bin/env python3
"""
Debug login process step by step
"""

import sys
sys.path.append('backend')
from db import fetch_user_by_username_or_email
import hashlib

def debug_login():
    """Debug login process step by step"""
    print("🔍 Debugging login process...")
    
    # Test 1: Fetch user
    print("\n1. Fetching user 'demo'...")
    user = fetch_user_by_username_or_email("demo")
    if user:
        print(f"✅ User found: {user}")
        user_id, db_username, db_password_hash, email, is_active, is_verified, created_at, resume_text = user
        print(f"User ID: {user_id}")
        print(f"Username: {db_username}")
        print(f"Email: {email}")
        print(f"Password hash: {db_password_hash[:50]}...")
        print(f"Is active: {is_active}")
        print(f"Is verified: {is_verified}")
    else:
        print("❌ User not found")
        return
    
    # Test 2: Test password
    print("\n2. Testing password 'demo123'...")
    test_password = "demo123"
    test_hash = hashlib.sha256(test_password.encode()).hexdigest()
    print(f"Test hash: {test_hash}")
    print(f"Stored hash: {db_password_hash}")
    print(f"Hashes match: {test_hash == db_password_hash}")
    
    # Test 3: Test with different password
    print("\n3. Testing password 'demo'...")
    test_password2 = "demo"
    test_hash2 = hashlib.sha256(test_password2.encode()).hexdigest()
    print(f"Test hash: {test_hash2}")
    print(f"Hashes match: {test_hash2 == db_password_hash}")
    
    # Test 4: Test with different password
    print("\n4. Testing password 'password'...")
    test_password3 = "password"
    test_hash3 = hashlib.sha256(test_password3.encode()).hexdigest()
    print(f"Test hash: {test_hash3}")
    print(f"Hashes match: {test_hash3 == db_password_hash}")

if __name__ == "__main__":
    debug_login() 