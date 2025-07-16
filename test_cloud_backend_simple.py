#!/usr/bin/env python3
"""
Simple test of backend with existing users in SQLite Cloud
"""

import requests
import json

def test_cloud_backend_simple():
    """Simple test of backend with existing users in SQLite Cloud"""
    print("🔍 Simple testing of backend with SQLite Cloud database...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Try to login with existing demo user
    print("\n1. Testing login with existing demo user...")
    login_data = {
        "username": "demo",
        "password": "demo123"  # Try different passwords
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
    
    # Test 2: Try to login with testuser
    print("\n2. Testing login with testuser...")
    login_data = {
        "username": "testuser",
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
    
    # Test applications endpoint
    try:
        response = requests.get(f"{base_url}/api/applications", headers=headers)
        print(f"Applications response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Applications access successful")
            print(f"Applications: {response.json()}")
        else:
            print(f"❌ Applications access failed: {response.text}")
    except Exception as e:
        print(f"❌ Applications access error: {e}")

if __name__ == "__main__":
    token = test_cloud_backend_simple()
    test_protected_endpoints(token) 