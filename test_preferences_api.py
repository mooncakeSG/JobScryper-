#!/usr/bin/env python3

"""
Test script for preferences API
"""

import requests
import json

def test_preferences_api():
    """Test the preferences API endpoints"""
    
    base_url = "http://localhost:8000"
    
    # First, let's try to login to get a token
    print("🔐 Testing login...")
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Login successful, got token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test GET preferences
            print("\n📋 Testing GET /api/preferences...")
            get_response = requests.get(f"{base_url}/api/preferences", headers=headers)
            print(f"GET preferences status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                preferences = get_response.json()
                print(f"✅ GET preferences successful:")
                print(json.dumps(preferences, indent=2))
                
                # Test PATCH preferences
                print("\n💾 Testing PATCH /api/preferences...")
                update_data = {
                    "salaryCurrency": "EUR",
                    "jobTypes": ["Full-time", "Remote"],
                    "locations": ["Berlin", "Amsterdam", "Remote"],
                    "industries": ["Technology", "Finance"],
                    "salaryRange": "60000-120000"
                }
                
                patch_response = requests.patch(f"{base_url}/api/preferences", 
                                              json=update_data, 
                                              headers=headers)
                print(f"PATCH preferences status: {patch_response.status_code}")
                
                if patch_response.status_code == 200:
                    print("✅ PATCH preferences successful")
                    
                    # Test GET preferences again to see the changes
                    print("\n📋 Testing GET /api/preferences again...")
                    get_response2 = requests.get(f"{base_url}/api/preferences", headers=headers)
                    if get_response2.status_code == 200:
                        updated_preferences = get_response2.json()
                        print(f"✅ Updated preferences:")
                        print(json.dumps(updated_preferences, indent=2))
                    else:
                        print(f"❌ Failed to get updated preferences: {get_response2.text}")
                else:
                    print(f"❌ PATCH preferences failed: {patch_response.text}")
            else:
                print(f"❌ GET preferences failed: {get_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing preferences API: {e}")

if __name__ == "__main__":
    test_preferences_api() 