#!/usr/bin/env python3
"""
Debug authentication issues
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    print("🔍 Testing authentication flow...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Try to register a test user
    test_user = {
        "username": "testuser_debug",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        print(f"📝 Register response: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Register failed: {e}")
    
    # Test 3: Try to login
    login_data = {
        "username": "testuser_debug",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"🔑 Login response: {response.status_code}")
        if response.status_code == 200:
            login_response = response.json()
            print(f"   Response: {login_response}")
            token = login_response.get("access_token")
            
            if token:
                print(f"✅ Got token: {token[:20]}...")
                
                # Test 4: Test /api/auth/me with token
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
                print(f"👤 /api/auth/me response: {me_response.status_code}")
                if me_response.status_code == 200:
                    print(f"   User data: {me_response.json()}")
                else:
                    print(f"   Error: {me_response.text}")
                
                # Test 5: Test /api/match with token
                match_response = requests.get(f"{BASE_URL}/api/match", headers=headers)
                print(f"🔍 /api/match response: {match_response.status_code}")
                if match_response.status_code == 200:
                    match_data = match_response.json()
                    print(f"   Found {len(match_data.get('jobs', []))} jobs")
                else:
                    print(f"   Error: {match_response.text}")
                
                # Test 6: Test /api/saved-jobs with token
                saved_response = requests.get(f"{BASE_URL}/api/saved-jobs", headers=headers)
                print(f"💾 /api/saved-jobs response: {saved_response.status_code}")
                if saved_response.status_code == 200:
                    print(f"   Saved jobs: {saved_response.json()}")
                else:
                    print(f"   Error: {saved_response.text}")
            else:
                print("❌ No token in login response")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Login failed: {e}")

if __name__ == "__main__":
    test_auth_flow() 