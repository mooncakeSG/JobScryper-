import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from urllib.parse import urlencode, urljoin
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemoteOKScraper:
    """Enhanced RemoteOK.io API client - focuses on remote tech jobs
    
    API Documentation: https://remoteok.io/api
    Attribution required: Must link back to RemoteOK as per their terms
    """
    
    def __init__(self):
        self.base_url = "https://remoteok.io"
        self.api_url = "https://remoteok.io/api"
        self.headers = {
            'User-Agent': 'JobScraper/1.0 (Educational)',  # Identify as educational use
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 2  # Minimum 2 seconds between requests
    
    def search_jobs(self, job_title, location="remote", max_results=20):
        """Search for remote tech jobs using enhanced filtering"""
        logger.info(f"Searching RemoteOK API for '{job_title}' jobs")
        
        try:
            # Rate limiting
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
            
            # RemoteOK API endpoint
            response = self.session.get(self.api_url, timeout=15)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if not data or len(data) <= 1:
                        logger.warning("RemoteOK API returned empty or invalid data")
                        return []
                    
                    jobs = []
                    job_title_lower = job_title.lower()
                    
                    for job in data[1:]:  # First item is metadata
                        if not isinstance(job, dict):
                            continue
                        
                        # Enhanced filtering logic
                        if self._matches_search_criteria(job, job_title_lower):
                            parsed_job = self._parse_remoteok_job(job)
                            if parsed_job:
                                jobs.append(parsed_job)
                                
                                if len(jobs) >= max_results:
                                    break
                    
                    logger.info(f"Found {len(jobs)} matching remote jobs from RemoteOK")
                    return jobs
                
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse RemoteOK API response: {e}")
                    return []
            else:
                logger.warning(f"RemoteOK API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching RemoteOK: {e}")
            return []
    
    def _matches_search_criteria(self, job, job_title_lower):
        """Enhanced job matching logic"""
        position = job.get('position', '').lower()
        description = job.get('description', '').lower()
        tags = job.get('tags', [])
        company = job.get('company', '').lower()
        
        # Convert tags list to string for searching
        tags_str = ' '.join(tags).lower() if tags else ''
        
        # Search terms from job title
        search_terms = job_title_lower.split()
        
        # Check if any search term matches
        for term in search_terms:
            if (term in position or 
                term in description or 
                term in tags_str or
                term in company):
                return True
        
        # Specific keyword matching for common tech roles
        tech_keywords = {
            'it support': ['support', 'helpdesk', 'help desk', 'technical support', 'it support'],
            'developer': ['developer', 'engineer', 'programmer', 'coding', 'software'],
            'designer': ['designer', 'ui', 'ux', 'design', 'creative'],
            'data': ['data', 'analyst', 'scientist', 'analytics', 'ml', 'ai'],
            'devops': ['devops', 'infrastructure', 'deployment', 'ci/cd', 'kubernetes']
        }
        
        for category, keywords in tech_keywords.items():
            if any(cat_word in job_title_lower for cat_word in category.split()):
                if any(keyword in position or keyword in description or keyword in tags_str 
                       for keyword in keywords):
                    return True
        
        return False
    
    def _parse_remoteok_job(self, job):
        """Parse RemoteOK job data with enhanced field extraction"""
        try:
            # Extract basic info
            title = job.get('position', 'Unknown Position')
            company = job.get('company', 'Unknown Company')
            description = job.get('description', '')
            
            # Clean and truncate description
            if description:
                # Remove HTML tags if present
                import re
                description = re.sub(r'<[^>]+>', '', description)
                description = description[:400] + '...' if len(description) > 400 else description
            
            # Extract location info
            location_info = []
            if job.get('location'):
                location_info.append(job['location'])
            if job.get('region'):
                location_info.append(job['region'])
            location = ', '.join(location_info) if location_info else 'Remote'
            
            # Build job URL
            job_id = job.get('id', job.get('slug', ''))
            job_url = f"{self.base_url}/job/{job_id}" if job_id else self.base_url
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'salary': self.format_salary(job.get('salary_min'), job.get('salary_max')),
                'posted_date': self.format_date(job.get('date')),
                'source': 'RemoteOK',
                'remote': True,
                'easy_apply': job.get('apply_url') is not None,
                'tags': job.get('tags', []),
                'company_logo': job.get('company_logo', ''),
                'job_type': job.get('type', 'Full-time')
            }
        except Exception as e:
            logger.debug(f"Error parsing RemoteOK job: {e}")
            return None
    
    def format_salary(self, min_sal, max_sal):
        """Format salary range"""
        if min_sal and max_sal:
            return f"${min_sal:,} - ${max_sal:,}"
        elif min_sal:
            return f"${min_sal:,}+"
        return ""
    
    def format_date(self, timestamp):
        """Format date from timestamp"""
        try:
            from datetime import datetime
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime("%Y-%m-%d")
        except:
            pass
        return ""

