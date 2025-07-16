#!/usr/bin/env python3
"""
Test to capture detailed error information from API
"""

import requests
import json

def test_api_error_details():
    """Test to capture detailed error information from API"""
    print("🔍 Testing API error details...")
    
    # Test registration via API
    data = {
        "username": "error_test_user",
        "password": "error_test_pass",
        "email": "error_test@example.com"
    }
    
    try:
        print("Making API request...")
        response = requests.post("http://localhost:8000/api/auth/register", json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except Exception as e:
            print(f"Response text: {response.text}")
            print(f"JSON parse error: {e}")
        
        # Also test with a simple request to see if the API is working
        print("\nTesting health endpoint...")
        health_response = requests.get("http://localhost:8000/health")
        print(f"Health status: {health_response.status_code}")
        print(f"Health response: {health_response.json()}")
        
    except Exception as e:
        print(f"❌ Request error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_error_details() 