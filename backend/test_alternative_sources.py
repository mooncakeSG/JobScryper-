import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from alternative_sources import AlternativeJobAggregator
    print("✅ Successfully imported AlternativeJobAggregator")
    
    # Test job search
    aggregator = AlternativeJobAggregator()
    jobs = aggregator.search_all_sources("Software Engineer", "Remote", max_per_source=5)
    print(f"✅ Alternative sources found {len(jobs)} jobs")
    
    if jobs:
        for i, job in enumerate(jobs[:3]):
            print(f"  {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} (Source: {job.get('source', 'N/A')})")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Job search failed: {e}") 