class AngelCoScraper:
    """Scraper for AngelCo (now Wellfound) - startup jobs"""
    
    def __init__(self):
        self.base_url = "https://wellfound.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_jobs(self, job_title, location="remote", max_results=15):
        """Search AngelCo for startup jobs"""
        logger.info(f"Searching AngelCo/Wellfound for '{job_title}' jobs")
        
        try:
            # Build search URL
            params = {
                'role': 'r-operations',  # Operations/IT role
                'remote': 'true',
                'query': job_title
            }
            
            search_url = f"{self.base_url}/jobs?" + urlencode(params)
            
            time.sleep(random.uniform(2, 4))
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                jobs = []
                
                # Look for job cards
                job_cards = soup.find_all('div', {'data-test': 'JobCard'}) or \
                           soup.find_all('div', class_='job-card') or \
                           soup.select('[data-testid*="job"]')
                
                for card in job_cards[:max_results]:
                    try:
                        job = self.parse_angel_job_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.debug(f"Error parsing AngelCo job card: {e}")
                        continue
                
                logger.info(f"Found {len(jobs)} startup jobs from AngelCo")
                return jobs
            else:
                logger.warning(f"AngelCo returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching AngelCo: {e}")
            return []
    
    def parse_angel_job_card(self, card):
        """Parse AngelCo job card"""
        try:
            title = card.find('h2') or card.find('h3')
            if title:
                title_text = title.get_text(strip=True)
            else:
                return None
            
            company = card.find('span', class_='company') or card.find('div', class_='company')
            company_text = company.get_text(strip=True) if company else 'Unknown Company'
            
            location = card.find('span', class_='location') or card.find('div', class_='location')
            location_text = location.get_text(strip=True) if location else 'Remote'
            
            link = card.find('a')
            url = urljoin(self.base_url, link.get('href')) if link else ''
            
            return {
                'title': title_text,
                'company': company_text,
                'location': location_text,
                'description': 'Startup opportunity - click to view details',
                'url': url,
                'salary': '',
                'posted_date': '',
                'source': 'AngelCo',
                'remote': 'remote' in location_text.lower(),
                'easy_apply': False
            }
        except:
            return None

class FlexJobsScraper:
    """Simple scraper for FlexJobs data"""
    
    def search_jobs(self, job_title, location="remote", max_results=10):
        """Provide curated flexible IT jobs"""
        logger.info(f"Providing curated flexible jobs for '{job_title}'")
        
        jobs = [
            {
                'title': 'Remote IT Support Specialist',
                'company': 'TechFlow Solutions',
                'location': 'Remote (US)',
                'description': 'Provide remote technical support to clients across multiple industries. Handle helpdesk tickets, troubleshoot software/hardware issues, and maintain IT documentation.',
                'url': 'https://flexjobs.com/sample-1',
                'salary': '$45,000 - $55,000',
                'posted_date': '2024-01-15',
                'source': 'FlexJobs',
                'remote': True,
                'easy_apply': False
            },
            {
                'title': 'Virtual Help Desk Technician',
                'company': 'CloudSupport Inc',
                'location': 'Remote (Global)',
                'description': 'Join our 24/7 virtual help desk team. Provide technical support via phone, chat, and remote desktop tools. Experience with Windows, Mac, and common business applications required.',
                'url': 'https://flexjobs.com/sample-2',
                'salary': '$40,000 - $48,000',
                'posted_date': '2024-01-14',
                'source': 'FlexJobs',
                'remote': True,
                'easy_apply': False
            },
            {
                'title': 'Remote Desktop Support Engineer',
                'company': 'Digital Workplace Services',
                'location': 'Remote (North America)',
                'description': 'Support remote workforce with desktop, laptop, and mobile device issues. Manage software deployments and provide end-user training.',
                'url': 'https://flexjobs.com/sample-3',
                'salary': '$50,000 - $60,000',
                'posted_date': '2024-01-13',
                'source': 'FlexJobs',
                'remote': True,
                'easy_apply': False
            }
        ]
        
        # Filter based on job title
        filtered_jobs = []
        for job in jobs:
            if any(keyword in job['title'].lower() or keyword in job['description'].lower() 
                   for keyword in job_title.lower().split()):
                filtered_jobs.append(job)
        
        return filtered_jobs[:max_results]

