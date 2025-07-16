from playwright.sync_api import sync_playwright
import time
import random
import logging
import os
from pathlib import Path
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

class AutoApply:
    def __init__(self, email, password, resume_path, headless=True):
        self.email = email
        self.password = password
        self.resume_path = resume_path
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
    
    def login(self):
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
            self.page.fill('#username', self.email)
            self.page.fill('#password', self.password)
            
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
    
    def apply_to_job(self, job_url):
        """Apply to a specific job using Easy Apply"""
        try:
            # Login if not already logged in
            if not self.logged_in:
                if not self.login():
                    return False
            
            logger.info(f"Applying to job: {job_url}")
            
            # Navigate to job page
            self.page.goto(job_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Look for Easy Apply button
            easy_apply_button = None
            easy_apply_selectors = [
                '.jobs-apply-button--top-card',
                '.jobs-apply-button',
                'button[aria-label*="Easy Apply"]',
                'button:has-text("Easy Apply")'
            ]
            
            for selector in easy_apply_selectors:
                try:
                    easy_apply_button = self.page.query_selector(selector)
                    if easy_apply_button and easy_apply_button.is_visible():
                        break
                except:
                    continue
            
            if not easy_apply_button:
                logger.warning("Easy Apply button not found")
                return False
            
            # Click Easy Apply button
            easy_apply_button.click()
            
            # Wait for application modal to open
            time.sleep(2)
            
            # Handle the application process
            return self.handle_application_process()
            
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return False
    
    def handle_application_process(self):
        """Handle the multi-step application process"""
        try:
            max_steps = 10  # Prevent infinite loops
            step = 0
            
            while step < max_steps:
                step += 1
                logger.info(f"Application step {step}")
                
                # Wait for modal to load
                time.sleep(2)
                
                # Check if we're done (submit button visible)
                submit_button = self.page.query_selector('button[aria-label="Submit application"]')
                if submit_button and submit_button.is_visible():
                    logger.info("Found submit button, submitting application")
                    submit_button.click()
                    time.sleep(2)
                    
                    # Check for success message
                    success_indicators = [
                        'text="Application submitted"',
                        'text="Your application was sent"',
                        '[data-test-modal-id="application-submitted-modal"]'
                    ]
                    
                    for indicator in success_indicators:
                        if self.page.is_visible(indicator):
                            logger.info("Application submitted successfully")
                            return True
                    
                    # Sometimes there's an additional confirmation step
                    continue
                
                # Handle resume upload
                if self.handle_resume_upload():
                    continue
                
                # Handle text fields
                if self.handle_text_fields():
                    continue
                
                # Handle dropdowns
                if self.handle_dropdowns():
                    continue
                
                # Handle checkboxes
                if self.handle_checkboxes():
                    continue
                
                # Handle radio buttons
                if self.handle_radio_buttons():
                    continue
                
                # Handle additional questions
                if self.handle_additional_questions():
                    continue
                
                # Look for Next button
                next_button = self.page.query_selector('button[aria-label="Continue to next step"]')
                if not next_button:
                    next_button = self.page.query_selector('button:has-text("Next")')
                
                if next_button and next_button.is_visible():
                    logger.info("Clicking Next button")
                    next_button.click()
                    time.sleep(2)
                    continue
                
                # Look for Review button
                review_button = self.page.query_selector('button[aria-label="Review your application"]')
                if not review_button:
                    review_button = self.page.query_selector('button:has-text("Review")')
                
                if review_button and review_button.is_visible():
                    logger.info("Clicking Review button")
                    review_button.click()
                    time.sleep(2)
                    continue
                
                # If we can't find any action to take, break
                logger.warning("No clear next action found")
                break
            
            logger.error("Application process timed out or failed")
            return False
            
        except Exception as e:
            logger.error(f"Error in application process: {e}")
            return False
    
    def handle_resume_upload(self):
        """Handle resume upload if required"""
        try:
            # Look for file upload input
            file_inputs = self.page.query_selector_all('input[type="file"]')
            
            for file_input in file_inputs:
                if file_input.is_visible():
                    logger.info("Found file upload field, uploading resume")
                    
                    # Make sure resume file exists
                    if not os.path.exists(self.resume_path):
                        logger.error(f"Resume file not found: {self.resume_path}")
                        return False
                    
                    # Upload file
                    file_input.set_input_files(self.resume_path)
                    time.sleep(2)
                    
                    # Wait for upload to complete
                    upload_success = self.page.wait_for_selector(
                        'text="Upload successful"',
                        timeout=10000
                    )
                    
                    if upload_success:
                        logger.info("Resume uploaded successfully")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling resume upload: {e}")
            return False
    
    def handle_text_fields(self):
        """Handle text input fields"""
        try:
            # Common text field patterns
            text_fields = self.page.query_selector_all('input[type="text"]')
            text_fields.extend(self.page.query_selector_all('textarea'))
            
            filled_any = False
            
            for field in text_fields:
                if not field.is_visible():
                    continue
                
                # Get field label or placeholder
                label = field.get_attribute('aria-label') or field.get_attribute('placeholder') or ''
                label = label.lower()
                
                # Skip if already filled
                if field.input_value():
                    continue
                
                # Handle common fields
                if any(keyword in label for keyword in ['phone', 'mobile', 'contact']):
                    field.fill('555-123-4567')
                    filled_any = True
                    logger.info(f"Filled phone field: {label}")
                
                elif any(keyword in label for keyword in ['address', 'location']):
                    field.fill('Remote')
                    filled_any = True
                    logger.info(f"Filled address field: {label}")
                
                elif any(keyword in label for keyword in ['website', 'portfolio', 'linkedin']):
                    field.fill('https://linkedin.com/in/profile')
                    filled_any = True
                    logger.info(f"Filled website field: {label}")
                
                elif any(keyword in label for keyword in ['salary', 'expected', 'compensation']):
                    field.fill('Negotiable')
                    filled_any = True
                    logger.info(f"Filled salary field: {label}")
                
                elif any(keyword in label for keyword in ['cover', 'additional', 'why']):
                    field.fill('I am excited about this opportunity and believe my skills align well with your requirements.')
                    filled_any = True
                    logger.info(f"Filled text area: {label}")
            
            return filled_any
            
        except Exception as e:
            logger.error(f"Error handling text fields: {e}")
            return False
    
    def handle_dropdowns(self):
        """Handle dropdown selections"""
        try:
            # Look for select elements
            selects = self.page.query_selector_all('select')
            
            filled_any = False
            
            for select in selects:
                if not select.is_visible():
                    continue
                
                # Get current value
                current_value = select.input_value()
                if current_value:
                    continue
                
                # Get options
                options = select.query_selector_all('option')
                if len(options) <= 1:
                    continue
                
                # Get field label
                label = select.get_attribute('aria-label') or select.get_attribute('name') or ''
                label = label.lower()
                
                # Handle common dropdown types
                if any(keyword in label for keyword in ['experience', 'years']):
                    # Select middle option for experience
                    middle_index = len(options) // 2
                    select.select_option(index=middle_index)
                    filled_any = True
                    logger.info(f"Selected experience option: {label}")
                
                elif any(keyword in label for keyword in ['location', 'country']):
                    # Try to select US or remote option
                    for option in options:
                        option_text = option.text_content().lower()
                        if 'united states' in option_text or 'remote' in option_text:
                            select.select_option(option)
                            filled_any = True
                            logger.info(f"Selected location option: {option_text}")
                            break
                
                elif any(keyword in label for keyword in ['visa', 'authorization']):
                    # Select "Yes" for work authorization
                    for option in options:
                        option_text = option.text_content().lower()
                        if 'yes' in option_text or 'authorized' in option_text:
                            select.select_option(option)
                            filled_any = True
                            logger.info(f"Selected visa option: {option_text}")
                            break
                
                else:
                    # Default to first non-empty option
                    for option in options[1:]:  # Skip first option which is usually empty
                        if option.text_content().strip():
                            select.select_option(option)
                            filled_any = True
                            logger.info(f"Selected default option: {option.text_content()}")
                            break
            
            return filled_any
            
        except Exception as e:
            logger.error(f"Error handling dropdowns: {e}")
            return False
    
    def handle_checkboxes(self):
        """Handle checkbox inputs"""
        try:
            checkboxes = self.page.query_selector_all('input[type="checkbox"]')
            
            filled_any = False
            
            for checkbox in checkboxes:
                if not checkbox.is_visible():
                    continue
                
                # Get checkbox label
                label = checkbox.get_attribute('aria-label') or ''
                label = label.lower()
                
                # Handle common checkboxes
                if any(keyword in label for keyword in ['terms', 'conditions', 'policy']):
                    if not checkbox.is_checked():
                        checkbox.check()
                        filled_any = True
                        logger.info(f"Checked terms checkbox: {label}")
                
                elif any(keyword in label for keyword in ['contact', 'email', 'updates']):
                    if not checkbox.is_checked():
                        checkbox.check()
                        filled_any = True
                        logger.info(f"Checked contact checkbox: {label}")
            
            return filled_any
            
        except Exception as e:
            logger.error(f"Error handling checkboxes: {e}")
            return False
    
    def handle_radio_buttons(self):
        """Handle radio button selections"""
        try:
            radio_groups = {}
            radio_buttons = self.page.query_selector_all('input[type="radio"]')
            
            # Group radio buttons by name
            for radio in radio_buttons:
                if not radio.is_visible():
                    continue
                
                name = radio.get_attribute('name')
                if name not in radio_groups:
                    radio_groups[name] = []
                radio_groups[name].append(radio)
            
            filled_any = False
            
            for name, radios in radio_groups.items():
                # Check if any radio in group is already selected
                if any(radio.is_checked() for radio in radios):
                    continue
                
                # Get group label or use first radio's label
                label = ''
                for radio in radios:
                    radio_label = radio.get_attribute('aria-label') or radio.get_attribute('value') or ''
                    if radio_label:
                        label = radio_label.lower()
                        break
                
                # Handle common radio groups
                if any(keyword in label for keyword in ['visa', 'authorization', 'eligible']):
                    # Select "Yes" for work authorization
                    for radio in radios:
                        radio_label = radio.get_attribute('aria-label') or radio.get_attribute('value') or ''
                        if 'yes' in radio_label.lower():
                            radio.check()
                            filled_any = True
                            logger.info(f"Selected work authorization: Yes")
                            break
                
                elif any(keyword in label for keyword in ['relocate', 'willing']):
                    # Select "Yes" for relocation
                    for radio in radios:
                        radio_label = radio.get_attribute('aria-label') or radio.get_attribute('value') or ''
                        if 'yes' in radio_label.lower():
                            radio.check()
                            filled_any = True
                            logger.info(f"Selected relocation: Yes")
                            break
                
                else:
                    # Default to first option
                    radios[0].check()
                    filled_any = True
                    logger.info(f"Selected default radio option for: {name}")
            
            return filled_any
            
        except Exception as e:
            logger.error(f"Error handling radio buttons: {e}")
            return False
    
    def handle_additional_questions(self):
        """Handle additional questions that might appear"""
        try:
            # Look for any remaining empty required fields
            required_fields = self.page.query_selector_all('[required]')
            
            filled_any = False
            
            for field in required_fields:
                if not field.is_visible():
                    continue
                
                # Skip if already filled
                if field.input_value():
                    continue
                
                field_type = field.get_attribute('type') or field.tag_name.lower()
                
                if field_type == 'text':
                    field.fill('N/A')
                    filled_any = True
                    logger.info("Filled required text field")
                
                elif field_type == 'number':
                    field.fill('1')
                    filled_any = True
                    logger.info("Filled required number field")
                
                elif field_type == 'email':
                    field.fill(self.email)
                    filled_any = True
                    logger.info("Filled required email field")
            
            return filled_any
            
        except Exception as e:
            logger.error(f"Error handling additional questions: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()

# Example usage
if __name__ == "__main__":
    # Test auto apply
    email = "your_email@example.com"
    password = "your_password"
    resume_path = "path/to/your/resume.pdf"
    job_url = "https://www.linkedin.com/jobs/view/123456789"
    
    with AutoApply(email, password, resume_path, headless=False) as auto_apply:
        success = auto_apply.apply_to_job(job_url)
        if success:
            print("Application submitted successfully!")
        else:
            print("Application failed.") 