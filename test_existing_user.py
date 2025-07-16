#!/usr/bin/env python3
"""
Test authentication with existing users
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_existing_users():
    print("🔍 Testing with existing users...")
    
    # Test 1: Check what users exist
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email FROM users LIMIT 10")
            users = cursor.fetchall()
            print(f"📋 Existing users:")
            for user in users:
                print(f"   ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    except Exception as e:
        print(f"❌ Failed to get users: {e}")
        return
    
    # Test 2: Try to login with the first user
    if users:
        test_user = users[0]
        username = test_user[1]
        print(f"\n🔑 Testing login with user: {username}")
        
        # Try a simple password first
        login_data = {
            "username": username,
            "password": "password"
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
                    me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
                    print(f"👤 /api/auth/me: {me_response.status_code}")
                    if me_response.status_code == 200:
                        print(f"   User data: {me_response.json()}")
                    else:
                        print(f"   Error: {me_response.text}")
                    
                    # Test /api/match
                    match_response = requests.get(f"{BASE_URL}/api/match", headers=headers)
                    print(f"🔍 /api/match: {match_response.status_code}")
                    if match_response.status_code == 200:
                        match_data = match_response.json()
                        print(f"   Found {len(match_data.get('jobs', []))} jobs")
                    else:
                        print(f"   Error: {match_response.text}")
                    
                    # Test /api/saved-jobs
                    saved_response = requests.get(f"{BASE_URL}/api/saved-jobs", headers=headers)
                    print(f"💾 /api/saved-jobs: {saved_response.status_code}")
                    if saved_response.status_code == 200:
                        print(f"   Saved jobs: {saved_response.json()}")
                    else:
                        print(f"   Error: {saved_response.text}")
                else:
                    print("❌ No token in login response")
            else:
                print(f"   Error: {response.text}")
                
                # Try with a different password
                login_data["password"] = "123456"
                response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
                print(f"📝 Login with '123456': {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Login successful with '123456'!")
                    login_response = response.json()
                    token = login_response.get("access_token")
                    
                    if token:
                        print(f"✅ Got token: {token[:20]}...")
                        
                        # Test authenticated endpoints
                        headers = {"Authorization": f"Bearer {token}"}
                        
                        # Test /api/auth/me
                        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
                        print(f"👤 /api/auth/me: {me_response.status_code}")
                        if me_response.status_code == 200:
                            print(f"   User data: {me_response.json()}")
                        else:
                            print(f"   Error: {me_response.text}")
                        
                        # Test /api/match
                        match_response = requests.get(f"{BASE_URL}/api/match", headers=headers)
                        print(f"🔍 /api/match: {match_response.status_code}")
                        if match_response.status_code == 200:
                            match_data = match_response.json()
                            print(f"   Found {len(match_data.get('jobs', []))} jobs")
                        else:
                            print(f"   Error: {match_response.text}")
                        
                        # Test /api/saved-jobs
                        saved_response = requests.get(f"{BASE_URL}/api/saved-jobs", headers=headers)
                        print(f"💾 /api/saved-jobs: {saved_response.status_code}")
                        if saved_response.status_code == 200:
                            print(f"   Saved jobs: {saved_response.json()}")
                        else:
                            print(f"   Error: {saved_response.text}")
                else:
                    print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Login test failed: {e}")
    else:
        print("❌ No users found in database")

if __name__ == "__main__":
    from db import cloud_db_connection
    test_existing_users() 