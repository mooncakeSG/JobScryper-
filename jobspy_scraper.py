"""
JobSpy-based Technology Job Scraper for Auto Applier

This module provides comprehensive technology job searching using the JobSpy library,
with specialized filtering and optimization for various tech roles including software development,
data science, DevOps, cybersecurity, IT support, and more.

Author: MooncakeSG 
Created: 2025-07-07
Updated: 2025-07-07 - Extended to support all tech roles
"""

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta

from jobspy_wrapper import JobSpyWrapper
from filters import JobFilter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechJobScraperConfig:
    """Configuration for Technology job scraping across multiple domains."""
    
    # Technology job titles organized by category
    TECH_JOB_TITLES = {
        'software_developer': [
            'Software Developer', 'Software Engineer', 'Full Stack Developer', 
            'Frontend Developer', 'Backend Developer', 'Web Developer', 
            'Mobile Developer', 'Application Developer', 'Python Developer',
            'Java Developer', 'JavaScript Developer', 'React Developer',
            'Node.js Developer', 'Angular Developer', 'Vue.js Developer',
            # SA-specific terms
            'Software Programmer', 'Web Application Developer', 'Mobile Application Developer',
            'C# Developer', '.NET Developer', 'PHP Developer', 'Systems Developer'
        ],
        'data_science': [
            'Data Scientist', 'Data Analyst', 'Machine Learning Engineer',
            'Data Engineer', 'Business Intelligence Analyst', 'Analytics Engineer',
            'ML Engineer', 'AI Engineer', 'Big Data Engineer', 'Statistical Analyst',
            # SA-specific terms
            'BI Analyst', 'BI Developer', 'Business Analyst', 'Reporting Analyst',
            'Database Analyst', 'Data Specialist', 'Analytics Specialist'
        ],
        'devops_cloud': [
            'DevOps Engineer', 'Cloud Engineer', 'Site Reliability Engineer',
            'Infrastructure Engineer', 'Platform Engineer', 'Cloud Architect',
            'AWS Engineer', 'Azure Engineer', 'GCP Engineer', 'Kubernetes Engineer',
            'Docker Engineer', 'CI/CD Engineer'
        ],
        'cybersecurity': [
            'Cybersecurity Analyst', 'Security Engineer', 'Information Security Analyst',
            'Security Architect', 'Penetration Tester', 'Security Consultant',
            'Incident Response Analyst', 'Compliance Analyst', 'Risk Analyst'
        ],
        'it_support': [
            'IT Support Specialist', 'IT Support Technician', 'Help Desk Technician',
            'Help Desk Specialist', 'Technical Support Specialist', 'Desktop Support Technician',
            'IT Support Analyst', 'Service Desk Analyst', 'Computer Support Specialist',
            'Technical Support Representative', 'IT Helpdesk Technician', 'Junior IT Support',
            'Level 1 Support', 'Level 2 Support', 'End User Support', 'Systems Support Specialist',
            # SA-specific terms
            'ICT Support', 'ICT Technician', 'ICT Support Officer', 'ICT Administrator',
            'Computer Support', 'Computer Support Technician', 'PC Support', 'PC Technician',
            'IT Officer', 'IT Assistant', 'IT Coordinator', 'IT Specialist', 'IT Consultant',
            'Systems Administrator', 'Network Administrator', 'IT Administrator'
        ],
        'product_management': [
            'Product Manager', 'Technical Product Manager', 'Product Owner',
            'Associate Product Manager', 'Senior Product Manager', 'Product Analyst',
            'Product Marketing Manager', 'Digital Product Manager'
        ],
        'qa_testing': [
            'QA Engineer', 'Test Engineer', 'Quality Assurance Analyst',
            'Software Tester', 'Automation Engineer', 'QA Analyst',
            'Test Automation Engineer', 'Performance Test Engineer'
        ],
        'ui_ux_design': [
            'UI Designer', 'UX Designer', 'UI/UX Designer', 'Product Designer',
            'Visual Designer', 'Interaction Designer', 'User Experience Designer',
            'Digital Designer', 'Design Systems Designer'
        ],
        'network_engineering': [
            'Network Engineer', 'Network Administrator', 'Network Architect',
            'Network Security Engineer', 'Wireless Network Engineer', 'Network Analyst',
            'Network Technician', 'Infrastructure Engineer'
        ]
    }
    
    # Flatten all titles for easy access
    ALL_TECH_TITLES = []
    for category_titles in TECH_JOB_TITLES.values():
        ALL_TECH_TITLES.extend(category_titles)
    
    # Keywords that indicate various tech roles
    TECH_KEYWORDS = {
        'software_developer': ['programming', 'coding', 'development', 'software', 'application', 'web', 'mobile'],
        'data_science': ['data', 'analytics', 'machine learning', 'python', 'sql', 'statistics', 'modeling'],
        'devops_cloud': ['devops', 'ci/cd', 'docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'automation'],
        'cybersecurity': ['security', 'cybersecurity', 'penetration', 'vulnerability', 'firewall', 'compliance'],
        'it_support': ['help desk', 'helpdesk', 'technical support', 'it support', 'desktop support', 'troubleshooting', 'ict support', 'computer support', 'pc support', 'systems administration', 'network administration'],
        'product_management': ['product', 'roadmap', 'stakeholder', 'agile', 'scrum', 'requirements'],
        'qa_testing': ['testing', 'qa', 'quality assurance', 'automation', 'selenium', 'bug'],
        'ui_ux_design': ['ui', 'ux', 'design', 'user experience', 'figma', 'sketch', 'prototyping'],
        'network_engineering': ['networking', 'cisco', 'router', 'switch', 'tcp/ip', 'vpn', 'firewall']
    }
    
    # Preferred job sites for tech roles (in order of preference)
    PREFERRED_SITES = ['indeed', 'linkedin', 'glassdoor', 'zip_recruiter']
    
    # Default search parameters
    DEFAULT_SEARCH_PARAMS = {
        'results_wanted': 20,  # Jobs per site
        'hours_old': 168,      # 1 week
        'country_indeed': 'USA',
        'distance': 25,        # Miles from location
        'is_remote': False,    # Will be set based on search
        'easy_apply': None     # Any application type
    }

class TechJobScraper:
    """
    Comprehensive job scraper for technology positions using JobSpy.
    Optimized for finding relevant tech opportunities across multiple domains including
    software development, data science, DevOps, cybersecurity, IT support, and more.
    """
    
    def __init__(self, config: Optional[TechJobScraperConfig] = None):
        """
        Initialize the Technology job scraper.
        
        Args:
            config: Configuration object for technology job searching
        """
        self.config = config or TechJobScraperConfig()
        self.jobspy_wrapper = JobSpyWrapper()
        self.job_filter = JobFilter()
        
        logger.info("🔧 TechJobScraper initialized successfully")
    
    def fetch_tech_jobs(
        self, 
        location: str = "Remote", 
        job_titles: Optional[List[str]] = None,
        job_categories: Optional[List[str]] = None,
        sites: Optional[List[str]] = None,
        results_per_site: int = 20,
        hours_old: int = 168,
        include_remote: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch technology jobs from multiple sources using JobSpy.
        
        Args:
            location (str): Job location or "Remote"
            job_titles (List[str], optional): Specific job titles to search for
            job_categories (List[str], optional): Job categories to include (e.g., ['software_developer', 'data_science'])
            sites (List[str], optional): Job sites to search
            results_per_site (int): Number of results per site
            hours_old (int): How old jobs can be (in hours)
            include_remote (bool): Whether to include remote positions
            
        Returns:
            List[Dict]: List of technology job postings
        """
        if job_titles is None:
            if job_categories is None:
                # Default to a mix of popular tech roles
                job_categories = ['software_developer', 'data_science', 'devops_cloud', 'it_support']
            
            job_titles = []
            for category in job_categories:
                if category in self.config.TECH_JOB_TITLES:
                    job_titles.extend(self.config.TECH_JOB_TITLES[category][:4])  # Top 4 from each category
        
        if sites is None:
            sites = self.config.PREFERRED_SITES
        
        all_jobs = []
        search_queries = self._generate_search_queries(job_titles, include_remote)
        
        logger.info(f"🎯 Starting technology job search in '{location}' using {len(sites)} sites")
        logger.info(f"📝 Search queries: {len(search_queries)} variations")
        if job_categories:
            logger.info(f"🔍 Job categories: {', '.join(job_categories)}")
        
        for i, (job_title, is_remote_search) in enumerate(search_queries):
            try:
                logger.info(f"🔍 Searching for '{job_title}' ({i+1}/{len(search_queries)})")
                
                # Determine location for search
                search_location = "Remote" if is_remote_search else location
                
                # Get jobs using JobSpy wrapper
                jobs = self.jobspy_wrapper.search_jobs(
                    job_title=job_title,
                    location=search_location,
                    sites=sites,
                    max_results=results_per_site
                )
                
                if jobs:
                    # Add search metadata
                    for job in jobs:
                        job['search_query'] = job_title
                        job['search_location'] = search_location
                        job['scraped_at'] = datetime.now().isoformat()
                    
                    all_jobs.extend(jobs)
                    logger.info(f"✅ Found {len(jobs)} jobs for '{job_title}'")
                else:
                    logger.warning(f"⚠️ No jobs found for '{job_title}'")
                
            except Exception as e:
                logger.error(f"❌ Error searching for '{job_title}': {str(e)}")
                continue
        
        # Remove duplicates and filter for technology relevance
        filtered_jobs = self._process_and_filter_jobs(all_jobs, job_categories or ['it_support'])
        
        logger.info(f"🎯 Technology job search completed: {len(filtered_jobs)} relevant jobs found")
        
        return filtered_jobs
    
    def _generate_search_queries(self, job_titles: List[str], include_remote: bool) -> List[tuple]:
        """
        Generate search queries with remote/on-site variations.
        
        Args:
            job_titles (List[str]): Base job titles
            include_remote (bool): Whether to include remote searches
            
        Returns:
            List[tuple]: List of (job_title, is_remote) tuples
        """
        queries = []
        
        # Add primary job titles (local search)
        for title in job_titles:
            queries.append((title, False))
        
        # Add international remote variations if requested
        if include_remote:
            remote_titles = []
            
            # Generate remote versions for each job category
            for title in job_titles:
                remote_titles.extend([
                    f"Remote {title}",
                    f"Work from Home {title}",
                    f"International {title}"
                ])
            
            # Add generic remote tech titles for broader international coverage
            remote_titles.extend([
                'Remote Software Developer',
                'Remote Data Scientist', 
                'Remote DevOps Engineer',
                'Remote Full Stack Developer',
                'Remote Frontend Developer',
                'Remote Backend Developer',
                'Remote Python Developer',
                'Remote JavaScript Developer'
            ])
            
            # Add each as remote search
            for title in remote_titles:
                queries.append((title, True))
        
        return queries
    
    def _process_and_filter_jobs(self, raw_jobs: List[Dict[str, Any]], job_categories: List[str]) -> List[Dict[str, Any]]:
        """
        Process raw jobs: remove duplicates, filter for relevance, and enhance data.
        
        Args:
            raw_jobs (List[Dict]): Raw job data from JobSpy
            
        Returns:
            List[Dict]: Processed and filtered jobs
        """
        if not raw_jobs:
            return []
        
        # Remove duplicates based on title + company + location
        seen_jobs = set()
        deduplicated_jobs = []
        
        for job in raw_jobs:
            # Create unique identifier
            job_id = (
                job.get('title', '').lower().strip(),
                job.get('company', '').lower().strip(),
                job.get('location', '').lower().strip()
            )
            
            if job_id not in seen_jobs:
                seen_jobs.add(job_id)
                deduplicated_jobs.append(job)
        
        logger.info(f"🔄 Deduplicated: {len(raw_jobs)} → {len(deduplicated_jobs)} jobs")
        
        # Filter for relevance based on job categories
        relevant_jobs = []
        for category in job_categories:
            category_jobs = self.job_filter.filter_jobs(deduplicated_jobs, job_category=category, min_score=0.2)
            relevant_jobs.extend(category_jobs)
        
        # Remove duplicates from multiple category filters
        seen_jobs = set()
        filtered_jobs = []
        for job in relevant_jobs:
            job_id = (job.get('title', ''), job.get('company', ''), job.get('location', ''))
            if job_id not in seen_jobs:
                seen_jobs.add(job_id)
                filtered_jobs.append(job)
        
        logger.info(f"🎯 Filtered for relevance: {len(deduplicated_jobs)} → {len(filtered_jobs)} {'/'.join(job_categories)} jobs")
        
        # Enhance job data
        enhanced_jobs = []
        for job in filtered_jobs:
            enhanced_job = self._enhance_job_data(job)
            enhanced_jobs.append(enhanced_job)
        
        # Sort by relevance and date
        enhanced_jobs.sort(key=lambda x: (x.get('it_support_score', 0), x.get('date_posted', '')), reverse=True)
        
        return enhanced_jobs
    
    def _enhance_job_data(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance job data with IT Support specific analysis.
        
        Args:
            job (Dict): Raw job data
            
        Returns:
            Dict: Enhanced job data
        """
        enhanced_job = job.copy()
        
        # Calculate IT Support relevance score
        it_support_score = self._calculate_it_support_score(job)
        enhanced_job['it_support_score'] = it_support_score
        
        # Identify experience level
        experience_level = self._identify_experience_level(job)
        enhanced_job['experience_level'] = experience_level
        
        # Check for remote work indicators
        is_remote = self._check_remote_indicators(job)
        enhanced_job['is_remote_confirmed'] = is_remote
        
        # Extract key requirements
        requirements = self._extract_key_requirements(job)
        enhanced_job['key_requirements'] = requirements
        
        # Add application urgency indicator
        urgency = self._assess_application_urgency(job)
        enhanced_job['application_urgency'] = urgency
        
        return enhanced_job
    
    def _calculate_it_support_score(self, job: Dict[str, Any]) -> float:
        """Calculate relevance score for IT Support role."""
        score = 0.0
        
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        combined_text = f"{title} {description}"
        
        # Score based on title keywords
        title_keywords = {
            'it support': 10, 'help desk': 10, 'helpdesk': 10,
            'technical support': 8, 'desktop support': 8,
            'service desk': 7, 'user support': 6, 'end user': 5
        }
        
        for keyword, points in title_keywords.items():
            if keyword in title:
                score += points
        
        # Score based on description keywords
        description_keywords = {
            'troubleshooting': 3, 'windows': 2, 'hardware': 2,
            'software': 2, 'network': 2, 'active directory': 3,
            'office 365': 2, 'remote desktop': 2, 'ticketing': 3
        }
        
        for keyword, points in description_keywords.items():
            if keyword in description:
                score += points
        
        # Normalize score to 0-100 range
        return min(score, 100.0)
    
    def _identify_experience_level(self, job: Dict[str, Any]) -> str:
        """Identify experience level required for the job."""
        text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        
        if any(term in text for term in ['entry level', 'junior', 'associate', 'level 1', 'trainee']):
            return 'Entry Level'
        elif any(term in text for term in ['senior', 'lead', 'principal', 'level 3', 'expert']):
            return 'Senior'
        elif any(term in text for term in ['mid', 'level 2', 'intermediate', '2-4 years', '3-5 years']):
            return 'Mid-Level'
        else:
            return 'Not Specified'
    
    def _check_remote_indicators(self, job: Dict[str, Any]) -> bool:
        """Check if job has strong remote work indicators."""
        text = f"{job.get('title', '')} {job.get('description', '')} {job.get('location', '')}".lower()
        
        remote_indicators = [
            'remote', 'work from home', 'wfh', 'telecommute', 'virtual',
            'anywhere', 'distributed team', 'home office', 'remote-first'
        ]
        
        return any(indicator in text for indicator in remote_indicators)
    
    def _extract_key_requirements(self, job: Dict[str, Any]) -> List[str]:
        """Extract key technical requirements from job description."""
        description = job.get('description', '').lower()
        requirements = []
        
        # Technical requirements to look for
        tech_requirements = [
            'active directory', 'windows 10', 'windows 11', 'office 365',
            'azure', 'aws', 'linux', 'macos', 'networking', 'tcp/ip',
            'dhcp', 'dns', 'vpn', 'firewall', 'antivirus', 'backup',
            'vmware', 'hyper-v', 'citrix', 'remote desktop', 'powershell',
            'itil', 'service now', 'jira', 'freshservice'
        ]
        
        for req in tech_requirements:
            if req in description:
                requirements.append(req.title())
        
        return requirements[:10]  # Return top 10
    
    def _assess_application_urgency(self, job: Dict[str, Any]) -> str:
        """Assess how urgent the application should be."""
        text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        
        urgent_indicators = ['urgent', 'immediate start', 'asap', 'start immediately']
        high_indicators = ['hiring now', 'quick hire', 'fast track']
        
        if any(indicator in text for indicator in urgent_indicators):
            return 'Urgent'
        elif any(indicator in text for indicator in high_indicators):
            return 'High'
        else:
            return 'Normal'
    
    def search_specific_companies(self, companies: List[str], location: str = "Remote") -> List[Dict[str, Any]]:
        """
        Search for IT Support jobs at specific companies.
        
        Args:
            companies (List[str]): List of company names to target
            location (str): Location for search
            
        Returns:
            List[Dict]: IT Support jobs at specified companies
        """
        all_jobs = []
        
        for company in companies:
            try:
                # Search with company-specific query
                query = f"IT Support {company}"
                jobs = self.jobspy_wrapper.search_jobs(
                    job_title=query,
                    location=location,
                    sites=['indeed', 'linkedin'],
                    results_wanted=10
                )
                
                # Filter to only include jobs from the target company
                company_jobs = [
                    job for job in jobs 
                    if company.lower() in job.get('company', '').lower()
                ]
                
                all_jobs.extend(company_jobs)
                logger.info(f"🏢 Found {len(company_jobs)} IT Support jobs at {company}")
                
            except Exception as e:
                logger.error(f"❌ Error searching {company}: {str(e)}")
        
        return self._process_and_filter_jobs(all_jobs)
    
    def get_trending_it_skills(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze jobs to identify trending IT skills.
        
        Args:
            jobs (List[Dict]): List of job postings
            
        Returns:
            Dict[str, int]: Skill frequency count
        """
        skill_counts = {}
        
        # IT skills to track
        it_skills = [
            'windows', 'linux', 'macos', 'active directory', 'office 365',
            'azure', 'aws', 'powershell', 'python', 'sql', 'networking',
            'tcp/ip', 'dhcp', 'dns', 'vpn', 'firewall', 'antivirus',
            'backup', 'vmware', 'hyper-v', 'citrix', 'exchange',
            'sharepoint', 'teams', 'itil', 'servicenow', 'jira'
        ]
        
        for job in jobs:
            description = job.get('description', '').lower()
            for skill in it_skills:
                if skill in description:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by frequency
        sorted_skills = dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_skills

# Convenience functions
def fetch_tech_jobs(location: str = "Remote", job_categories: Optional[List[str]] = None, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Convenience function to fetch technology jobs.
    
    Args:
        location (str): Job location
        job_categories (List[str], optional): Job categories to include
        max_results (int): Maximum number of results
        
    Returns:
        List[Dict]: Technology job postings
    """
    scraper = TechJobScraper()
    return scraper.fetch_tech_jobs(
        location=location,
        job_categories=job_categories,
        results_per_site=max_results // 4,  # Distribute across 4 sites
        include_remote=True
    )

def fetch_it_support_jobs(location: str = "Remote", max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Convenience function to fetch IT Support jobs (backward compatibility).
    
    Args:
        location (str): Job location
        max_results (int): Maximum number of results
        
    Returns:
        List[Dict]: IT Support job postings
    """
    return fetch_tech_jobs(location=location, job_categories=['it_support'], max_results=max_results)

def search_it_jobs_by_company(companies: List[str], location: str = "Remote") -> List[Dict[str, Any]]:
    """
    Convenience function to search IT jobs by specific companies.
    
    Args:
        companies (List[str]): Target companies
        location (str): Job location
        
    Returns:
        List[Dict]: Company-specific IT Support jobs
    """
    scraper = TechJobScraper()
    return scraper.search_specific_companies(companies, location)

if __name__ == "__main__":
    # Test the Technology job scraper
    logger.info("🧪 Testing TechJobScraper...")
    
    try:
        scraper = TechJobScraper()
        
        # Test with a small search across multiple tech categories
        test_jobs = scraper.fetch_tech_jobs(
            location="Remote",
            job_categories=['software_developer', 'it_support'],
            results_per_site=3
        )
        
        if test_jobs:
            print(f"✅ Test successful! Found {len(test_jobs)} technology jobs")
            print(f"📊 Average tech relevance score: {sum(job.get('it_support_score', 0) for job in test_jobs) / len(test_jobs):.1f}")
            
            # Show trending skills
            trending_skills = scraper.get_trending_it_skills(test_jobs)
            top_skills = list(trending_skills.items())[:5]
            print(f"🔥 Top trending skills: {top_skills}")
            
            # Show job categories found
            job_titles = [job.get('title', 'Unknown') for job in test_jobs[:5]]
            print(f"📋 Sample job titles: {job_titles}")
        else:
            print("⚠️ Test completed but no jobs found")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("ℹ️ TechJobScraper ready for use.") 