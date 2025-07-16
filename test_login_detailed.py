#!/usr/bin/env python3
"""
Detailed login test to see exact error
"""

import requests
import json

def test_login_detailed():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing login endpoint in detail...")
    
    # Test login with detailed error handling
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        print(f"📤 Sending login request to {base_url}/api/auth/login")
        print(f"📋 Data: {json.dumps(login_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/api/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"📋 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Login failed!")
            print(f"📋 Response text: {response.text}")
            
            # Try to parse as JSON for better error details
            try:
                error_data = response.json()
                print(f"📋 Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Raw response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server might not be running")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_detailed() 