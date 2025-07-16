#!/usr/bin/env python3
"""
Test script to check API endpoints
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test login endpoint
    try:
        login_data = {
            "username": "demo",
            "password": "demo123"
        }
        response = requests.post(
            f"{base_url}/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        print(f"✅ Login test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Token: {data.get('access_token', 'No token')[:20]}...")
            token = data.get('access_token')
        else:
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return
    
    # Test authenticated endpoint
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        print(f"✅ Auth test: {response.status_code}")
        if response.status_code == 200:
            print(f"   User: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
    
    # Test recent activity endpoint
    try:
        response = requests.get(f"{base_url}/api/activity/recent?limit=5", headers=headers)
        print(f"✅ Activity test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Activities: {len(data.get('activities', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Activity test failed: {e}")
    
    print("\n🎉 API test completed!")

if __name__ == "__main__":
    test_api() 