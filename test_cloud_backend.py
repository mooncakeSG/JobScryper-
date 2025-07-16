#!/usr/bin/env python3
"""
Test backend endpoints with SQLite Cloud database
"""

import requests
import json
import hashlib

def test_cloud_backend():
    """Test backend endpoints with SQLite Cloud database"""
    print("🔍 Testing backend endpoints with SQLite Cloud database...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    register_data = {
        "username": "cloud_backend_test",
        "email": "cloud_backend_test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"Register response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Registration successful")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test 2: Login with the new user
    print("\n2. Testing user login...")
    login_data = {
        "username": "cloud_backend_test",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Login successful")
            result = response.json()
            print(f"Access token: {result.get('access_token', 'None')[:50]}...")
            return result.get('access_token')
        else:
            print(f"❌ Login failed: {response.text}")
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    return None

def test_protected_endpoints(token):
    """Test protected endpoints with authentication token"""
    if not token:
        print("❌ No token available for protected endpoint tests")
        return
    
    print("\n3. Testing protected endpoints...")
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test user profile
    try:
        response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        print(f"Profile response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Profile access successful")
            print(f"User data: {response.json()}")
        else:
            print(f"❌ Profile access failed: {response.text}")
    except Exception as e:
        print(f"❌ Profile access error: {e}")

if __name__ == "__main__":
    token = test_cloud_backend()
    test_protected_endpoints(token) 