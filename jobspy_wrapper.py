import logging
import pandas as pd
from typing import List, Dict, Any
from jobspy import scrape_jobs
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobSpyWrapper:
    """
    Wrapper class for JobSpy library to integrate with our Streamlit application.
    Provides robust job scraping from multiple sources with anti-blocking capabilities.
    """
    
    def __init__(self):
        self.supported_sites = [
            'indeed', 'linkedin', 'zip_recruiter', 'glassdoor', 
            'google', 'bayt', 'naukri'
        ]
        logger.info("JobSpy wrapper initialized with supported sites: %s", self.supported_sites)
    
    def search_jobs(self, job_title: str, location: str = "Remote", 
                   sites: List[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs using JobSpy across multiple job boards.
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            sites: List of job sites to search (default: indeed, linkedin, glassdoor)
            max_results: Maximum number of results per site
            
        Returns:
            List of job dictionaries in our standard format
        """
        if sites is None:
            # Default to the most reliable sites (will be filtered by country)
            sites = ['indeed', 'linkedin', 'glassdoor', 'google']
        
        # Validate sites
        valid_sites = [site for site in sites if site in self.supported_sites]
        if not valid_sites:
            logger.warning("No valid sites provided. Using default sites.")
            valid_sites = ['indeed', 'linkedin']
        
        # Determine country based on location
        country_indeed = self._get_indeed_country(location)
        
        # Filter sites based on country support
        valid_sites = self._filter_sites_by_country(valid_sites, country_indeed)
        
        logger.info(f"Searching for '{job_title}' in '{location}' on sites: {valid_sites} (Country: {country_indeed})")
        
        try:
            # Use JobSpy to scrape jobs
            jobs_df = scrape_jobs(
                site_name=valid_sites,
                search_term=job_title,
                location=location,
                results_wanted=max_results,
                hours_old=168,  # Jobs from last week
                country_indeed=country_indeed,  # Dynamic country setting
                description_format='markdown',  # Get markdown descriptions
                # linkedin_fetch_description=True,  # Get full LinkedIn descriptions (slower)
                verbose=1  # Reduced verbosity
            )
            
            if jobs_df is not None and len(jobs_df) > 0:
                logger.info(f"JobSpy found {len(jobs_df)} jobs total")
                
                # Convert to our standard format
                standardized_jobs = self._standardize_jobs(jobs_df)
                logger.info(f"Standardized {len(standardized_jobs)} jobs")
                
                return standardized_jobs
            else:
                logger.warning("JobSpy returned no jobs")
                # Try fallback strategy for SA searches
                if country_indeed == 'south africa':
                    return self._fallback_sa_search(job_title, location, max_results)
                return []
                
        except Exception as e:
            logger.error(f"Error during JobSpy search: {e}")
            # Try fallback strategy for SA searches
            if country_indeed == 'south africa':
                logger.info("Attempting fallback search for South Africa...")
                return self._fallback_sa_search(job_title, location, max_results)
            return []
    
    def _standardize_jobs(self, jobs_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convert JobSpy DataFrame to our standard job format.
        
        Args:
            jobs_df: DataFrame from JobSpy
            
        Returns:
            List of standardized job dictionaries
        """
        standardized_jobs = []
        
        for _, job in jobs_df.iterrows():
            try:
                # Map JobSpy fields to our format
                standardized_job = {
                    'title': str(job.get('title', 'Unknown Title')),
                    'company': str(job.get('company', 'Unknown Company')),
                    'location': str(job.get('location', 'Not specified')),
                    'description': self._clean_description(job.get('description', '')),
                    'url': str(job.get('job_url', '')),
                    'salary': self._format_salary(job),
                    'posted_date': self._format_date(job.get('date_posted')),
                    'source': str(job.get('site', 'JobSpy')).title(),
                    'remote': self._is_remote(job),
                    'easy_apply': False,  # JobSpy doesn't track this consistently
                    'job_type': str(job.get('job_type', '')),
                    'company_url': str(job.get('company_url', '')),
                    'job_level': str(job.get('job_level', '')),
                    'company_industry': str(job.get('company_industry', ''))
                }
                
                # Only add jobs with valid titles and companies
                if (standardized_job['title'] != 'Unknown Title' and 
                    standardized_job['company'] != 'Unknown Company'):
                    standardized_jobs.append(standardized_job)
                    
            except Exception as e:
                logger.debug(f"Error standardizing job: {e}")
                continue
        
        return standardized_jobs
    
    def _clean_description(self, description: str) -> str:
        """Clean and truncate job description."""
        if not description or description == 'nan':
            return 'No description available'
        
        # Remove excessive whitespace and truncate
        cleaned = ' '.join(str(description).split())
        return cleaned[:500] + '...' if len(cleaned) > 500 else cleaned
    
    def _format_salary(self, job: pd.Series) -> str:
        """Format salary information from JobSpy data."""
        try:
            min_amount = job.get('min_amount')
            max_amount = job.get('max_amount')
            interval = job.get('interval', '')
            currency = job.get('currency', '$')
            
            # Handle different currency symbols
            if currency == 'ZAR' or currency == 'R':
                currency_symbol = 'R'
            elif currency == 'USD' or currency == '$':
                currency_symbol = '$'
            elif currency == 'EUR' or currency == '€':
                currency_symbol = '€'
            elif currency == 'GBP' or currency == '£':
                currency_symbol = '£'
            else:
                currency_symbol = currency
            
            if pd.notna(min_amount) and pd.notna(max_amount):
                if interval == 'yearly':
                    return f"{currency_symbol}{int(min_amount):,} - {currency_symbol}{int(max_amount):,} /year"
                elif interval == 'hourly':
                    return f"{currency_symbol}{min_amount} - {currency_symbol}{max_amount} /hour"
                else:
                    return f"{currency_symbol}{int(min_amount):,} - {currency_symbol}{int(max_amount):,}"
            elif pd.notna(min_amount):
                return f"{currency_symbol}{int(min_amount):,}+ /{interval or 'year'}"
            else:
                return ""
        except:
            return ""
    
    def _format_date(self, date_posted) -> str:
        """Format posted date."""
        if pd.notna(date_posted):
            try:
                # Convert to string if it's a datetime
                if hasattr(date_posted, 'strftime'):
                    return date_posted.strftime('%Y-%m-%d')
                else:
                    return str(date_posted)
            except:
                return str(date_posted)
        return ""
    
    def _is_remote(self, job: pd.Series) -> bool:
        """Determine if job is remote."""
        is_remote = job.get('is_remote', False)
        location = str(job.get('location', '')).lower()
        
        return (bool(is_remote) or 
                'remote' in location or 
                'anywhere' in location or
                'work from home' in location)
    
    def _get_indeed_country(self, location: str) -> str:
        """
        Determine the appropriate Indeed country setting based on location.
        
        Args:
            location: Search location string
            
        Returns:
            Country code for Indeed searches
        """
        location_lower = location.lower()
        
        # South African locations
        if any(sa_term in location_lower for sa_term in [
            'south africa', 'cape town', 'johannesburg', 'durban', 
            'eastern cape', 'port elizabeth', 'east london', 'grahamstown',
            'gauteng', 'western cape', 'kwazulu-natal'
        ]):
            return 'south africa'
        
        # Remote searches - default to international (USA for broader reach)
        elif 'remote' in location_lower:
            return 'USA'  # USA Indeed has the most international remote jobs
        
        # Default to USA for other international searches
        else:
            return 'USA'
    
    def _filter_sites_by_country(self, sites: List[str], country: str) -> List[str]:
        """
        Filter job sites based on country support.
        
        Args:
            sites: List of job sites to filter
            country: Country for job search
            
        Returns:
            List of supported sites for the country
        """
        if country.lower() == 'south africa':
            # Sites that work well with South African searches
            supported_sites = {
                'indeed': True,        # Indeed SA works well
                'linkedin': True,      # LinkedIn has good SA coverage
                'glassdoor': False,    # Glassdoor doesn't support SA
                'zip_recruiter': False, # ZipRecruiter is US-focused
                'google': True,        # Google Jobs has SA coverage
                'bayt': False,         # Bayt is Middle East focused
                'naukri': False        # Naukri is India focused
            }
        else:
            # International/USA sites
            supported_sites = {
                'indeed': True,
                'linkedin': True,
                'glassdoor': True,
                'zip_recruiter': True,
                'google': True,
                'bayt': False,         # Still not relevant for international
                'naukri': False        # Still not relevant for international
            }
        
        # Filter sites based on support
        filtered_sites = [site for site in sites if supported_sites.get(site, False)]
        
        # Ensure we have at least one site
        if not filtered_sites:
            logger.warning(f"No supported sites for country '{country}'. Defaulting to Indeed.")
            filtered_sites = ['indeed']
        
        return filtered_sites
    
    def _fallback_sa_search(self, job_title: str, location: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Fallback search strategy for South African locations.
        
        Args:
            job_title: Job title to search for
            location: Original SA location
            max_results: Maximum number of results
            
        Returns:
            List of job dictionaries from fallback search
        """
        fallback_strategies = [
            # Try with just Indeed (most reliable for SA)
            (['indeed'], location),
            # Try with broader SA locations
            (['indeed'], 'South Africa'),
            # Try with major SA cities
            (['indeed'], 'Cape Town, South Africa'),
            (['indeed'], 'Johannesburg, South Africa'),
            # Try remote search as last resort
            (['indeed'], 'Remote')
        ]
        
        for sites, fallback_location in fallback_strategies:
            try:
                logger.info(f"Trying fallback: {sites} in {fallback_location}")
                
                jobs_df = scrape_jobs(
                    site_name=sites,
                    search_term=job_title,
                    location=fallback_location,
                    results_wanted=min(max_results, 10),  # Limit results for fallback
                    hours_old=168,
                    country_indeed='south africa' if 'south africa' in fallback_location.lower() else 'USA',
                    description_format='markdown',
                    verbose=0  # Reduce verbosity for fallback
                )
                
                if jobs_df is not None and len(jobs_df) > 0:
                    logger.info(f"Fallback successful: found {len(jobs_df)} jobs")
                    return self._standardize_jobs(jobs_df)
                    
            except Exception as e:
                logger.debug(f"Fallback attempt failed: {e}")
                continue
        
        logger.warning("All fallback strategies failed for South African search")
        return []
    
    def search_jobs_by_site(self, job_title: str, location: str = "Remote", 
                           site: str = 'indeed', max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search jobs on a specific site.
        
        Args:
            job_title: Job title to search for
            location: Location to search in
            site: Specific site to search ('indeed', 'linkedin', etc.)
            max_results: Maximum number of results
            
        Returns:
            List of job dictionaries
        """
        return self.search_jobs(job_title, location, [site], max_results)
    
    def get_available_sites(self) -> List[str]:
        """Get list of available job sites."""
        return self.supported_sites.copy()
    
    def search_multiple_terms(self, job_titles: List[str], location: str = "Remote",
                             sites: List[str] = None, max_results_per_term: int = 20) -> List[Dict[str, Any]]:
        """
        Search for multiple job titles and combine results.
        
        Args:
            job_titles: List of job titles to search for
            location: Location to search in  
            sites: List of job sites to search
            max_results_per_term: Maximum results per job title
            
        Returns:
            Combined list of job dictionaries
        """
        all_jobs = []
        
        for job_title in job_titles:
            logger.info(f"Searching for: {job_title}")
            jobs = self.search_jobs(job_title, location, sites, max_results_per_term)
            all_jobs.extend(jobs)
            
            # Add small delay between searches
            time.sleep(1)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        
        for job in all_jobs:
            url = job.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
            elif not url:  # Keep jobs without URLs
                unique_jobs.append(job)
        
        logger.info(f"Found {len(unique_jobs)} unique jobs across all search terms")
        return unique_jobs

# Example usage and testing
if __name__ == "__main__":
    wrapper = JobSpyWrapper()
    
    # Test basic search
    print("Testing JobSpy wrapper...")
    jobs = wrapper.search_jobs("IT Support", "Remote", sites=['indeed'], max_results=5)
    
    print(f"Found {len(jobs)} jobs:")
    for i, job in enumerate(jobs[:3]):
        print(f"{i+1}. {job['title']} at {job['company']} - {job['source']}")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job['salary']}")
        print(f"   Remote: {job['remote']}")
        print(f"   URL: {job['url'][:50]}...")
        print() 