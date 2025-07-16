import requests
import json

# Test the resume analysis endpoint
BASE_URL = "http://localhost:8000"

def test_resume_endpoint():
    print("🧪 Testing Resume Analysis Endpoint")
    
    # Step 1: Login to get a token
    print("\n1. Logging in...")
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token_data = response.json()
    token = token_data.get("access_token")
    print(f"✅ Login successful, token received")
    
    # Step 2: Test the resume/analyze endpoint exists
    print("\n2. Testing endpoint availability...")
    response = requests.options(f"{BASE_URL}/api/resume/analyze")
    print(f"OPTIONS status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Resume analysis endpoint is available")
    else:
        print("❌ Resume analysis endpoint not found")
    
    # Step 3: Test with a simple file (this will fail but should give proper error)
    print("\n3. Testing with dummy file...")
    files = {'file': ('test.pdf', b'dummy content', 'application/pdf')}
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(f"{BASE_URL}/api/resume/analyze", files=files, headers=headers)
    print(f"POST status: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ Endpoint is working (expected error for dummy file)")
    elif response.status_code == 200:
        print("✅ Endpoint is working (unexpected success)")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_resume_endpoint() 