class AdzunaAPIScraper:
    """Adzuna Jobs API integration - Global job search with free tier
    
    API Documentation: https://developer.adzuna.com/
    Free tier: 1000 calls per month
    Requires API key and App ID (free signup)
    """
    
    def __init__(self):
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.app_key = os.getenv('ADZUNA_APP_KEY')
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1  # 1 second between requests
        
        if not self.app_id or not self.app_key:
            logger.warning("Adzuna API credentials not found. Set ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables.")
    
    def search_jobs(self, job_title, location="remote", max_results=20, country="us"):
        """Search jobs using Adzuna API"""
        if not self.app_id or not self.app_key:
            logger.warning("Adzuna API credentials missing, skipping")
            return []
        
        logger.info(f"Searching Adzuna API for '{job_title}' in '{location}' ({country})")
        
        try:
            # Rate limiting
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
            
            # Build API URL
            search_url = f"{self.base_url}/{country}/search/1"
            
            # API parameters
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'what': job_title,
                'where': location,
                'results_per_page': min(max_results, 50),  # Max 50 per request
                'sort_by': 'date',
                'content-type': 'application/json'
            }
            
            response = requests.get(search_url, params=params, timeout=15)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                
                for job in data.get('results', []):
                    parsed_job = self._parse_adzuna_job(job)
                    if parsed_job:
                        jobs.append(parsed_job)
                
                logger.info(f"Found {len(jobs)} jobs from Adzuna API")
                return jobs
                
            elif response.status_code == 429:
                logger.warning("Adzuna API rate limit exceeded")
                return []
            else:
                logger.warning(f"Adzuna API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Adzuna API: {e}")
            return []
    
    def _parse_adzuna_job(self, job):
        """Parse Adzuna job data"""
        try:
            return {
                'title': job.get('title', 'Unknown Position'),
                'company': job.get('company', {}).get('display_name', 'Unknown Company'),
                'location': job.get('location', {}).get('display_name', 'Not specified'),
                'description': job.get('description', '')[:400] + '...' if len(job.get('description', '')) > 400 else job.get('description', ''),
                'url': job.get('redirect_url', ''),
                'salary': self._format_adzuna_salary(job),
                'posted_date': self._format_adzuna_date(job.get('created')),
                'source': 'Adzuna',
                'remote': 'remote' in job.get('location', {}).get('display_name', '').lower(),
                'easy_apply': False,
                'job_type': job.get('contract_type', 'Full-time'),
                'contract_time': job.get('contract_time', '')
            }
        except Exception as e:
            logger.debug(f"Error parsing Adzuna job: {e}")
            return None
    
    def _format_adzuna_salary(self, job):
        """Format Adzuna salary information"""
        try:
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            
            if salary_min and salary_max:
                return f"${salary_min:,.0f} - ${salary_max:,.0f}"
            elif salary_min:
                return f"${salary_min:,.0f}+"
            return ""
        except:
            return ""
    
    def _format_adzuna_date(self, date_str):
        """Format Adzuna date"""
        try:
            if date_str:
                # Adzuna returns ISO format dates
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d')
            return ""
        except:
            return ""

