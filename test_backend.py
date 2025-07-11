#!/usr/bin/env python3
"""
Test script for backend database integration
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_signup():
    """Test user signup"""
    try:
        data = {
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com"
        }
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
        print(f"✅ Signup: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"   Error Response: {response.text}")
            try:
                print(f"   JSON Error: {response.json()}")
            except:
                pass
            return False
    except Exception as e:
        print(f"❌ Signup failed: {e}")
        return False

def test_login():
    """Test user login"""
    try:
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"✅ Login: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if response.status_code == 200:
            return result.get("access_token")
        return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_create_application(token):
    """Test creating a job application"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "job_title": "Software Engineer",
            "company": "Test Company",
            "location": "Remote",
            "status": "applied",
            "salary_min": 80000,
            "salary_max": 120000,
            "job_url": "https://example.com/job",
            "notes": "Test application"
        }
        response = requests.post(f"{BASE_URL}/api/applications", json=data, headers=headers)
        print(f"✅ Create application: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Create application failed: {e}")
        return False

def test_get_applications(token):
    """Test getting job applications"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/applications", headers=headers)
        print(f"✅ Get applications: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get applications failed: {e}")
        return False

def test_analytics(token):
    """Test analytics endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/analytics", headers=headers)
        print(f"✅ Analytics: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Analytics failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Backend Database Integration")
    print("=" * 50)
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    # Test health
    if not test_health():
        print("❌ Backend not responding")
        return
    
    print("\n" + "-" * 50)
    
    # Test signup
    if not test_signup():
        print("❌ Signup test failed")
        return
    
    print("\n" + "-" * 50)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login test failed")
        return
    
    print("\n" + "-" * 50)
    
    # Test application creation
    if not test_create_application(token):
        print("❌ Application creation test failed")
        return
    
    print("\n" + "-" * 50)
    
    # Test getting applications
    if not test_get_applications(token):
        print("❌ Get applications test failed")
        return
    
    print("\n" + "-" * 50)
    
    # Test analytics
    if not test_analytics(token):
        print("❌ Analytics test failed")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Backend database integration is working correctly.")

if __name__ == "__main__":
    main() 