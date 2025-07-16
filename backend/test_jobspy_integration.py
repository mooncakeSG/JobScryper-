import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_jobspy_wrapper():
    print("🧪 Testing JobSpy Integration")
    
    try:
        from jobspy_wrapper import JobSpyWrapper
        print("✅ Successfully imported JobSpyWrapper")
        
        # Test JobSpy initialization
        wrapper = JobSpyWrapper()
        print("✅ JobSpyWrapper initialized successfully")
        
        # Test job search
        print("\n🔍 Testing job search...")
        jobs = wrapper.search_jobs("Software Engineer", "Remote", max_results=5)
        print(f"✅ JobSpy found {len(jobs)} jobs")
        
        if jobs:
            for i, job in enumerate(jobs[:3]):
                print(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} (Source: {job.get('source', 'N/A')})")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ JobSpy test failed: {e}")
        return False

def test_backend_integration():
    print("\n🧪 Testing Backend Integration")
    
    try:
        import requests
        import json
        
        # Test the backend health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend health: {health_data['status']}")
            print(f"   Services: {health_data['services']}")
            
            if health_data['services'].get('job_spy_wrapper'):
                print("✅ JobSpyWrapper is available in backend")
                return True
            else:
                print("❌ JobSpyWrapper not available in backend")
                return False
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing JobSpy Integration with Backend")
    print("=" * 50)
    
    # Test JobSpy directly
    jobspy_works = test_jobspy_wrapper()
    
    # Test backend integration
    backend_works = test_backend_integration()
    
    print("\n" + "=" * 50)
    if jobspy_works and backend_works:
        print("🎉 JobSpy integration is working perfectly!")
    elif jobspy_works:
        print("⚠️  JobSpy works but backend integration needs attention")
    else:
        print("❌ JobSpy integration has issues") 