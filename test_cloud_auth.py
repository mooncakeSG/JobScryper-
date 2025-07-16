#!/usr/bin/env python3
"""
Test authentication with SQLite Cloud database
"""

import sys
sys.path.append('backend')
from db import fetch_user_by_username_or_email, create_user, cloud_db_connection
import hashlib

def test_cloud_auth():
    """Test authentication with SQLite Cloud database"""
    print("🔍 Testing authentication with SQLite Cloud database...")
    
    # Test user lookup for existing users
    print("\n1. Testing user lookup for existing users...")
    
    # Test demo user
    demo_user = fetch_user_by_username_or_email("demo")
    if demo_user:
        print(f"✅ Demo user found: {demo_user[1]}")  # username
        print(f"Demo user data length: {len(demo_user)}")
    else:
        print("❌ Demo user not found")
    
    # Test testuser
    testuser = fetch_user_by_username_or_email("testuser")
    if testuser:
        print(f"✅ Testuser found: {testuser[1]}")  # username
        print(f"Testuser data length: {len(testuser)}")
    else:
        print("❌ Testuser not found")
    
    # Test password verification for demo user
    print("\n2. Testing password verification...")
    if demo_user:
        stored_hash = demo_user[3]  # password_hash
        test_password = "demo"  # Assuming demo user has password "demo"
        test_hash = hashlib.sha256(test_password.encode()).hexdigest()
        
        print(f"Stored hash: {stored_hash[:50]}...")
        print(f"Test hash: {test_hash}")
        print(f"Hashes match: {stored_hash == test_hash}")
    
    # Test creating a new user
    print("\n3. Testing user creation...")
    new_username = "cloud_test_user"
    new_email = "cloud_test@example.com"
    new_password = "cloud_test_pass"
    new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    # Check if user exists
    existing_user = fetch_user_by_username_or_email(new_username)
    if existing_user:
        print(f"User {new_username} already exists")
    else:
        # Create user
        user_id = create_user(new_username, new_email, new_password_hash)
        if user_id:
            print(f"✅ User created successfully with ID: {user_id}")
            
            # Verify user was created
            created_user = fetch_user_by_username_or_email(new_username)
            if created_user:
                print(f"✅ User verified: {created_user[1]}")
            else:
                print("❌ User not found after creation")
        else:
            print("❌ User creation failed")

if __name__ == "__main__":
    test_cloud_auth() 