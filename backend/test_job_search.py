import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from jobspy_wrapper import JobSpyWrapper
    print("✅ Successfully imported JobSpyWrapper")
    
    # Test job search
    wrapper = JobSpyWrapper()
    jobs = wrapper.search_jobs("Software Engineer", "Remote", max_results=5)
    print(f"✅ Job search found {len(jobs)} jobs")
    
    if jobs:
        for i, job in enumerate(jobs[:3]):
            print(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Job search failed: {e}") 