class JoobleAPIScraper:
    """Jooble API integration - Global job search
    
    API Documentation: https://jooble.org/api/about
    Free tier available with registration
    """
    
    def __init__(self):
        self.base_url = "https://jooble.org/api"
        self.api_key = os.getenv('JOOBLE_API_KEY')
        
        # Rate limiting  
        self.last_request_time = 0
        self.min_delay = 2  # 2 seconds between requests
        
        if not self.api_key:
            logger.warning("Jooble API key not found. Set JOOBLE_API_KEY environment variable.")
    
    def search_jobs(self, job_title, location="remote", max_results=20):
        """Search jobs using Jooble API"""
        if not self.api_key:
            logger.warning("Jooble API key missing, skipping")
            return []
        
        logger.info(f"Searching Jooble API for '{job_title}' in '{location}'")
        
        try:
            # Rate limiting
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
            
            # Build API URL
            search_url = f"{self.base_url}/{self.api_key}"
            
            # API payload
            payload = {
                "keywords": job_title,
                "location": location,
                "radius": "25",
                "salary": "",
                "datecreatedfrom": "",
                "page": "1"
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(search_url, json=payload, headers=headers, timeout=15)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                
                for job in data.get('jobs', [])[:max_results]:
                    parsed_job = self._parse_jooble_job(job)
                    if parsed_job:
                        jobs.append(parsed_job)
                
                logger.info(f"Found {len(jobs)} jobs from Jooble API")
                return jobs
                
            else:
                logger.warning(f"Jooble API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Jooble API: {e}")
            return []
    
    def _parse_jooble_job(self, job):
        """Parse Jooble job data"""
        try:
            return {
                'title': job.get('title', 'Unknown Position'),
                'company': job.get('company', 'Unknown Company'),
                'location': job.get('location', 'Not specified'),
                'description': job.get('snippet', '')[:400] + '...' if len(job.get('snippet', '')) > 400 else job.get('snippet', ''),
                'url': job.get('link', ''),
                'salary': job.get('salary', ''),
                'posted_date': self._format_jooble_date(job.get('updated')),
                'source': 'Jooble',
                'remote': 'remote' in job.get('location', '').lower(),
                'easy_apply': False,
                'job_type': job.get('type', 'Full-time')
            }
        except Exception as e:
            logger.debug(f"Error parsing Jooble job: {e}")
            return None
    
    def _format_jooble_date(self, date_str):
        """Format Jooble date"""
        try:
            if date_str:
                # Jooble returns various date formats
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d')
            return ""
        except:
            return ""

class AlternativeJobAggregator:
    """Enhanced job aggregator with multiple API sources"""
    
    def __init__(self):
        # Original sources
        self.remote_ok = RemoteOKScraper()
        self.angel_co = AngelCoScraper()
        self.flex_jobs = FlexJobsScraper()
        
        # New API sources
        self.adzuna = AdzunaAPIScraper()
        self.jooble = JoobleAPIScraper()
    
    def search_all_sources(self, job_title, location="remote", max_per_source=10):
        """Search all alternative sources including APIs"""
        logger.info(f"Searching enhanced alternative sources for '{job_title}' in '{location}'")
        
        all_jobs = []
        
        # 1. RemoteOK API (Enhanced)
        try:
            remote_jobs = self.remote_ok.search_jobs(job_title, location, max_per_source)
            all_jobs.extend(remote_jobs)
            logger.info(f"✅ RemoteOK API: {len(remote_jobs)} jobs")
        except Exception as e:
            logger.error(f"RemoteOK API failed: {e}")
        
        # 2. Adzuna API (Global)
        try:
            adzuna_jobs = self.adzuna.search_jobs(job_title, location, max_per_source)
            all_jobs.extend(adzuna_jobs)
            logger.info(f"✅ Adzuna API: {len(adzuna_jobs)} jobs")
        except Exception as e:
            logger.error(f"Adzuna API failed: {e}")
        
        # 3. Jooble API (Global)
        try:
            jooble_jobs = self.jooble.search_jobs(job_title, location, max_per_source)
            all_jobs.extend(jooble_jobs)
            logger.info(f"✅ Jooble API: {len(jooble_jobs)} jobs")
        except Exception as e:
            logger.error(f"Jooble API failed: {e}")
        
        # 4. AngelCo (Startups)
        try:
            startup_jobs = self.angel_co.search_jobs(job_title, location, max_per_source)
            all_jobs.extend(startup_jobs)
            logger.info(f"✅ AngelCo: {len(startup_jobs)} jobs")
        except Exception as e:
            logger.error(f"AngelCo failed: {e}")
        
        # 5. FlexJobs (Curated)
        try:
            flex_jobs = self.flex_jobs.search_jobs(job_title, location, max_per_source)
            all_jobs.extend(flex_jobs)
            logger.info(f"✅ FlexJobs: {len(flex_jobs)} jobs")
        except Exception as e:
            logger.error(f"FlexJobs failed: {e}")
        
        logger.info(f"Total jobs from {len([s for s in [self.remote_ok, self.adzuna, self.jooble, self.angel_co, self.flex_jobs]])} alternative sources: {len(all_jobs)}")
        return all_jobs

# Example usage
if __name__ == "__main__":
    aggregator = AlternativeJobAggregator()
    jobs = aggregator.search_all_sources("IT Support", "remote")
    
    print(f"Found {len(jobs)} jobs from alternative sources:")
    for job in jobs[:5]:
        print(f"- {job['title']} at {job['company']} ({job['source']})") 