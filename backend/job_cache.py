"""
Job search caching for improved performance
"""
import json
import time
import hashlib
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class JobSearchCache:
    """Cache for job search results"""
    
    def __init__(self, cache_duration=3600):  # 1 hour default
        self.cache_duration = cache_duration
        self.cache: Dict[str, Dict] = {}
        
    def _generate_cache_key(self, query: str, location: str, job_type: str = "all") -> str:
        """Generate a cache key for the search parameters"""
        search_params = f"{query.lower().strip()}:{location.lower().strip()}:{job_type.lower()}"
        return hashlib.md5(search_params.encode()).hexdigest()
    
    def get_cached_results(self, query: str, location: str, job_type: str = "all") -> Optional[List[Dict]]:
        """Get cached job search results if available and not expired"""
        cache_key = self._generate_cache_key(query, location, job_type)
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                logger.info(f"Returning cached job results for '{query}' in '{location}'")
                return cached_data['jobs']
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
                logger.debug(f"Removed expired cache entry for '{query}' in '{location}'")
        
        return None
    
    def cache_results(self, query: str, location: str, jobs: List[Dict], job_type: str = "all"):
        """Cache job search results"""
        cache_key = self._generate_cache_key(query, location, job_type)
        
        self.cache[cache_key] = {
            'jobs': jobs,
            'timestamp': time.time(),
            'query': query,
            'location': location,
            'job_type': job_type
        }
        
        logger.info(f"Cached {len(jobs)} jobs for '{query}' in '{location}'")
        
        # Clean up old cache entries
        self._cleanup_expired()
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.cache.items()
            if current_time - data['timestamp'] > self.cache_duration
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        current_time = time.time()
        active_entries = sum(
            1 for data in self.cache.values()
            if current_time - data['timestamp'] < self.cache_duration
        )
        
        return {
            'total_entries': len(self.cache),
            'active_entries': active_entries,
            'cache_duration': self.cache_duration
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Job search cache cleared")

# Global job cache instance
job_cache = JobSearchCache() 