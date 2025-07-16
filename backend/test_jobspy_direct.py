import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_jobspy_queries():
    print("🧪 Testing JobSpy Directly with Different Queries")
    print("=" * 60)
    
    try:
        from jobspy_wrapper import JobSpyWrapper
        print("✅ Successfully imported JobSpyWrapper")
        
        # Initialize JobSpy
        wrapper = JobSpyWrapper()
        print("✅ JobSpyWrapper initialized successfully")
        
        # Test queries
        test_queries = [
            ("Full Stack Developer", "Cape Town"),
            ("Software Engineer", "Remote"),
            ("Software Engineer", "Cape Town"),
            ("Developer", "Remote"),
            ("Python Developer", "Remote"),
            ("Frontend Developer", "Remote"),
            ("Backend Developer", "Remote"),
        ]
        
        for query, location in test_queries:
            print(f"\n🔍 Testing: '{query}' in '{location}'")
            print("-" * 40)
            
            try:
                jobs = wrapper.search_jobs(query, location, max_results=10)
                print(f"✅ JobSpy found {len(jobs)} jobs")
                
                if jobs:
                    for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
                        print(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                        print(f"     Location: {job.get('location', 'N/A')}")
                        print(f"     Source: {job.get('source', 'N/A')}")
                        print(f"     URL: {job.get('url', 'N/A')[:50]}...")
                        print()
                else:
                    print("  ❌ No jobs found")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_jobspy_sites():
    print("\n🧪 Testing JobSpy Individual Sites")
    print("=" * 60)
    
    try:
        from jobspy_wrapper import JobSpyWrapper
        wrapper = JobSpyWrapper()
        
        # Test individual sites
        test_sites = ['indeed', 'linkedin', 'glassdoor', 'google']
        
        for site in test_sites:
            print(f"\n🔍 Testing site: {site}")
            print("-" * 30)
            
            try:
                jobs = wrapper.search_jobs_by_site("Software Engineer", "Remote", site=site, max_results=5)
                print(f"✅ {site.title()} found {len(jobs)} jobs")
                
                if jobs:
                    for i, job in enumerate(jobs[:2]):  # Show first 2 jobs
                        print(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                else:
                    print(f"  ❌ No jobs from {site}")
                    
            except Exception as e:
                print(f"  ❌ Error with {site}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Site test failed: {e}")
        return False

if __name__ == "__main__":
    print("Comprehensive JobSpy Testing")
    print("=" * 60)
    
    # Test different queries
    queries_work = test_jobspy_queries()
    
    # Test individual sites
    sites_work = test_jobspy_sites()
    
    print("\n" + "=" * 60)
    if queries_work and sites_work:
        print("🎉 JobSpy is working correctly!")
    else:
        print("⚠️  JobSpy has some issues")
    
    print("\n💡 If JobSpy returns no jobs for your specific query, it means:")
    print("   - The job sites don't have data for that location/query")
    print("   - The sites are blocking the scraper")
    print("   - The query is too specific or location is too narrow") 