import requests
import json

# Test the backend API directly
BASE_URL = "http://localhost:8000"

def test_backend_jobspy():
    print("🧪 Testing Backend JobSpy Integration")
    print("=" * 50)
    
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
    
    # Step 2: Test job search with JobSpy
    print("\n2. Testing job search with JobSpy...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test the same query that worked in direct JobSpy test
    params = {
        'query': 'Full Stack Developer',
        'location': 'Cape Town',
        'job_type': 'all'
    }
    
    response = requests.get(f"{BASE_URL}/api/match", params=params, headers=headers)
    print(f"Job search status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        jobs = data.get('jobs', [])
        print(f"✅ Backend returned {len(jobs)} jobs")
        
        # Check job sources
        sources = {}
        for job in jobs:
            source = job.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"Job sources: {sources}")
        
        # Show first few jobs
        for i, job in enumerate(jobs[:3]):
            print(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            print(f"     Source: {job.get('source', 'N/A')}")
            print(f"     Location: {job.get('location', 'N/A')}")
            print()
    else:
        print(f"❌ Job search failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Step 3: Test with a different query that we know works
    print("\n3. Testing with 'Software Engineer' in 'Remote'...")
    params = {
        'query': 'Software Engineer',
        'location': 'Remote',
        'job_type': 'all'
    }
    
    response = requests.get(f"{BASE_URL}/api/match", params=params, headers=headers)
    print(f"Job search status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        jobs = data.get('jobs', [])
        print(f"✅ Backend returned {len(jobs)} jobs")
        
        # Check job sources
        sources = {}
        for job in jobs:
            source = job.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"Job sources: {sources}")
        
        # Show first few jobs
        for i, job in enumerate(jobs[:3]):
            print(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            print(f"     Source: {job.get('source', 'N/A')}")
            print(f"     Location: {job.get('location', 'N/A')}")
            print()
    else:
        print(f"❌ Job search failed: {response.status_code}")

if __name__ == "__main__":
    test_backend_jobspy() 