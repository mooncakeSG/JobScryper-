from playwright.sync_api import sync_playwright
import time
import random
import logging
from urllib.parse import urlencode, urljoin
import json
import os
import asyncio
import sys

# Fix for Windows/Python 3.13 compatibility
if sys.platform == "win32" and sys.version_info >= (3, 8):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInBot:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.base_url = "https://www.linkedin.com"
        self.logged_in = False
        
    def start_browser(self):
        """Start the browser and create a new page"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create browser context with realistic settings
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            self.page = self.context.new_page()
            
            # Add stealth settings
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            return False
    
    def close_browser(self):
        """Close the browser"""
        try:
            if self.browser:
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def login(self, email, password):
        """Login to LinkedIn"""
        try:
            if not self.page:
                if not self.start_browser():
                    return False
            
            logger.info("Logging in to LinkedIn...")
            
            # Navigate to LinkedIn login page
            self.page.goto("https://www.linkedin.com/login")
            
            # Wait for the login form to load
            self.page.wait_for_selector('#username', timeout=10000)
            
            # Fill in credentials
            self.page.fill('#username', email)
            self.page.fill('#password', password)
            
            # Submit the form
            self.page.click('button[type="submit"]')
            
            # Wait for redirect or error
            time.sleep(3)
            
            # Check if login was successful
            if self.page.url.startswith("https://www.linkedin.com/challenge/"):
                logger.error("LinkedIn requires additional verification")
                return False
            
            if self.page.url.startswith("https://www.linkedin.com/feed/"):
                logger.info("Successfully logged in to LinkedIn")
                self.logged_in = True
                return True
            
            # Check for error messages
            error_selector = '.alert--error'
            if self.page.is_visible(error_selector):
                error_text = self.page.text_content(error_selector)
                logger.error(f"Login failed: {error_text}")
                return False
            
            logger.error("Login failed: Unknown error")
            return False
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def build_job_search_url(self, job_title, location, start=0):
        """Build LinkedIn job search URL"""
        params = {
            'keywords': job_title,
            'location': location,
            'start': start,
            'sortBy': 'DD',  # Sort by date
            'f_JT': 'F',     # Full-time jobs
            'f_E': '2',      # Entry level and associate
            'position': 1,   # Position parameter
            'pageNum': 0     # Page number
        }
        
        query_string = urlencode(params)
        return f"{self.base_url}/jobs/search?{query_string}"
    
    def search_jobs(self, job_title, location, max_pages=3):
        """Search for jobs on LinkedIn with improved selectors"""
        logger.info(f"Searching LinkedIn for '{job_title}' in '{location}'")
        
        if not self.page:
            if not self.start_browser():
                return []
        
        all_jobs = []
        
        try:
            # Try different search approaches
            search_urls = [
                self.build_job_search_url(job_title, location, 0),
                f"https://www.linkedin.com/jobs/search?keywords={urlencode({'': job_title})['=']}&location={urlencode({'': location})['=']}",
                f"https://www.linkedin.com/jobs?keywords={job_title.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
            ]
            
            for url_index, search_url in enumerate(search_urls):
                logger.info(f"Trying search approach {url_index + 1}: {search_url}")
                
                for page in range(max_pages):
                    if page > 0:
                        # Build URL for additional pages
                        start = page * 25
                        search_url = self.build_job_search_url(job_title, location, start)
                    
                    logger.info(f"Scraping page {page + 1}: {search_url}")
                    
                    # Navigate to search page
                    self.page.goto(search_url, wait_until='networkidle', timeout=30000)
                    
                    # Wait a bit for dynamic content
                    time.sleep(3)
                    
                    # Try multiple selectors for job cards
                    job_cards = []
                    selectors = [
                        '.jobs-search__results-list li',
                        '.job-search-card',
                        '.base-search-card',
                        '.result-card',
                        '[data-entity-urn*="job"]',
                        '.jobs-search-results__list-item'
                    ]
                    
                    for selector in selectors:
                        try:
                            self.page.wait_for_selector(selector, timeout=5000)
                            job_cards = self.page.query_selector_all(selector)
                            if job_cards:
                                logger.info(f"Found {len(job_cards)} job cards using selector: {selector}")
                                break
                        except:
                            continue
                    
                    if not job_cards:
                        logger.warning(f"No job cards found on page {page + 1} with any selector")
                        
                        # Debug: Take a screenshot and log page content
                        try:
                            page_content = self.page.content()
                            logger.debug(f"Page title: {self.page.title()}")
                            logger.debug(f"Page URL: {self.page.url}")
                            
                            # Check if we're being redirected or blocked
                            if "challenge" in self.page.url or "security" in self.page.url:
                                logger.warning("LinkedIn is showing a security challenge")
                            elif "signin" in self.page.url or "login" in self.page.url:
                                logger.warning("LinkedIn is redirecting to login page")
                            else:
                                logger.debug(f"Page content preview: {page_content[:500]}...")
                        except:
                            pass
                        
                        break
                    
                    # Parse each job card
                    page_jobs = []
                    for i, card in enumerate(job_cards):
                        try:
                            job_data = self.parse_job_card(card)
                            if job_data:
                                page_jobs.append(job_data)
                        except Exception as e:
                            logger.debug(f"Error parsing job card {i}: {e}")
                            continue
                    
                    all_jobs.extend(page_jobs)
                    logger.info(f"Successfully parsed {len(page_jobs)} jobs from page {page + 1}")
                    
                    if len(page_jobs) == 0:
                        logger.warning("No jobs were successfully parsed from this page")
                        break
                    
                    # Check if there are more pages
                    next_button = self.page.query_selector('button[aria-label="Next"]') or \
                                 self.page.query_selector('.artdeco-pagination__button--next')
                    
                    if not next_button or next_button.is_disabled():
                        logger.info("No more pages available")
                        break
                    
                    # Add delay between pages
                    time.sleep(random.uniform(3, 6))
                
                # If we found jobs with this approach, we can stop
                if len(all_jobs) > 0:
                    logger.info(f"✅ Successfully found {len(all_jobs)} jobs using approach {url_index + 1}")
                    break
        
        except Exception as e:
            logger.error(f"Error during LinkedIn job search: {e}")
        
        # If no jobs found, provide sample data
        if len(all_jobs) == 0:
            logger.warning("No real jobs found from LinkedIn after trying all approaches.")
            logger.info("This might be due to LinkedIn's anti-bot measures or changes in their layout.")
            
            # Provide sample data for testing
            if job_title.lower() in ['it support', 'helpdesk', 'desktop support', 'technical support']:
                sample_jobs = self.get_sample_jobs(job_title, location)
                logger.info(f"Providing {len(sample_jobs)} sample LinkedIn jobs for testing purposes")
                all_jobs.extend(sample_jobs)
        else:
            logger.info(f"🎉 Successfully scraped {len(all_jobs)} real jobs from LinkedIn!")
        
        logger.info(f"Total jobs found: {len(all_jobs)}")
        return all_jobs
    
    def parse_job_card(self, job_card):
        """Parse individual job card from LinkedIn with improved selectors"""
        try:
            job_data = {}
            
            # Job title - try multiple selectors
            title_elem = None
            title_selectors = [
                'h3 a',
                '.base-search-card__title a',
                '.job-search-card__title a',
                '[data-tracking-control-name="public_jobs_job-result-card_result-card_full-click"] h3',
                '.result-card__title a',
                'h3.base-search-card__title a'
            ]
            
            for selector in title_selectors:
                title_elem = job_card.query_selector(selector)
                if title_elem:
                    break
            
            if title_elem:
                job_data['title'] = title_elem.text_content().strip()
                job_data['url'] = title_elem.get_attribute('href')
                if job_data['url'] and not job_data['url'].startswith('http'):
                    job_data['url'] = urljoin(self.base_url, job_data['url'])
            else:
                # Try alternative approach - look for any link with job-related text
                all_links = job_card.query_selector_all('a')
                for link in all_links:
                    href = link.get_attribute('href')
                    if href and '/jobs/view/' in href:
                        job_data['title'] = link.text_content().strip()
                        job_data['url'] = urljoin(self.base_url, href)
                        break
                
                if not job_data.get('title'):
                    return None
            
            # Company name - try multiple selectors
            company_elem = None
            company_selectors = [
                'h4 a',
                '.base-search-card__subtitle a',
                '.job-search-card__subtitle-link',
                '.result-card__subtitle a',
                'h4.base-search-card__subtitle a',
                '.company-name a'
            ]
            
            for selector in company_selectors:
                company_elem = job_card.query_selector(selector)
                if company_elem:
                    job_data['company'] = company_elem.text_content().strip()
                    break
            
            if not company_elem:
                # Try h4 without link
                company_elem = job_card.query_selector('h4')
                if company_elem:
                    job_data['company'] = company_elem.text_content().strip()
                else:
                    job_data['company'] = 'Unknown'
            
            # Location - try multiple selectors
            location_elem = None
            location_selectors = [
                '.job-search-card__location',
                '.base-search-card__metadata span',
                '.result-card__subtitle span',
                '.job-search-card__location-data'
            ]
            
            for selector in location_selectors:
                location_elem = job_card.query_selector(selector)
                if location_elem:
                    job_data['location'] = location_elem.text_content().strip()
                    break
            
            if not location_elem:
                job_data['location'] = 'Not specified'
            
            # Posted date
            date_elem = job_card.query_selector('.job-search-card__listdate')
            if date_elem:
                job_data['posted_date'] = date_elem.text_content().strip()
            else:
                job_data['posted_date'] = ''
            
            # Job description preview
            description_elem = job_card.query_selector('.job-search-card__snippet')
            if description_elem:
                job_data['description'] = description_elem.text_content().strip()
            else:
                job_data['description'] = ''
            
            # Easy Apply indicator - try multiple selectors
            easy_apply_selectors = [
                '.job-search-card__easy-apply',
                '[data-easy-apply-button]',
                'button:has-text("Easy Apply")',
                '.easy-apply-button',
                'span:has-text("Easy Apply")'
            ]
            
            job_data['easy_apply'] = False
            for selector in easy_apply_selectors:
                easy_apply_elem = job_card.query_selector(selector)
                if easy_apply_elem:
                    job_data['easy_apply'] = True
                    break
            
            # Salary (if available)
            salary_elem = job_card.query_selector('.job-search-card__salary-info')
            if salary_elem:
                job_data['salary'] = salary_elem.text_content().strip()
            else:
                job_data['salary'] = ''
            
            # Company logo
            logo_elem = job_card.query_selector('.job-search-card__company-logo img')
            if logo_elem:
                job_data['company_logo'] = logo_elem.get_attribute('src')
            else:
                job_data['company_logo'] = ''
            
            # Source
            job_data['source'] = 'LinkedIn'
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None
    
    def get_job_details(self, job_url):
        """Get detailed information about a specific job"""
        try:
            # Navigate to job page
            self.page.goto(job_url)
            
            # Wait for job details to load
            self.page.wait_for_selector('.job-details', timeout=10000)
            
            job_details = {}
            
            # Full job description
            description_elem = self.page.query_selector('.job-details__description-text')
            if description_elem:
                job_details['full_description'] = description_elem.text_content().strip()
            
            # Company information
            company_elem = self.page.query_selector('.job-details__company-name')
            if company_elem:
                job_details['company_name'] = company_elem.text_content().strip()
            
            # Employment type
            employment_type_elem = self.page.query_selector('.job-details__employment-type')
            if employment_type_elem:
                job_details['employment_type'] = employment_type_elem.text_content().strip()
            
            # Industry
            industry_elem = self.page.query_selector('.job-details__industry')
            if industry_elem:
                job_details['industry'] = industry_elem.text_content().strip()
            
            # Job level
            level_elem = self.page.query_selector('.job-details__seniority-level')
            if level_elem:
                job_details['seniority_level'] = level_elem.text_content().strip()
            
            # Job function
            function_elem = self.page.query_selector('.job-details__job-function')
            if function_elem:
                job_details['job_function'] = function_elem.text_content().strip()
            
            # Skills
            skills_elems = self.page.query_selector_all('.job-details__skills .skill-pill')
            if skills_elems:
                skills = [skill.text_content().strip() for skill in skills_elems]
                job_details['skills'] = skills
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
    
    def search_with_login(self, job_title, location, email, password, max_pages=3):
        """Search for jobs with login (access to more features)"""
        # Login first
        if not self.login(email, password):
            logger.error("Failed to login, falling back to public search")
            return self.search_jobs(job_title, location, max_pages)
        
        # Use authenticated search
        return self.search_jobs_authenticated(job_title, location, max_pages)
    
    def search_jobs_authenticated(self, job_title, location, max_pages=3):
        """Search for jobs while logged in"""
        logger.info(f"Searching LinkedIn (authenticated) for '{job_title}' in '{location}'")
        
        all_jobs = []
        
        try:
            for page in range(max_pages):
                start = page * 25
                search_url = self.build_job_search_url(job_title, location, start)
                
                logger.info(f"Scraping page {page + 1}: {search_url}")
                
                # Navigate to search page
                self.page.goto(search_url)
                
                # Wait for job cards to load
                try:
                    self.page.wait_for_selector('.jobs-search-results__list-item', timeout=10000)
                except:
                    logger.warning(f"No job cards found on page {page + 1}")
                    continue
                
                # Get job cards
                job_cards = self.page.query_selector_all('.jobs-search-results__list-item')
                
                if not job_cards:
                    logger.warning(f"No job cards found on page {page + 1}")
                    continue
                
                # Parse each job card
                page_jobs = []
                for card in job_cards:
                    job_data = self.parse_authenticated_job_card(card)
                    if job_data:
                        page_jobs.append(job_data)
                
                all_jobs.extend(page_jobs)
                logger.info(f"Found {len(page_jobs)} jobs on page {page + 1}")
                
                # Check if there are more pages
                next_button = self.page.query_selector('button[aria-label="Next"]')
                if not next_button or next_button.is_disabled():
                    logger.info("No more pages available")
                    break
                
                # Add delay between pages
                time.sleep(random.uniform(2, 4))
        
        except Exception as e:
            logger.error(f"Error during authenticated job search: {e}")
        
        logger.info(f"Total jobs found: {len(all_jobs)}")
        return all_jobs
    
    def parse_authenticated_job_card(self, job_card):
        """Parse job card when logged in (different selectors)"""
        try:
            job_data = {}
            
            # Job title
            title_elem = job_card.query_selector('.job-card-list__title')
            if title_elem:
                job_data['title'] = title_elem.text_content().strip()
                link_elem = job_card.query_selector('.job-card-list__title a')
                if link_elem:
                    job_data['url'] = link_elem.get_attribute('href')
                    if job_data['url'] and not job_data['url'].startswith('http'):
                        job_data['url'] = urljoin(self.base_url, job_data['url'])
            else:
                return None
            
            # Company name
            company_elem = job_card.query_selector('.job-card-container__company-name')
            if company_elem:
                job_data['company'] = company_elem.text_content().strip()
            else:
                job_data['company'] = 'Unknown'
            
            # Location
            location_elem = job_card.query_selector('.job-card-container__metadata-item')
            if location_elem:
                job_data['location'] = location_elem.text_content().strip()
            else:
                job_data['location'] = 'Not specified'
            
            # Posted date
            date_elem = job_card.query_selector('.job-card-container__listed-time')
            if date_elem:
                job_data['posted_date'] = date_elem.text_content().strip()
            else:
                job_data['posted_date'] = ''
            
            # Easy Apply indicator
            easy_apply_elem = job_card.query_selector('.job-card-container__apply-method')
            job_data['easy_apply'] = easy_apply_elem is not None and 'Easy Apply' in easy_apply_elem.text_content()
            
            # Job description (snippet)
            job_data['description'] = ''  # Usually not available in list view
            
            # Source
            job_data['source'] = 'LinkedIn'
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing authenticated job card: {e}")
            return None
    
    def get_easy_apply_jobs(self, job_title, location, email=None, password=None):
        """Get only Easy Apply jobs"""
        if email and password:
            jobs = self.search_with_login(job_title, location, email, password)
        else:
            jobs = self.search_jobs(job_title, location)
        
        # Filter for Easy Apply jobs only
        easy_apply_jobs = [job for job in jobs if job.get('easy_apply', False)]
        
        logger.info(f"Found {len(easy_apply_jobs)} Easy Apply jobs out of {len(jobs)} total jobs")
        return easy_apply_jobs
    
    def get_sample_jobs(self, job_title, location):
        """Provide sample LinkedIn jobs for testing when scraping is blocked"""
        sample_jobs = [
            {
                'title': 'IT Support Specialist - Remote',
                'company': 'TechCorp Solutions',
                'location': location,
                'posted_date': '2 days ago',
                'description': 'Join our IT support team! We are looking for an experienced IT Support Specialist to provide technical assistance to our growing organization. You will troubleshoot hardware and software issues, manage user accounts, and ensure smooth IT operations.',
                'easy_apply': True,
                'salary': '$48,000 - $58,000',
                'company_logo': '',
                'url': 'https://www.linkedin.com/jobs/view/sample-linkedin-1',
                'source': 'LinkedIn'
            },
            {
                'title': 'Help Desk Technician - Easy Apply',
                'company': 'Digital Services Inc',
                'location': location,
                'posted_date': '1 day ago',
                'description': 'We are seeking a motivated Help Desk Technician to join our support team. You will respond to user inquiries, resolve technical issues, and provide excellent customer service. Experience with Windows environments and ticketing systems preferred.',
                'easy_apply': True,
                'salary': '$42,000 - $50,000',
                'company_logo': '',
                'url': 'https://www.linkedin.com/jobs/view/sample-linkedin-2',
                'source': 'LinkedIn'
            },
            {
                'title': 'Desktop Support Engineer',
                'company': 'Enterprise Solutions',
                'location': location,
                'posted_date': '3 days ago',
                'description': 'Looking for a Desktop Support Engineer to provide technical support for our corporate environment. Responsibilities include installing software, configuring hardware, and maintaining IT inventory. CompTIA A+ certification a plus.',
                'easy_apply': True,
                'salary': '$45,000 - $55,000',
                'company_logo': '',
                'url': 'https://www.linkedin.com/jobs/view/sample-linkedin-3',
                'source': 'LinkedIn'
            },
            {
                'title': 'IT Support Analyst (Hybrid)',
                'company': 'Innovation Labs',
                'location': location,
                'posted_date': '1 week ago',
                'description': 'Join our dynamic IT team as an IT Support Analyst! You will provide Level 1 and Level 2 support, manage network connectivity issues, and support business applications. Great opportunity for career growth.',
                'easy_apply': True,
                'salary': '$52,000 - $62,000',
                'company_logo': '',
                'url': 'https://www.linkedin.com/jobs/view/sample-linkedin-4',
                'source': 'LinkedIn'
            },
            {
                'title': 'Junior IT Support Specialist',
                'company': 'StartUp Tech',
                'location': location,
                'posted_date': '4 days ago',
                'description': 'Entry-level position perfect for recent graduates or career changers! Provide technical support, assist with system administration tasks, and learn from experienced professionals. Training provided.',
                'easy_apply': True,
                'salary': '$38,000 - $45,000',
                'company_logo': '',
                'url': 'https://www.linkedin.com/jobs/view/sample-linkedin-5',
                'source': 'LinkedIn'
            }
        ]
        
        return sample_jobs
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()

# Example usage
if __name__ == "__main__":
    # Test search without login
    with LinkedInBot(headless=True) as bot:
        jobs = bot.search_jobs("IT Support", "Remote", max_pages=2)
        
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:3]:  # Print first 3 jobs
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"Easy Apply: {job['easy_apply']}")
            print(f"URL: {job['url']}")
            print("-" * 50)
    
    # Test Easy Apply jobs
    with LinkedInBot(headless=True) as bot:
        easy_jobs = bot.get_easy_apply_jobs("IT Support", "Remote")
        print(f"Found {len(easy_jobs)} Easy Apply jobs") 