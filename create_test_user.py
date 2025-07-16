#!/usr/bin/env python3
"""
Create a test user and test authentication flow
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import cloud_db_connection, create_user
import hashlib
import requests
import json

BASE_URL = "http://localhost:8000"

def create_and_test_user():
    print("🔧 Creating test user and testing authentication...")
    
    # Create a test user with known credentials
    username = "testuser_auth"
    email = "testauth@example.com"
    password = "testpass123"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Check if user already exists
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            existing = cursor.fetchone()
            if existing:
                print(f"⚠️  User '{username}' already exists, deleting...")
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                print(f"✅ Deleted existing user")
    except Exception as e:
        print(f"❌ Failed to check/delete existing user: {e}")
        return
    
    # Create new user
    try:
        user_id = create_user(username, email, hashed_password)
        if user_id:
            print(f"✅ Created test user with ID: {user_id}")
        else:
            print(f"❌ Failed to create user")
            return
    except Exception as e:
        print(f"❌ Failed to create user: {e}")
        return
    
    # Test login
    print(f"\n🔑 Testing login with credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"📝 Login response: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            print(f"✅ Login successful!")
            print(f"   Response: {login_response}")
            token = login_response.get("access_token")
            
            if token:
                print(f"✅ Got token: {token[:20]}...")
                
                # Test authenticated endpoints
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test /api/auth/me
                print(f"\n👤 Testing /api/auth/me...")
                me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
                print(f"   Status: {me_response.status_code}")
                if me_response.status_code == 200:
                    print(f"   ✅ User data: {me_response.json()}")
                else:
                    print(f"   ❌ Error: {me_response.text}")
                
                # Test /api/match
                print(f"\n🔍 Testing /api/match...")
                match_response = requests.get(f"{BASE_URL}/api/match", headers=headers)
                print(f"   Status: {match_response.status_code}")
                if match_response.status_code == 200:
                    match_data = match_response.json()
                    print(f"   ✅ Found {len(match_data.get('jobs', []))} jobs")
                else:
                    print(f"   ❌ Error: {match_response.text}")
                
                # Test /api/saved-jobs
                print(f"\n💾 Testing /api/saved-jobs...")
                saved_response = requests.get(f"{BASE_URL}/api/saved-jobs", headers=headers)
                print(f"   Status: {saved_response.status_code}")
                if saved_response.status_code == 200:
                    print(f"   ✅ Saved jobs: {saved_response.json()}")
                else:
                    print(f"   ❌ Error: {saved_response.text}")
                
                print(f"\n🎉 Authentication flow test completed successfully!")
                print(f"   You can now use these credentials in the frontend:")
                print(f"   Username: {username}")
                print(f"   Password: {password}")
                
            else:
                print("❌ No token in login response")
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_and_test_user() 