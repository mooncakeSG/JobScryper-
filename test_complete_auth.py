#!/usr/bin/env python3
"""
Complete authentication flow test
"""

import requests
import json

def test_complete_auth():
    """Test complete authentication flow"""
    print("🔍 Testing complete authentication flow...")
    
    # Test registration
    print("\n1. Testing registration...")
    register_data = {
        "username": "complete_auth_user",
        "password": "complete_auth_pass",
        "email": "complete_auth@example.com"
    }
    
    try:
        register_response = requests.post("http://localhost:8000/api/auth/register", json=register_data)
        print(f"Registration: {register_response.status_code}")
        print(f"Registration body: {register_response.json()}")
        
        if register_response.status_code == 200:
            print("✅ Registration successful!")
            
            # Test login
            print("\n2. Testing login...")
            login_data = {
                "username": "complete_auth_user",
                "password": "complete_auth_pass"
            }
            
            login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
            print(f"Login: {login_response.status_code}")
            print(f"Login body: {login_response.json()}")
            
            if login_response.status_code == 200:
                print("✅ Login successful!")
                
                # Test protected endpoint
                print("\n3. Testing protected endpoint...")
                token = login_response.json().get("access_token")
                if token:
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = requests.get("http://localhost:8000/api/auth/me", headers=headers)
                    print(f"Me endpoint: {me_response.status_code}")
                    print(f"Me endpoint body: {me_response.json()}")
                    
                    if me_response.status_code == 200:
                        print("✅ Protected endpoint successful!")
                    else:
                        print("❌ Protected endpoint failed")
                else:
                    print("❌ No access token received")
            else:
                print("❌ Login failed")
                
                # Try with different password formats
                print("\n4. Testing alternative password formats...")
                
                # Try with bcrypt hash
                import hashlib
                password_hash = hashlib.sha256("complete_auth_pass".encode()).hexdigest()
                print(f"Password hash: {password_hash}")
                
                # Try login with wrong password to see error
                wrong_login_data = {
                    "username": "complete_auth_user",
                    "password": "wrong_password"
                }
                wrong_response = requests.post("http://localhost:8000/api/auth/login", json=wrong_login_data)
                print(f"Wrong password response: {wrong_response.status_code}")
                print(f"Wrong password body: {wrong_response.json()}")
        else:
            print("❌ Registration failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_auth() 