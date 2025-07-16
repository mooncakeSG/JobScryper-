#!/usr/bin/env python3
"""
Debug script for login issues
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db import fetch_user_by_username_or_email, cloud_db_connection
import hashlib

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def debug_login():
    print("🔍 Debugging login issues...")
    
    # Test 1: Check if demo user exists
    print("\n1️⃣  Checking demo user...")
    try:
        user = fetch_user_by_username_or_email("demo")
        if user:
            print(f"✅ Demo user found: ID={user[0]}, Username={user[1]}")
            print(f"   Password hash: {user[2][:20]}...")
        else:
            print("❌ Demo user not found")
            return
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return
    
    # Test 2: Check password hashing
    print("\n2️⃣  Testing password hashing...")
    test_password = "demo123"
    hashed = hash_password(test_password)
    print(f"✅ Password hash for 'demo123': {hashed[:20]}...")
    
    # Test 3: Verify password
    print("\n3️⃣  Verifying password...")
    if hashed == user[2]:
        print("✅ Password matches!")
    else:
        print("❌ Password does not match!")
        print(f"   Expected: {user[2]}")
        print(f"   Got:      {hashed}")
    
    # Test 4: Check database connection
    print("\n4️⃣  Testing database connection...")
    try:
        with cloud_db_connection() as conn:
            # Check users table
            result = conn.execute("SELECT COUNT(*) FROM users").fetchone()
            print(f"✅ Users table: {result[0]} users")
            
            # Check demo user specifically
            demo = conn.execute("SELECT id, username, email FROM users WHERE username = 'demo'").fetchone()
            if demo:
                print(f"✅ Demo user in DB: ID={demo[0]}, Username={demo[1]}, Email={demo[2]}")
            else:
                print("❌ Demo user not found in DB")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print("\n🎉 Debug completed!")

if __name__ == "__main__":
    debug_login() 