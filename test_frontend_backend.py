#!/usr/bin/env python3
"""
Test script for frontend-backend integration
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        print(f"✅ Backend Health: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_frontend_health():
    """Test frontend health"""
    try:
        response = requests.get(FRONTEND_URL)
        print(f"✅ Frontend Health: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Frontend health check failed: {e}")
        return False

def test_auth_flow():
    """Test complete authentication flow"""
    try:
        # Test signup
        signup_data = {
            "username": "frontendtest",
            "password": "testpass123",
            "email": "frontend@test.com"
        }
        response = requests.post(f"{BACKEND_URL}/api/auth/signup", json=signup_data)
        print(f"✅ Signup: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
        
        # Test login
        login_data = {
            "username": "frontendtest",
            "password": "testpass123"
        }
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Token: {data.get('access_token', 'No token')[:20]}...")
            return data.get('access_token')
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Auth flow failed: {e}")
        return None

def test_protected_endpoints(token):
    """Test protected endpoints with authentication"""
    if not token:
        print("❌ No token available for protected endpoint tests")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test get applications
        response = requests.get(f"{BACKEND_URL}/api/applications", headers=headers)
        print(f"✅ Get Applications: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Applications: {len(data.get('applications', []))}")
        
        # Test analytics
        response = requests.get(f"{BACKEND_URL}/api/analytics", headers=headers)
        print(f"✅ Analytics: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total Applications: {data.get('total_applications', 0)}")
        
        # Test create application
        app_data = {
            "job_title": "Frontend Test Job",
            "company": "Test Company",
            "location": "Remote",
            "status": "applied",
            "salary_min": 75000,
            "salary_max": 95000,
            "job_url": "https://example.com/test-job",
            "notes": "Created via frontend test"
        }
        response = requests.post(f"{BACKEND_URL}/api/applications", json=app_data, headers=headers)
        print(f"✅ Create Application: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Protected endpoints test failed: {e}")

def test_job_search():
    """Test job search endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/match", params={
            "query": "software engineer",
            "location": "remote",
            "max_results": 5
        })
        print(f"✅ Job Search: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json()
            print(f"   Jobs found: {len(jobs)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Job search failed: {e}")

def main():
    """Run all frontend-backend integration tests"""
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # Test health endpoints
    if not test_backend_health():
        print("❌ Backend not available")
        return
    
    if not test_frontend_health():
        print("❌ Frontend not available")
        return
    
    print("\n" + "-" * 50)
    
    # Test authentication flow
    token = test_auth_flow()
    
    print("\n" + "-" * 50)
    
    # Test protected endpoints
    test_protected_endpoints(token)
    
    print("\n" + "-" * 50)
    
    # Test job search
    test_job_search()
    
    print("\n" + "=" * 50)
    print("🎉 Frontend-backend integration test completed!")

if __name__ == "__main__":
    main() 