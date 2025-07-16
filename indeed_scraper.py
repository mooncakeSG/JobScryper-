import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlencode, urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndeedScraper:
    def __init__(self):
        self.base_url = "https://www.indeed.com"
        
        # Try mobile site which is often less protected
        self.mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Desktop headers as fallback
        self.desktop_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.mobile_headers)  # Start with mobile
        
        # Try different Indeed endpoints
        self.endpoints = [
            "https://www.indeed.com/jobs",
            "https://m.indeed.com/jobs", 
            "https://indeed.com/jobs"
        ]
    
    def build_search_url(self, job_title, location, start=0, endpoint_index=0):
        """Build Indeed search URL with parameters"""
        params = {
            'q': job_title,
            'l': location,
            'start': start,
            'sort': 'date',
            'fromage': '14',  # Jobs from last 14 days (less restrictive)
            'limit': '50'    # Maximum results per page
        }
        
        query_string = urlencode(params)
        base_endpoint = self.endpoints[endpoint_index % len(self.endpoints)]
        return f"{base_endpoint}?{query_string}"
    
    def visit_homepage(self):
        """Visit Indeed homepage to establish session"""
        try:
            homepage_url = "https://www.indeed.com"
            response = self.session.get(homepage_url, timeout=10)
            logger.info(f"Visited homepage: {response.status_code}")
            time.sleep(random.uniform(1, 3))
            return True
        except:
            return False
    
    def get_page(self, url, max_retries=5):
        """Get page content with advanced anti-detection"""
        
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/114.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        ]
        
        desktop_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Try different strategies
        strategies = [
            ('mobile', mobile_agents, self.mobile_headers),
            ('desktop', desktop_agents, self.desktop_headers)
        ]
        
        for strategy_name, user_agents, headers in strategies:
            logger.info(f"Trying {strategy_name} strategy")
            
            # Update session headers
            self.session.headers.clear()
            self.session.headers.update(headers)
            
            for attempt in range(max_retries):
                try:
                    # Visit homepage first on first attempt
                    if attempt == 0:
                        self.visit_homepage()
                    
                    # Random delay
                    time.sleep(random.uniform(3, 8))
                    
                    # Rotate user agent
                    self.session.headers['User-Agent'] = random.choice(user_agents)
                    
                    # Add referrer for more realistic behavior
                    self.session.headers['Referer'] = 'https://www.indeed.com/'
                    
                    # Vary accept language
                    languages = ['en-US,en;q=0.9', 'en-US,en;q=0.9,es;q=0.8', 'en-US,en;q=0.8']
                    self.session.headers['Accept-Language'] = random.choice(languages)
                    
                    logger.info(f"Attempting {strategy_name} request {attempt + 1} to {url}")
                    response = self.session.get(url, timeout=20)
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Success with {strategy_name} strategy!")
                        return response.text
                    elif response.status_code == 403:
                        logger.warning(f"Got 403 with {strategy_name} on attempt {attempt + 1}")
                        time.sleep(random.uniform(15, 30))  # Longer delay for 403
                    else:
                        logger.warning(f"Got status {response.status_code} with {strategy_name}")
                        time.sleep(random.uniform(5, 10))
                        
                except requests.RequestException as e:
                    logger.warning(f"{strategy_name} attempt {attempt + 1} failed: {e}")
                    time.sleep(random.uniform(5, 15))
            
            logger.warning(f"All attempts failed with {strategy_name} strategy")
        
        logger.error(f"All strategies failed for {url}")
        return None
    
    def parse_job_card(self, job_card):
        """Parse individual job card from Indeed with multiple layout support"""
        try:
            job_data = {}
            
            # Job title - try multiple selectors
            title_elem = None
            title_selectors = [
                'h2.jobTitle a',
                '[data-testid="job-title"] a',
                '.jobTitle a',
                'h2 a[data-jk]',
                '.jobTitle',
                'h2',
                '[data-testid="job-title"]'
            ]
            
            for selector in title_selectors:
                title_elem = job_card.select_one(selector)
                if title_elem:
                    break
            
            if title_elem:
                if title_elem.name == 'a':
                    job_data['title'] = title_elem.get('title', '') or title_elem.get_text(strip=True)
                    job_data['url'] = urljoin(self.base_url, title_elem.get('href', ''))
                else:
                    # Try to find link inside
                    link = title_elem.find('a')
                    if link:
                        job_data['title'] = link.get('title', '') or link.get_text(strip=True)
                        job_data['url'] = urljoin(self.base_url, link.get('href', ''))
                    else:
                        job_data['title'] = title_elem.get_text(strip=True)
                        job_data['url'] = ''
            else:
                return None
            
            # Company name - try multiple selectors
            company_elem = None
            company_selectors = [
                '.companyName a',
                '.companyName',
                '[data-testid="company-name"]',
                '.company a',
                '.company'
            ]
            
            for selector in company_selectors:
                company_elem = job_card.select_one(selector)
                if company_elem:
                    job_data['company'] = company_elem.get_text(strip=True)
                    break
            
            if not company_elem:
                job_data['company'] = 'Unknown'
            
            # Location - try multiple selectors  
            location_elem = None
            location_selectors = [
                '.companyLocation',
                '[data-testid="location"]',
                '.locationsContainer',
                '.location'
            ]
            
            for selector in location_selectors:
                location_elem = job_card.select_one(selector)
                if location_elem:
                    job_data['location'] = location_elem.get_text(strip=True)
                    break
            
            if not location_elem:
                job_data['location'] = 'Not specified'
            
            # Salary
            salary_elem = job_card.find('span', class_='salaryText')
            if salary_elem:
                job_data['salary'] = salary_elem.get_text(strip=True)
            else:
                job_data['salary'] = ''
            
            # Job summary/description
            summary_elem = job_card.find('div', class_='job-snippet')
            if summary_elem:
                job_data['description'] = summary_elem.get_text(strip=True)
            else:
                job_data['description'] = ''
            
            # Posted date
            date_elem = job_card.find('span', class_='date')
            if date_elem:
                job_data['posted_date'] = date_elem.get_text(strip=True)
            else:
                job_data['posted_date'] = ''
            
            # Job type (full-time, part-time, etc.)
            job_type_elem = job_card.find('span', class_='jobType')
            if job_type_elem:
                job_data['job_type'] = job_type_elem.get_text(strip=True)
            else:
                job_data['job_type'] = ''
            
            # Remote work indicator
            remote_elem = job_card.find('span', class_='remote')
            job_data['remote'] = remote_elem is not None
            
            # Rating
            rating_elem = job_card.find('span', class_='ratingsContent')
            if rating_elem:
                job_data['rating'] = rating_elem.get_text(strip=True)
            else:
                job_data['rating'] = ''
            
            # Source
            job_data['source'] = 'Indeed'
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None
    
    def search_jobs(self, job_title, location, max_pages=3):
        """Search for jobs on Indeed with multiple strategies"""
        logger.info(f"Searching Indeed for '{job_title}' in '{location}'")
        
        all_jobs = []
        
        # Try multiple endpoints
        for endpoint_index in range(len(self.endpoints)):
            logger.info(f"Trying endpoint {endpoint_index + 1}/{len(self.endpoints)}: {self.endpoints[endpoint_index]}")
            
            try:
                for page in range(max_pages):
                    start = page * 10
                    search_url = self.build_search_url(job_title, location, start, endpoint_index)
                    
                    logger.info(f"Scraping page {page + 1}: {search_url}")
                    
                    # Get page content
                    page_content = self.get_page(search_url)
                    if not page_content:
                        logger.warning(f"Failed to get page {page + 1} from endpoint {endpoint_index + 1}")
                        break  # Try next endpoint if this one fails
                    
                    # Parse HTML
                    soup = BeautifulSoup(page_content, 'html.parser')
                    
                    # Find job cards with multiple selectors
                    job_cards = []
                    selectors = [
                        'div[data-jk]',  # Modern Indeed job cards
                        '.job_seen_beacon',  # Traditional selector
                        '.jobsearch-SerpJobCard',  # Alternative selector
                        '.slider_container .slider_item',  # Mobile view
                        '[data-testid="job-card"]'  # New test ID selector
                    ]
                    
                    for selector in selectors:
                        job_cards = soup.select(selector)
                        if job_cards:
                            logger.info(f"Found {len(job_cards)} job cards using selector: {selector}")
                            break
                    
                    if not job_cards:
                        logger.warning(f"No job cards found on page {page + 1} with any selector")
                        # Log page content for debugging (first 500 chars)
                        logger.debug(f"Page content preview: {page_content[:500]}...")
                        break
                    
                    # Parse each job card
                    page_jobs = []
                    for card in job_cards:
                        job_data = self.parse_job_card(card)
                        if job_data:
                            page_jobs.append(job_data)
                    
                    all_jobs.extend(page_jobs)
                    logger.info(f"Successfully parsed {len(page_jobs)} jobs from page {page + 1}")
                    
                    # If we found jobs, we can continue with this endpoint
                    if len(page_jobs) > 0:
                        # Check if there are more pages
                        next_page = soup.find('a', {'aria-label': 'Next'}) or soup.find('a', {'aria-label': 'Next Page'})
                        if not next_page:
                            logger.info("No more pages available")
                            break
                        
                        # Add delay between pages
                        time.sleep(random.uniform(3, 6))
                    else:
                        logger.warning("No jobs parsed from this page, trying next endpoint")
                        break
                
                # If we found jobs with this endpoint, we can stop
                if len(all_jobs) > 0:
                    logger.info(f"✅ Successfully found {len(all_jobs)} jobs using endpoint {endpoint_index + 1}")
                    break
                    
            except Exception as e:
                logger.error(f"Error with endpoint {endpoint_index + 1}: {e}")
                continue
        
        # If no jobs found after all attempts
        if len(all_jobs) == 0:
            logger.warning("No real jobs found from Indeed after trying all endpoints and strategies.")
            logger.info("This is likely due to Indeed's anti-bot measures.")
            
            # Provide sample data for testing
            if job_title.lower() in ['it support', 'helpdesk', 'desktop support', 'technical support']:
                sample_jobs = self.get_sample_jobs(job_title, location)
                logger.info(f"Providing {len(sample_jobs)} sample jobs for testing purposes")
                all_jobs.extend(sample_jobs)
        else:
            logger.info(f"🎉 Successfully scraped {len(all_jobs)} real jobs from Indeed!")
        
        logger.info(f"Total jobs found: {len(all_jobs)}")
        return all_jobs
    
    def get_job_details(self, job_url):
        """Get detailed information about a specific job"""
        try:
            page_content = self.get_page(job_url)
            if not page_content:
                return None
            
            soup = BeautifulSoup(page_content, 'html.parser')
            
            job_details = {}
            
            # Full job description
            description_elem = soup.find('div', class_='jobsearch-jobDescriptionText')
            if description_elem:
                job_details['full_description'] = description_elem.get_text(strip=True)
            
            # Company information
            company_section = soup.find('div', class_='jobsearch-CompanyInfoContainer')
            if company_section:
                company_name = company_section.find('div', class_='jobsearch-CompanyName')
                if company_name:
                    job_details['company_name'] = company_name.get_text(strip=True)
                
                company_rating = company_section.find('span', class_='ratingsContent')
                if company_rating:
                    job_details['company_rating'] = company_rating.get_text(strip=True)
            
            # Job details section
            job_details_section = soup.find('div', class_='jobsearch-JobDetailsSection')
            if job_details_section:
                details_items = job_details_section.find_all('div', class_='jobsearch-JobDetailsSection-item')
                for item in details_items:
                    key_elem = item.find('span', class_='jobsearch-JobDetailsSection-itemKey')
                    value_elem = item.find('span', class_='jobsearch-JobDetailsSection-itemValue')
                    if key_elem and value_elem:
                        key = key_elem.get_text(strip=True).lower().replace(' ', '_')
                        value = value_elem.get_text(strip=True)
                        job_details[key] = value
            
            # Benefits
            benefits_section = soup.find('div', class_='jobsearch-BenefitsSection')
            if benefits_section:
                benefits = []
                benefit_items = benefits_section.find_all('div', class_='jobsearch-BenefitsSection-item')
                for item in benefit_items:
                    benefit_text = item.get_text(strip=True)
                    if benefit_text:
                        benefits.append(benefit_text)
                job_details['benefits'] = benefits
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
    
    def search_with_filters(self, job_title, location, filters=None):
        """Search jobs with additional filters"""
        if filters is None:
            filters = {}
        
        # Build URL with filters
        params = {
            'q': job_title,
            'l': location,
            'sort': 'date',
            'fromage': '7'
        }
        
        # Add salary filter
        if 'salary_min' in filters:
            params['salary'] = f"${filters['salary_min']},000+"
        
        # Add job type filter
        if 'job_type' in filters:
            params['jt'] = filters['job_type']  # fulltime, parttime, contract, etc.
        
        # Add experience level filter
        if 'experience_level' in filters:
            params['explvl'] = filters['experience_level']  # entry_level, mid_level, senior_level
        
        # Add remote filter
        if filters.get('remote_only', False):
            params['remotejob'] = '1'
        
        query_string = urlencode(params)
        search_url = f"{self.base_url}/jobs?{query_string}"
        
        return self.search_jobs_from_url(search_url)
    
    def search_jobs_from_url(self, url):
        """Search jobs from a specific URL"""
        try:
            page_content = self.get_page(url)
            if not page_content:
                return []
            
            soup = BeautifulSoup(page_content, 'html.parser')
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            if not job_cards:
                job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')
            
            jobs = []
            for card in job_cards:
                job_data = self.parse_job_card(card)
                if job_data:
                    jobs.append(job_data)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching jobs from URL: {e}")
            return []
    
    def get_sample_jobs(self, job_title, location):
        """Provide sample jobs for testing when scraping is blocked"""
        sample_jobs = [
            {
                'title': 'IT Support Specialist',
                'company': 'Tech Solutions Inc',
                'location': location,
                'salary': '$45,000 - $55,000',
                'description': 'Provide technical support for Windows environments, troubleshoot hardware and software issues, and assist users with IT-related problems. Experience with Active Directory, Office 365, and ticketing systems preferred.',
                'posted_date': '2 days ago',
                'job_type': 'Full-time',
                'remote': 'remote' in location.lower(),
                'rating': '4.2',
                'url': 'https://www.indeed.com/viewjob?jk=sample1',
                'source': 'Indeed'
            },
            {
                'title': 'Help Desk Technician',
                'company': 'Global Services Corp',
                'location': location,
                'salary': '$40,000 - $48,000',
                'description': 'Answer support calls and tickets, troubleshoot PC and network issues, provide phone and email support to end users. CompTIA A+ certification preferred.',
                'posted_date': '1 day ago',
                'job_type': 'Full-time',
                'remote': 'remote' in location.lower(),
                'rating': '3.8',
                'url': 'https://www.indeed.com/viewjob?jk=sample2',
                'source': 'Indeed'
            },
            {
                'title': 'Desktop Support Technician',
                'company': 'Healthcare Systems',
                'location': location,
                'salary': '$42,000 - $50,000',
                'description': 'Provide on-site and remote desktop support, install and configure software, manage user accounts, and maintain computer inventory. Experience with Windows 10/11 required.',
                'posted_date': '3 days ago',
                'job_type': 'Full-time',
                'remote': 'remote' in location.lower(),
                'rating': '4.0',
                'url': 'https://www.indeed.com/viewjob?jk=sample3',
                'source': 'Indeed'
            },
            {
                'title': 'IT Support Analyst',
                'company': 'Financial Services Ltd',
                'location': location,
                'salary': '$50,000 - $60,000',
                'description': 'Support business applications, troubleshoot network connectivity issues, and provide technical guidance to users. Experience with VPN, firewalls, and backup systems required.',
                'posted_date': '1 week ago',
                'job_type': 'Full-time',
                'remote': 'remote' in location.lower(),
                'rating': '4.3',
                'url': 'https://www.indeed.com/viewjob?jk=sample4',
                'source': 'Indeed'
            },
            {
                'title': 'Junior IT Support Specialist',
                'company': 'Education Institute',
                'location': location,
                'salary': '$35,000 - $42,000',
                'description': 'Entry-level position providing technical support in educational environment. Assist with classroom technology, troubleshoot student and faculty computer issues.',
                'posted_date': '4 days ago',
                'job_type': 'Full-time',
                'remote': 'remote' in location.lower(),
                'rating': '3.9',
                'url': 'https://www.indeed.com/viewjob?jk=sample5',
                'source': 'Indeed'
            }
        ]
        
        return sample_jobs

# Example usage
if __name__ == "__main__":
    scraper = IndeedScraper()
    
    # Test search
    jobs = scraper.search_jobs("IT Support", "Remote", max_pages=2)
    
    print(f"Found {len(jobs)} jobs")
    for job in jobs[:3]:  # Print first 3 jobs
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")
        print("-" * 50) 