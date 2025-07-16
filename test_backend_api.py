#!/usr/bin/env python3
"""
Test script for backend API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_register():
    """Test user registration"""
    print("\n🔍 Testing user registration...")
    try:
        data = {
            "username": "testuser3",
            "password": "testpass123",
            "email": "testuser3@example.com"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        print(f"✅ Registration: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def test_login_existing():
    """Test login with existing user"""
    print("\n🔍 Testing login with existing user...")
    try:
        data = {
            "username": "demo",
            "password": "demo"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"✅ Login: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_login():
    """Test user login"""
    print("\n🔍 Testing user login...")
    try:
        data = {
            "username": "testuser3",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"✅ Login: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test a protected endpoint"""
    if not token:
        print("❌ No token available for protected endpoint test")
        return False
    
    print("\n🔍 Testing protected endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"✅ Protected endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Protected endpoint failed: {e}")
        return False

def test_2fa_setup(token):
    """Test 2FA setup"""
    if not token:
        print("❌ No token available for 2FA test")
        return False
    
    print("\n🔍 Testing 2FA setup...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/api/auth/setup-2fa", headers=headers)
        print(f"✅ 2FA setup: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 2FA setup failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting backend API tests...")
    
    # Test health endpoint
    if not test_health():
        print("❌ Backend is not running or health check failed")
        return
    
    # Test login with existing user first
    token = test_login_existing()
    if token:
        print("✅ Login with existing user successful!")
        test_protected_endpoint(token)
        test_2fa_setup(token)
    else:
        print("❌ Login with existing user failed")
    
    # Test registration
    if not test_register():
        print("❌ Registration failed")
        return
    
    # Test login with new user
    token = test_login()
    if not token:
        print("❌ Login failed")
        return
    
    # Test protected endpoint
    test_protected_endpoint(token)
    
    # Test 2FA setup
    test_2fa_setup(token)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 