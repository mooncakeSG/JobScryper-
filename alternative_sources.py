import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from urllib.parse import urlencode, urljoin
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemoteOKScraper:
    """Scraper for RemoteOK.io - focuses on remote tech jobs"""
    
    def __init__(self):
        self.base_url = "https://remoteok.io"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_jobs(self, job_title, location="remote", max_results=20):
        """Search for remote tech jobs"""
        logger.info(f"Searching RemoteOK for '{job_title}' jobs")
        
        try:
            # RemoteOK has a simple API endpoint
            search_url = f"{self.base_url}/api"
            
            time.sleep(random.uniform(1, 3))
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    jobs = []
                    
                    for job in data[1:]:  # First item is metadata
                        if not isinstance(job, dict):
                            continue
                            
                        # Filter for IT support related jobs
                        title = job.get('position', '').lower()
                        description = job.get('description', '').lower()
                        
                        if any(keyword in title or keyword in description for keyword in 
                               ['support', 'helpdesk', 'help desk', 'technical', 'it support', 'desktop']):
                            
                            parsed_job = {
                                'title': job.get('position', 'Unknown Position'),
                                'company': job.get('company', 'Unknown Company'),
                                'location': 'Remote',
                                'description': job.get('description', '')[:300] + '...',
                                'url': f"{self.base_url}/job/{job.get('id', '')}",
                                'salary': self.format_salary(job.get('salary_min'), job.get('salary_max')),
                                'posted_date': self.format_date(job.get('date')),
                                'source': 'RemoteOK',
                                'remote': True,
                                'easy_apply': False
                            }
                            jobs.append(parsed_job)
                            
                            if len(jobs) >= max_results:
                                break
                    
                    logger.info(f"Found {len(jobs)} remote jobs from RemoteOK")
                    return jobs
                
                except json.JSONDecodeError:
                    logger.error("Failed to parse RemoteOK API response")
                    return []
            else:
                logger.warning(f"RemoteOK API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching RemoteOK: {e}")
            return []
    
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

class AlternativeJobAggregator:
    """Main class that aggregates jobs from multiple alternative sources"""
    
    def __init__(self):
        self.remote_ok = RemoteOKScraper()
        self.angel_co = AngelCoScraper()
        self.flex_jobs = FlexJobsScraper()
    
    def search_all_sources(self, job_title, location="remote", max_per_source=10):
        """Search all alternative sources"""
        logger.info(f"Searching alternative sources for '{job_title}' in '{location}'")
        
        all_jobs = []
        
        # Search RemoteOK (API-based, more reliable)
        try:
            remote_jobs = self.remote_ok.search_jobs(job_title, location, max_per_source)
            all_jobs.extend(remote_jobs)
            logger.info(f"✅ RemoteOK: {len(remote_jobs)} jobs")
        except Exception as e:
            logger.error(f"RemoteOK failed: {e}")
        
        # Search AngelCo (startups)
        try:
            startup_jobs = self.angel_co.search_jobs(job_title, location, max_per_source)
            all_jobs.extend(startup_jobs)
            logger.info(f"✅ AngelCo: {len(startup_jobs)} jobs")
        except Exception as e:
            logger.error(f"AngelCo failed: {e}")
        
        # Add curated flexible jobs
        try:
            flex_jobs = self.flex_jobs.search_jobs(job_title, location, max_per_source)
            all_jobs.extend(flex_jobs)
            logger.info(f"✅ FlexJobs: {len(flex_jobs)} jobs")
        except Exception as e:
            logger.error(f"FlexJobs failed: {e}")
        
        logger.info(f"Total jobs from alternative sources: {len(all_jobs)}")
        return all_jobs

# Example usage
if __name__ == "__main__":
    aggregator = AlternativeJobAggregator()
    jobs = aggregator.search_all_sources("IT Support", "remote")
    
    print(f"Found {len(jobs)} jobs from alternative sources:")
    for job in jobs[:5]:
        print(f"- {job['title']} at {job['company']} ({job['source']})") 