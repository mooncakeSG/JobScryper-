#!/usr/bin/env python3
"""
Test login with the correct database
"""

import requests

def test_login_final():
    """Test login with the correct database"""
    print("🔍 Testing login with correct database...")
    
    # Test login with the user we just created
    login_data = {
        "username": "db_check_user",
        "password": "db_check_pass"
    }
    
    try:
        login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        print(f"Login response: {login_response.status_code}")
        print(f"Login body: {login_response.json()}")
        
        if login_response.status_code == 200:
            print("✅ Login successful!")
            
            # Test a protected endpoint
            token = login_response.json().get("access_token")
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get("http://localhost:8000/api/auth/me", headers=headers)
                print(f"Me endpoint response: {me_response.status_code}")
                print(f"Me endpoint body: {me_response.json()}")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_final() 