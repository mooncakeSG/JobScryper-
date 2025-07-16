import requests
import json

# Test the full API workflow
BASE_URL = "http://localhost:8000"

def test_full_workflow():
    print("🧪 Testing Full API Workflow")
    
    # Step 1: Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "username": "testuser_api",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"Register status: {response.status_code}")
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_data = {
        "username": "testuser_api",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"✅ Login successful, got token")
        
        # Step 3: Test job search
        print("\n3. Testing job search...")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/match?query=Software Engineer&location=Remote",
            headers=headers
        )
        print(f"Job search status: {response.status_code}")
        
        if response.status_code == 200:
            jobs_data = response.json()
            jobs = jobs_data.get("jobs", [])
            print(f"✅ Found {len(jobs)} jobs")
            
            for i, job in enumerate(jobs[:3]):
                print(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                print(f"     Match Score: {job.get('matchScore', 'N/A')}")
                print(f"     Explanation: {job.get('matchExplanation', 'N/A')[:100]}...")
        else:
            print(f"❌ Job search failed: {response.text}")
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_full_workflow() 