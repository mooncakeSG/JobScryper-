import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
from datetime import datetime
import time
from pathlib import Path
import requests
import json

# Import our new error handling and utility modules
from utils import (
    get_logger, ErrorContext, handle_errors, validate_job_search,
    APIError, RateLimitError, NetworkError, ValidationError,
    retry_on_failure, get_retry_handler, display_error_to_user,
    ErrorResponse, get_performance_logger, sanitize_input
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will rely on system environment variables

# Import our custom modules
from linkedin_bot import LinkedInBot
from apply import AutoApply
from filters import JobFilter
from alternative_sources import AlternativeJobAggregator
from jobspy_wrapper import JobSpyWrapper

# Import new AI modules
from resume_parser import ResumeParser, get_resume_text_for_matching
from matcher import JobResumeMatcher, match_resume_to_jobs
from ats_report import ATSAnalyzer, generate_ats_report_for_job, save_ats_report, export_ats_report_text
from jobspy_scraper import TechJobScraper, fetch_tech_jobs, fetch_it_support_jobs
from groq_resume_suggestion import generate_resume_suggestions_groq, save_suggestions_to_file

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set Streamlit config
st.set_page_config(
    page_title="JOBscraper",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load icon styles
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.3/font/bootstrap-icons.css">
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        color: #1f77b4;
    }
    .job-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .apply-button {
        background-color: #0073b1;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'applications' not in st.session_state:
    st.session_state.applications = []
if 'jobs_data' not in st.session_state:
    st.session_state.jobs_data = {
        'jobspy': [],
        'linkedin': [], 
        'alternatives': []
    }
if 'current_jobs' not in st.session_state:
    st.session_state.current_jobs = []
if 'resume_path' not in st.session_state:
    st.session_state.resume_path = None
if 'resume_parsed' not in st.session_state:
    st.session_state.resume_parsed = None
if 'matched_jobs' not in st.session_state:
    st.session_state.matched_jobs = []
if 'ats_reports' not in st.session_state:
    st.session_state.ats_reports = {}
if 'groq_suggestions' not in st.session_state:
    st.session_state.groq_suggestions = {}

# Ensure all required keys exist in jobs_data (for backward compatibility)
required_keys = ['jobspy', 'linkedin', 'alternatives']
for key in required_keys:
    if key not in st.session_state.jobs_data:
        st.session_state.jobs_data[key] = []

# Initialize logger for this module
logger = get_logger(__name__)
performance_logger = get_performance_logger()

def save_uploaded_resume(uploaded_file):
    """Save uploaded resume file to assets folder and parse it"""
    if uploaded_file is not None:
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"resume_{timestamp}.{file_extension}"
        
        # Save file
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)
        file_path = assets_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Parse the resume immediately
        try:
            resume_parser = ResumeParser()
            parsed_resume = resume_parser.parse_resume(str(file_path))
            st.session_state.resume_parsed = parsed_resume
            
            if parsed_resume.get('success'):
                st.success(f"Resume parsed successfully! ({parsed_resume.get('cleaned_text_length', 0)} chars)")
            else:
                st.warning("Resume parsing had issues, but file was saved")
                
        except Exception as e:
            st.warning(f"Resume parsing failed: {str(e)}")
            st.session_state.resume_parsed = None
        
        return str(file_path)
    return None

def query_groq(prompt):
    """Query Groq API for AI suggestions"""
    if not GROQ_API_KEY:
        return "Error: GROQ API key not found. Please set GROQ_API_KEY in your environment variables."
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error querying Groq: {str(e)}"

@handle_errors(
    operation_name="Job Search",
    show_user_error=True,
    show_technical_details=True,
    default_return_value=[],
    log_errors=True
)
def search_jobs(job_title, location, job_type, keywords):
    """Search for jobs using multiple scrapers with comprehensive error handling"""
    
    # Start performance tracking
    search_start_time = time.time()
    
    try:
        # Validate input parameters
        search_params = {
            'job_title': job_title,
            'location': location,
            'job_type': job_type,
            'keywords': keywords,
            'max_results': 50  # Default max results
        }
        
        validated_params = validate_job_search(search_params)
        logger.info(f"Starting job search with validated parameters: {validated_params}")
        
        all_jobs = []
        search_results = {}
        
        # JobSpy Search with error context
        with ErrorContext("JobSpy Search", show_spinner=True, show_technical_details=False) as ctx:
            if not ctx.error_occurred:
                retry_handler = get_retry_handler('jobspy')
                
                def _jobspy_search():
                    jobspy_wrapper = JobSpyWrapper()
                    return jobspy_wrapper.search_jobs(
                        job_title=validated_params['job_title'],
                        location=validated_params['location'],
                        sites=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                        max_results=20
                    )
                
                try:
                    jobspy_jobs = retry_handler.retry(
                        _jobspy_search,
                        circuit_breaker_key="jobspy_search"
                    )
                    
                    if jobspy_jobs:
                        st.session_state.jobs_data['jobspy'] = jobspy_jobs
                        all_jobs.extend(jobspy_jobs)
                        search_results['jobspy'] = len(jobspy_jobs)
                        st.success(f"✅ JobSpy: Found {len(jobspy_jobs)} jobs (from LinkedIn and other sources)")
                        logger.info(f"JobSpy search successful: {len(jobspy_jobs)} jobs found")
                    else:
                        st.info("ℹ️ JobSpy: No jobs found - some sites may be blocking requests")
                        search_results['jobspy'] = 0
                        
                except Exception as e:
                    logger.warning(f"JobSpy search failed after retries: {str(e)}")
                    search_results['jobspy'] = 0
                    st.warning("⚠️ JobSpy: Search temporarily unavailable, continuing with other sources...")
        
        # Alternative Sources Search with error context
        with ErrorContext("Alternative Sources Search", show_spinner=True, show_technical_details=False) as ctx:
            if not ctx.error_occurred:
                retry_handler = get_retry_handler('adzuna')  # Use Adzuna config for alternative sources
                
                def _alternative_search():
                    alt_aggregator = AlternativeJobAggregator()
                    return alt_aggregator.search_all_sources(
                        validated_params['job_title'],
                        validated_params['location'],
                        max_per_source=10
                    )
                
                try:
                    alt_jobs = retry_handler.retry(
                        _alternative_search,
                        circuit_breaker_key="alternative_sources"
                    )
                    
                    if alt_jobs:
                        st.session_state.jobs_data['alternatives'] = alt_jobs
                        all_jobs.extend(alt_jobs)
                        search_results['alternatives'] = len(alt_jobs)
                        st.success(f"✅ Alternative Sources: Found {len(alt_jobs)} jobs")
                        logger.info(f"Alternative sources search successful: {len(alt_jobs)} jobs found")
                    else:
                        st.info("ℹ️ Alternative Sources: No matching jobs found")
                        search_results['alternatives'] = 0
                        
                except Exception as e:
                    logger.warning(f"Alternative sources search failed after retries: {str(e)}")
                    search_results['alternatives'] = 0
                    st.warning("⚠️ Alternative Sources: Search temporarily unavailable")
        
        # Store current jobs in session state for persistence
        st.session_state.current_jobs = all_jobs
        
        # Log performance metrics
        search_duration = time.time() - search_start_time
        performance_logger.log_operation(
            operation="job_search",
            duration=search_duration,
            success=len(all_jobs) > 0,
            metadata={
                "search_params": validated_params,
                "results": search_results,
                "total_jobs": len(all_jobs)
            }
        )
        
        # Show summary
        total_jobs = len(all_jobs)
        if total_jobs > 0:
            logger.info(f"Job search completed successfully: {total_jobs} total jobs found in {search_duration:.2f}s")
            st.balloons()  # Celebrate successful search
        else:
            logger.warning("Job search completed but no jobs found")
            st.warning("🔍 No jobs found. Try different search terms or check your spelling.")
            
            # Provide helpful suggestions
            with st.expander("💡 Search Tips", expanded=True):
                st.write("**Try these suggestions:**")
                st.write("• Use broader job titles (e.g., 'Developer' instead of 'Senior React Developer')")
                st.write("• Check spelling of job title and location")
                st.write("• Try different locations (Cape Town, Johannesburg, Remote)")
                st.write("• Use fewer specific keywords")
                st.write("• Search for related job titles")
        
        return all_jobs
        
    except ValidationError as e:
        logger.error(f"Job search validation error: {str(e)}")
        st.error(f"❌ Invalid search parameters: {str(e)}")
        return []
        
    except Exception as e:
        logger.error(f"Unexpected error in job search: {str(e)}", exc_info=True)
        error_response = ErrorResponse(e, {"operation": "job_search", "params": search_params})
        display_error_to_user(error_response, show_technical_details=True)
        return []

def display_job_card(job, source):
    """Display a job card with apply functionality"""
    # Add source indicator
    source_icon = {
        'jobspy': '<i class="fa fa-rocket"></i>',
        'linkedin': '<i class="fa fa-linkedin"></i>', 
        'alternatives': '<i class="fa fa-globe"></i>',
        'remoteok': '<i class="fa fa-laptop"></i>',
        'adzuna': '<i class="fa fa-search"></i>',
        'jooble': '<i class="fa fa-briefcase"></i>'
    }
    
    # Get more accurate source name
    actual_source = job.get('source', source.title())
    source_key = source.lower()
    if actual_source.lower() in ['remoteok', 'adzuna', 'jooble']:
        source_key = actual_source.lower()
    
    title_prefix = f"{source_icon.get(source_key, '<i class=\"fa fa-clipboard\"></i>')} [{actual_source}]"
    
    # Get job details with better validation
    title = job.get('title', 'Position Title Not Available')
    company = job.get('company', 'Company Name Not Available')
    location = job.get('location', 'Location Not Specified')
    date_posted = job.get('date_posted', job.get('posted_date', 'Date Not Available'))
    salary = job.get('salary', '')
    job_type = job.get('job_type', '')
    description = job.get('description', '')
    
    # Validate and clean data
    if title in ['N/A', 'Unknown', 'null', 'None']:
        title = 'Position Title Not Available'
    if company in ['N/A', 'Unknown', 'null', 'None']:
        company = 'Company Name Not Available'
    
    # Create a more informative job card
    st.markdown(f"""
    <div style='border:1px solid #ddd; padding:20px; border-radius:12px; margin-bottom:20px; 
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
        <div style='display: flex; justify-content: between; align-items: start; margin-bottom: 12px;'>
            <h4 style='margin: 0; color: #2c3e50; font-weight: 600;'>
                <i class='fa fa-briefcase' style='color: #3498db; margin-right: 8px;'></i>{title}
            </h4>
            <span style='background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 20px; font-size: 12px; font-weight: 500;'>
                {title_prefix}
            </span>
        </div>
        <div style='margin-bottom: 15px;'>
            <p style='margin: 5px 0; color: #34495e; font-weight: 500;'>
                <i class='fa fa-building' style='color: #e74c3c; margin-right: 8px; width: 16px;'></i><strong>{company}</strong>
            </p>
            <p style='margin: 5px 0; color: #7f8c8d;'>
                <i class='fa fa-map-marker-alt' style='color: #27ae60; margin-right: 8px; width: 16px;'></i>{location}
                <span style='margin-left: 20px;'>
                    <i class='fa fa-clock' style='color: #f39c12; margin-right: 8px;'></i>{date_posted}
                </span>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Add additional job details if available
    details_html = ""
    if salary and salary not in ['', 'N/A', 'Not specified']:
        details_html += f"""
            <p style='margin: 5px 0; color: #27ae60; font-weight: 500;'>
                <i class='fa fa-dollar-sign' style='margin-right: 8px; width: 16px;'></i>{salary}
            </p>
        """
    
    if job_type and job_type not in ['', 'N/A', 'Not specified']:
        details_html += f"""
            <p style='margin: 5px 0; color: #8e44ad;'>
                <i class='fa fa-tags' style='margin-right: 8px; width: 16px;'></i>{job_type}
            </p>
        """
    
    # Show job description preview if available
    if description and len(description.strip()) > 10:
        preview = description[:200] + "..." if len(description) > 200 else description
        details_html += f"""
            <div style='margin-top: 10px; padding: 12px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;'>
                <p style='margin: 0; color: #555; font-size: 14px; line-height: 1.4;'>
                    <i class='fa fa-file-text' style='color: #3498db; margin-right: 8px;'></i>
                    <strong>Description:</strong> {preview}
                </p>
            </div>
        """
    
    # Check for special features
    features = []
    if job.get('easy_apply', False):
        features.append('<span style="background: #4caf50; color: white; padding: 2px 6px; border-radius: 12px; font-size: 11px;">Easy Apply</span>')
    if job.get('remote', False) or 'remote' in location.lower():
        features.append('<span style="background: #2196f3; color: white; padding: 2px 6px; border-radius: 12px; font-size: 11px;">Remote</span>')
    if 'urgent' in title.lower() or 'immediate' in description.lower():
        features.append('<span style="background: #ff9800; color: white; padding: 2px 6px; border-radius: 12px; font-size: 11px;">Urgent</span>')
    
    if features:
        details_html += f"""
            <div style='margin-top: 10px;'>
                {' '.join(features)}
            </div>
        """
    
    if details_html:
        st.markdown(details_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Apply and Analyze buttons with better spacing
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Apply", key=f"apply_{job.get('id', hash(str(job)))}", use_container_width=True):
            apply_to_job(job, source)
    
    with col2:
        if st.button("Analyze", key=f"analyze_{job.get('id', hash(str(job)))}", use_container_width=True):
            analyze_job(job)
    
    with col3:
        # Show data quality indicator
        data_quality = calculate_job_data_quality(job)
        quality_color = "#4caf50" if data_quality >= 80 else "#ff9800" if data_quality >= 60 else "#f44336"
        st.markdown(f"""
        <div style='text-align: right; margin-top: 8px; color: {quality_color}; font-size: 12px;'>
            <i class='fa fa-info-circle'></i> Data Quality: {data_quality}%
        </div>
        """, unsafe_allow_html=True)

def calculate_job_data_quality(job):
    """Calculate data quality score for a job posting"""
    score = 0
    total_fields = 8
    
    # Check essential fields
    if job.get('title') and job['title'] not in ['', 'N/A', 'Unknown', 'null']:
        score += 1
    if job.get('company') and job['company'] not in ['', 'N/A', 'Unknown', 'null']:
        score += 1
    if job.get('location') and job['location'] not in ['', 'N/A', 'Not specified', 'null']:
        score += 1
    if job.get('description') and len(job['description'].strip()) > 20:
        score += 1
    
    # Check additional valuable fields
    if job.get('salary') and job['salary'] not in ['', 'N/A', 'Not specified']:
        score += 1
    if job.get('job_type') and job['job_type'] not in ['', 'N/A', 'Not specified']:
        score += 1
    if job.get('date_posted', job.get('posted_date')) and job.get('date_posted', job.get('posted_date')) not in ['', 'N/A', 'Date Not Available']:
        score += 1
    if job.get('url', job.get('job_url')) and str(job.get('url', job.get('job_url'))).startswith(('http://', 'https://')):
        score += 1
    
    return round((score / total_fields) * 100)

@handle_errors(
    operation_name="Job Application Tracking",
    show_user_error=True,
    show_technical_details=False,
    log_errors=True
)
def apply_to_job(job, source):
    """Apply to a job and track the application with comprehensive error handling"""
    
    apply_start_time = time.time()
    
    try:
        # Import sanitize_input here to avoid circular imports
        from utils.validation import sanitize_input
        
        # Validate job data
        if not job or not isinstance(job, dict):
            raise ValidationError("Invalid job data provided", field="job", value=job)
        
        job_title = sanitize_input(job.get('title', 'Unknown Position'))
        company = sanitize_input(job.get('company', 'Unknown Company'))
        job_url = job.get('job_url', job.get('url', ''))
        
        # Validate required fields
        if job_title == 'Unknown Position':
            raise ValidationError("Job title is required", field="job_title")
        
        if company == 'Unknown Company':
            raise ValidationError("Company name is required", field="company")
        
        # Validate URL
        if not job_url or job_url in ['', 'N/A', 'Unknown']:
            logger.warning(f"No valid job URL found for {job_title} at {company}")
            st.warning(f"⚠️ No valid job URL found for **{job_title}** at **{company}**")
            st.info("💡 This usually means the job posting doesn't have a direct application link. You may need to search for this position on the company's careers page.")
            return
        
        # Validate URL format if provided
        try:
            from utils.validation import InputValidator
            validated_url = InputValidator.validate_url(job_url, "job_url")
            job_url = validated_url
        except ValidationError:
            logger.warning(f"Invalid job URL format: {job_url}")
            st.warning(f"⚠️ Invalid job URL format for **{job_title}** at **{company}**")
            job_url = f"https://www.google.com/search?q={job_title.replace(' ', '+')}+{company.replace(' ', '+')}"
        
        # Check for LinkedIn Easy Apply
        is_easy_apply = job.get('easy_apply', False)
        
        # Create application record with validation
        application = {
            'job_title': job_title,
            'company': company,
            'location': sanitize_input(job.get('location', 'Not specified')),
            'source': sanitize_input(source),
            'applied_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Tracked - Manual Application Required',
            'job_url': job_url,
            'easy_apply': is_easy_apply,
            'salary': sanitize_input(job.get('salary', 'Not specified')),
            'job_type': sanitize_input(job.get('job_type', 'Not specified')),
            'application_method': 'Manual (External URL)' if not is_easy_apply else 'LinkedIn Easy Apply Available'
        }
        
        # Add to session state with error handling
        try:
            if 'applications' not in st.session_state:
                st.session_state.applications = []
            
            st.session_state.applications.append(application)
            logger.info(f"Application tracked: {job_title} at {company}")
            
        except Exception as e:
            logger.error(f"Error adding application to session state: {str(e)}")
            raise ValidationError("Failed to save application to session", field="session_state")
        
        # Save to file with error context
        with ErrorContext("Saving Application Data", show_spinner=False):
            try:
                save_applications_to_csv()
                logger.info("Application saved to CSV successfully")
            except Exception as e:
                logger.warning(f"Failed to save application to CSV: {str(e)}")
                st.warning("⚠️ Application tracked in session but couldn't save to file")
        
        # Success message
        st.success(f"✅ Application tracked for **{job_title}** at **{company}**!")
        
        # Show application summary
        with st.expander("📋 Application Details & Next Steps"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Position Details:**")
                st.write(f"**Title:** {application['job_title']}")
                st.write(f"**Company:** {application['company']}")
                st.write(f"**Location:** {application['location']}")
                st.write(f"**Source:** {application['source']}")
                if application['salary'] != 'Not specified':
                    st.write(f"**Salary:** {application['salary']}")
            
            with col2:
                st.write("**Application Info:**")
                st.write(f"**Tracked:** {application['applied_date']}")
                st.write(f"**Method:** {application['application_method']}")
                st.write(f"**Status:** {application['status']}")
                
                # Show special LinkedIn Easy Apply info
                if is_easy_apply:
                    st.info("🎯 This job supports LinkedIn Easy Apply! You can apply directly on LinkedIn.")
            
            # Action buttons
            st.write("**Next Steps:**")
            
            # Validate URL before showing button
            if job_url.startswith(('http://', 'https://')):
                if st.button(f"🔗 Open Job Application", key=f"open_{hash(job_url)}"):
                    st.markdown(f'<a href="{job_url}" target="_blank">Click here if the job didn\'t open automatically</a>', unsafe_allow_html=True)
                    # Use JavaScript to open in new tab
                    st.markdown(f"""
                    <script>
                        window.open('{job_url}', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
                    
                st.write("1. Click the button above to open the job application")
                st.write("2. Complete the application on the company's website")
                st.write("3. Update the status in the Stats section when done")
            else:
                st.warning("⚠️ Invalid job URL format. Please search for this position manually.")
                st.write(f"**Search for:** {job_title} at {company}")
                
            # LinkedIn specific instructions
            if 'linkedin' in source.lower() and is_easy_apply:
                st.write("**LinkedIn Easy Apply Tips:**")
                st.write("• Make sure your LinkedIn profile is complete")
                st.write("• Have your resume uploaded to LinkedIn")
                st.write("• Check for required questions before submitting")
            
            # General application tips
            st.write("**💡 Application Tips:**")
            st.write("• Tailor your resume to match the job requirements")
            st.write("• Use keywords from the job description")
            st.write("• Write a compelling cover letter if required")
            st.write("• Follow up after 1-2 weeks if you don't hear back")
        
        # Log performance
        apply_duration = time.time() - apply_start_time
        performance_logger.log_operation(
            operation="job_application_tracking",
            duration=apply_duration,
            success=True,
            metadata={
                "job_title": job_title,
                "company": company,
                "source": source,
                "has_url": bool(job_url)
            }
        )
        
    except ValidationError as e:
        logger.error(f"Validation error in job application: {str(e)}")
        st.error(f"❌ {str(e)}")
        st.info("💡 Please check the job data and try again.")
        
    except Exception as e:
        logger.error(f"Unexpected error in job application tracking: {str(e)}", exc_info=True)
        st.error(f"❌ Error tracking application: {str(e)}")
        st.info("💡 You can still apply manually by visiting the company's careers page.")

@handle_errors(
    operation_name="Job Analysis",
    show_user_error=True,
    show_technical_details=True,
    log_errors=True
)
def analyze_job(job):
    """Analyze job compatibility with resume with comprehensive error handling"""
    
    # Validate prerequisites
    if not st.session_state.resume_path:
        st.warning("⚠️ Please upload a resume first in the **Resume Check** section to use job analysis.")
        st.info("💡 The analysis will compare your resume against the job requirements and provide a compatibility score.")
        return
    
    # Validate job data
    if not job or not isinstance(job, dict):
        raise ValidationError("Invalid job data provided for analysis", field="job")
    
    analysis_start_time = time.time()
    
    try:
        # Validate job has required fields
        job_title = sanitize_input(job.get('title', 'N/A'))
        company = sanitize_input(job.get('company', 'N/A'))
        
        if job_title == 'N/A':
            raise ValidationError("Job title is required for analysis", field="job_title")
        
        logger.info(f"Starting job analysis for {job_title} at {company}")
        
        with ErrorContext("Job Compatibility Analysis", show_spinner=True, show_technical_details=False) as ctx:
            if not ctx.error_occurred:
                # Use retry handler for the analysis
                retry_handler = get_retry_handler('groq')
                
                def _generate_analysis():
                    return generate_ats_report_for_job(job, st.session_state.resume_path)
                
                ats_report = retry_handler.retry(
                    _generate_analysis,
                    circuit_breaker_key="job_analysis"
                )
        
        if ats_report and 'error' not in ats_report:
            st.success("✅ Job Analysis Complete!")
            
            # Get the correct score from ats_analysis
            ats_analysis = ats_report.get('ats_analysis', {})
            match_score = ats_analysis.get('ats_score', 0)
            
            # Validate score
            if not isinstance(match_score, (int, float)) or match_score < 0 or match_score > 100:
                logger.warning(f"Invalid match score received: {match_score}")
                match_score = 0
            
            logger.info(f"Job analysis completed with score: {match_score}%")
            
            # Display analysis results in a nice format
            col1, col2 = st.columns(2)
            with col1:
                if match_score >= 70:
                    score_color = "green"
                    score_icon = "🟢"
                elif match_score >= 50:
                    score_color = "orange"
                    score_icon = "🟡"
                else:
                    score_color = "red"
                    score_icon = "🔴"
                
                st.markdown(f"""
                <div style='text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 8px;'>
                    <h3 style='color: {score_color}; margin: 0;'>{score_icon} {match_score}%</h3>
                    <p style='margin: 0;'>Compatibility Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 8px;'>
                    <h4 style='margin: 0;'>📋 {job_title}</h4>
                    <p style='margin: 0;'>{company}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Show detailed analysis
            with st.expander("📊 Detailed Analysis Results", expanded=True):
                # Display ATS score details
                st.markdown(f"**🎯 ATS Score Details:**")
                earned_points = ats_analysis.get('earned_points', 0)
                possible_points = ats_analysis.get('possible_points', 0)
                st.info(f"Earned {earned_points} out of {possible_points} possible points")
                
                # Show matched keywords
                critical_matches = ats_analysis.get('critical_matches', [])
                general_matches = ats_analysis.get('general_matches', [])
                
                if critical_matches or general_matches:
                    st.write("**✅ Matched Keywords:**")
                    all_matches = []
                    for match in critical_matches:
                        if isinstance(match, dict) and 'keyword' in match:
                            all_matches.append(f"{match['keyword']} (critical)")
                    for match in general_matches:
                        if isinstance(match, dict) and 'keyword' in match:
                            all_matches.append(f"{match['keyword']} (general)")
                    if all_matches:
                        st.success(", ".join(all_matches[:10]))  # Show top 10
                
                # Show missing keywords
                missing_keywords = ats_report.get('missing_keywords', [])
                if missing_keywords:
                    st.write("**❌ Missing Important Keywords:**")
                    missing_list = []
                    for kw in missing_keywords[:8]:  # Show top 8
                        if isinstance(kw, dict) and 'keyword' in kw:
                            category_indicator = "🔴" if kw.get('category') == 'critical' else "🟡"
                            missing_list.append(f"{category_indicator} {kw['keyword']}")
                    if missing_list:
                        st.error(", ".join(missing_list))
                
                # Show recommendations
                recommendations = ats_report.get('recommendations', [])
                if recommendations:
                    st.write("**💡 Improvement Recommendations:**")
                    for rec in recommendations:
                        if isinstance(rec, str):
                            st.write(f"• {rec}")
                
                # Show bias analysis if available
                bias_analysis = ats_report.get('bias_analysis', {})
                if bias_analysis:
                    bias_level = bias_analysis.get('bias_level', 'Unknown')
                    if bias_analysis.get('bias_flags'):
                        st.write(f"**⚠️ Job Posting Bias Analysis:** {bias_level}")
                        st.write(f"Found {len(bias_analysis['bias_flags'])} potential bias indicators in the job posting")
                    else:
                        st.write("**✅ Job Posting Analysis:** No bias concerns detected")
            
            # Log performance
            analysis_duration = time.time() - analysis_start_time
            performance_logger.log_operation(
                operation="job_analysis",
                duration=analysis_duration,
                success=True,
                metadata={
                    "job_title": job_title,
                    "company": company,
                    "match_score": match_score,
                    "has_recommendations": bool(recommendations)
                }
            )
                        
        elif ats_report and 'error' in ats_report:
            error_msg = ats_report['error']
            logger.error(f"Job analysis failed with error: {error_msg}")
            st.error(f"❌ Analysis failed: {error_msg}")
        else:
            logger.error("Job analysis failed: No report generated")
            st.error("❌ Failed to generate job analysis. Please try again or check your resume upload.")
            
    except ValidationError as e:
        logger.error(f"Validation error in job analysis: {str(e)}")
        st.error(f"❌ {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error in job analysis: {str(e)}", exc_info=True)
        error_response = ErrorResponse(e, {
            "operation": "job_analysis",
            "job_title": job.get('title', 'Unknown'),
            "resume_path": st.session_state.resume_path
        })
        display_error_to_user(error_response, show_technical_details=True)

def save_applications_to_csv():
    """Save applications to CSV file"""
    try:
        df = pd.DataFrame(st.session_state.applications)
        df.to_csv("applications.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Error saving applications: {e}")
        return False

def load_applications_from_csv():
    """Load applications from CSV file"""
    csv_path = "applications.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            st.session_state.applications = df.to_dict('records')
            return True
        except Exception as e:
            st.error(f"Error loading applications: {e}")
    return False

# Load applications on startup
if not st.session_state.applications:
    load_applications_from_csv()

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Job Search", "Resume Check", "Apply AI", "Stats"],
        icons=["bi-search", "bi-file-earmark-text", "bi-robot", "bi-bar-chart"],
        menu_icon="bi-list",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#1f77b4", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#1f77b4"},
        }
    )

# Main content based on selection
if selected == "Job Search":
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h2><i class="fa fa-search"></i> Job Search</h2>
        <p>Search for tech jobs across multiple platforms</p>
    </div>
    """, unsafe_allow_html=True)

    # Info about the search process
    with st.expander("ℹ️ How Job Search Works"):
        st.markdown("""
        **Our enhanced multi-source job search:**
        - **JobSpy**: Searches LinkedIn, Indeed, ZipRecruiter, and Glassdoor simultaneously
        - **Enhanced Alternative Sources**: 
          - RemoteOK API (no key needed)
          - Adzuna API (1000+ job boards globally) 🆕
          - Jooble API (worldwide job aggregation) 🆕
          - AngelCo (startup jobs)
          - FlexJobs (curated remote jobs)
        
        **🔑 API Setup**: Check `API_SETUP.md` for enhanced search capabilities with free API keys
        
        **Note**: Some job sites actively block scrapers, so expect some sources to be blocked. API sources are more reliable.
        """)
    
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("Job Title", placeholder="e.g. IT Support, Software Developer")
            location = st.text_input("Location", placeholder="e.g. Remote, Cape Town, Johannesburg")
        with col2:
            job_type = st.selectbox("Job Type", ["Any", "Full-time", "Part-time", "Contract", "Internship"])
            keywords = st.text_input("Keywords", placeholder="e.g. Python, Networking, Help Desk")
        
        submitted = st.form_submit_button("Search Jobs", use_container_width=True)

    if submitted and job_title:
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Clear previous results
        st.session_state.jobs_data = {'jobspy': [], 'linkedin': [], 'alternatives': []}
        
        # Search for jobs
        jobs = search_jobs(job_title, location, job_type, keywords)
        
        # Store search results in session state
        st.session_state.current_jobs = jobs
        
    # Display jobs if they exist (either from new search or previous search)
    all_existing_jobs = []
    for source_jobs in st.session_state.jobs_data.values():
        all_existing_jobs.extend(source_jobs)
    
    # Use current_jobs if available, otherwise use jobs from jobs_data
    display_jobs = getattr(st.session_state, 'current_jobs', all_existing_jobs)
    
    if display_jobs:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0; background: #d4edda; border-radius: 8px; margin: 1rem 0;'>
            <h4><i class="fa fa-check-circle" style="color: #155724;"></i> Found {len(display_jobs)} Jobs Total</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Show breakdown by source
        col1, col2 = st.columns(2)
        with col1:
            jobspy_count = len(st.session_state.jobs_data.get('jobspy', []))
            st.metric("JobSpy (Multi-platform)", jobspy_count)
        with col2:
            alt_count = len(st.session_state.jobs_data.get('alternatives', []))
            st.metric("Alternative Sources", alt_count)
        
        # Display jobs
        for i, job in enumerate(display_jobs):
            source = job.get('source', 'unknown')
            display_job_card(job, source)
            
    elif submitted and job_title:
        # Only show "no jobs found" message if a search was just performed
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: #fff3cd; border-radius: 8px; margin: 1rem 0;'>
            <h4><i class="fa fa-exclamation-triangle" style="color: #856404;"></i> No Jobs Found</h4>
            <p>This could be due to:</p>
            <ul style='text-align: left; display: inline-block;'>
                <li>Job sites blocking scrapers (common)</li>
                <li>Very specific search terms</li>
                <li>Network restrictions</li>
            </ul>
            <p><strong>Try:</strong> Different keywords, broader location, or check back later</p>
        </div>
        """, unsafe_allow_html=True)

elif selected == "Resume Check":
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h2><i class="fa fa-file-text"></i> Resume Analyzer</h2>
        <p>Upload your resume for AI-powered analysis and suggestions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Resume upload
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF/DOCX)", 
        type=["pdf", "docx"],
        help="Upload your resume to get AI-powered suggestions and ATS analysis"
    )
    
    if uploaded_file is not None:
        # Save and parse resume
        resume_path = save_uploaded_resume(uploaded_file)
        if resume_path:
            st.session_state.resume_path = resume_path
            
            # Show resume details
            if st.session_state.resume_parsed:
                parsed_data = st.session_state.resume_parsed
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Characters", parsed_data.get('cleaned_text_length', 0))
                with col2:
                    # Get text from the correct location in the parsed data
                    resume_text = ""
                    if 'sections' in parsed_data:
                        resume_text = parsed_data['sections'].get('full_text', '')
                    
                    # Fallback to other possible locations
                    if not resume_text:
                        resume_text = (
                            parsed_data.get('cleaned_text', '') or 
                            parsed_data.get('text', '') or 
                            parsed_data.get('raw_text', '') or
                            parsed_data.get('content', '') or
                            ''
                        )
                    
                    word_count = len(resume_text.split()) if resume_text else 0
                    st.metric("Words", word_count)
                
                # AI Analysis
                st.markdown("### <i class='fa fa-robot'></i> AI Analysis & Suggestions", unsafe_allow_html=True)
                
                if st.button("Generate AI Suggestions", use_container_width=True):
                    with st.spinner("Analyzing resume..."):
                        try:
                            # Get text from the correct location in the parsed data
                            resume_text = ""
                            if 'sections' in parsed_data:
                                resume_text = parsed_data['sections'].get('full_text', '')
                            
                            # Fallback to other possible locations
                            if not resume_text:
                                resume_text = (
                                    parsed_data.get('cleaned_text', '') or 
                                    parsed_data.get('text', '') or 
                                    parsed_data.get('raw_text', '') or
                                    parsed_data.get('content', '') or
                                    ''
                                )
                            
                            if not resume_text:
                                st.error("No text could be extracted from the resume. Please try uploading again.")
                            else:
                                prompt = f"""
                                Analyze the following resume for ATS compliance and provide specific suggestions for improvement for IT Support and tech roles in South Africa. Focus on:
                                1. ATS optimization (keywords, formatting)
                                2. Skills section improvements
                                3. Experience descriptions
                                4. Technical skills alignment
                                5. Local market relevance
                                
                                Resume:
                                {resume_text}
                                
                                Provide actionable suggestions in bullet points.
                                """
                                
                                suggestions = query_groq(prompt)
                                
                                st.markdown("### <i class='fa fa-lightbulb'></i> AI Suggestions", unsafe_allow_html=True)
                                st.write(suggestions)
                                
                                # Save suggestions
                                st.session_state.groq_suggestions[resume_path] = suggestions
                            
                        except Exception as e:
                            st.error(f"Error generating suggestions: {str(e)}")
                
                # Display existing suggestions if available
                if resume_path in st.session_state.groq_suggestions:
                    st.markdown("### <i class='fa fa-lightbulb'></i> Previous AI Suggestions", unsafe_allow_html=True)
                    st.write(st.session_state.groq_suggestions[resume_path])

elif selected == "Apply AI":
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h2><i class="fa fa-robot"></i> AI-Powered Job Matching</h2>
        <p>Get personalized job recommendations based on your skills</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for Apply AI
    if 'ai_recommendations' not in st.session_state:
        st.session_state.ai_recommendations = None
    if 'ai_skills' not in st.session_state:
        st.session_state.ai_skills = ""
    if 'ai_focus_area' not in st.session_state:
        st.session_state.ai_focus_area = "IT Support"
    if 'interview_tips' not in st.session_state:
        st.session_state.interview_tips = None
    
    # Skills input form
    with st.form("ai_form"):
        skills = st.text_area(
            "Describe your skills, experience, and career goals:",
            placeholder="e.g. I have 3 years of IT support experience, skilled in Windows, networking, troubleshooting...",
            value=st.session_state.ai_skills,
            height=150
        )
        
        focus_area = st.selectbox(
            "Focus Area",
            ["IT Support", "Software Development", "Data Analysis", "Cybersecurity", "DevOps", "General Tech"],
            index=["IT Support", "Software Development", "Data Analysis", "Cybersecurity", "DevOps", "General Tech"].index(st.session_state.ai_focus_area)
        )
        
        submitted = st.form_submit_button("Generate Job Matches", use_container_width=True)

    # Handle form submission
    if submitted and skills:
        st.session_state.ai_skills = skills
        st.session_state.ai_focus_area = focus_area
        
        with st.spinner("Generating personalized job recommendations..."):
            try:
                match_prompt = f"""
                Based on the following skills and experience, recommend specific job titles and companies in South Africa's tech market.
                Focus area: {focus_area}
                
                Skills and Experience:
                {skills}
                
                Provide:
                1. 5-7 specific job titles that match this profile
                2. Types of companies to target
                3. Key skills to highlight in applications
                4. Salary expectations (in ZAR)
                5. Career progression tips
                
                Format as clear sections with bullet points.
                """
                
                recommendations = query_groq(match_prompt)
                st.session_state.ai_recommendations = recommendations
                
                # Clear previous interview tips when new recommendations are generated
                st.session_state.interview_tips = None
                
            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")

    # Display recommendations if available
    if st.session_state.ai_recommendations:
        st.markdown("### <i class='fa fa-bullseye'></i> Personalized Job Recommendations", unsafe_allow_html=True)
        st.write(st.session_state.ai_recommendations)
        
        # Interview Tips Button (now always available when recommendations exist)
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Get Interview Preparation Tips", use_container_width=True, type="primary"):
                with st.spinner("Generating personalized interview tips..."):
                    try:
                        interview_prompt = f"""
                        Based on this profile for {st.session_state.ai_focus_area} roles, provide specific interview preparation tips:
                        
                        Skills: {st.session_state.ai_skills}
                        
                        Include:
                        1. Technical questions to expect for {st.session_state.ai_focus_area}
                        2. Projects and experiences to mention
                        3. Skills to demonstrate during the interview
                        4. Common behavioral and situational interview scenarios
                        5. Smart questions to ask the interviewer
                        6. Red flags to watch for during the interview
                        
                        Make it specific to the South African tech market and {st.session_state.ai_focus_area} field.
                        """
                        
                        interview_tips = query_groq(interview_prompt)
                        st.session_state.interview_tips = interview_tips
                        
                    except Exception as e:
                        st.error(f"Error generating interview tips: {str(e)}")

    # Display interview tips if available
    if st.session_state.interview_tips:
        st.markdown("---")
        st.markdown("### <i class='fa fa-handshake'></i> Interview Preparation Tips", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background: #f0f8ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #1976d2; margin: 1rem 0;'>
            <p style='margin: 0; color: #1976d2; font-weight: 500;'>
                <i class='fa fa-lightbulb'></i> Personalized for {st.session_state.ai_focus_area} roles
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(st.session_state.interview_tips)
        
        # Download button for interview tips
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Download Interview Tips", use_container_width=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"interview_tips_{st.session_state.ai_focus_area.lower().replace(' ', '_')}_{timestamp}.txt"
                
                # Create downloadable content
                content = f"""
INTERVIEW PREPARATION TIPS
=========================

Focus Area: {st.session_state.ai_focus_area}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Skills Profile:
{st.session_state.ai_skills}

INTERVIEW TIPS:
{st.session_state.interview_tips}

---
Generated by JOBscraper AI Assistant
                """.strip()
                
                st.download_button(
                    label="📄 Download as TXT file",
                    data=content,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )

    # Reset functionality
    if st.session_state.ai_recommendations or st.session_state.interview_tips:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Start New Analysis", use_container_width=True):
                st.session_state.ai_recommendations = None
                st.session_state.interview_tips = None
                st.session_state.ai_skills = ""
                st.session_state.ai_focus_area = "IT Support"
                st.rerun()

elif selected == "Stats":
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h2><i class="fa fa-chart-bar"></i> Application Statistics</h2>
        <p>Track your job application progress and success metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load applications
    applications = st.session_state.applications
    
    if applications:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(applications)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Applications", len(applications))
        
        with col2:
            applied_count = len(df[df['status'] == 'Applied'])
            st.metric("Applied", applied_count)
        
        with col3:
            # Count interviews (you can expand this based on your status tracking)
            interview_count = len(df[df['status'].str.contains('Interview', case=False, na=False)])
            st.metric("Interviews", interview_count)
        
        with col4:
            # Success rate
            success_rate = (interview_count / len(applications)) * 100 if applications else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Progress bar
        if applied_count > 0:
            progress = min(interview_count / applied_count, 1.0)
            st.progress(progress)
        
        # Recent applications
        st.markdown("### <i class='fa fa-clipboard-list'></i> Recent Applications", unsafe_allow_html=True)
        
        # Display applications table
        if len(df) > 0:
            # Sort by date
            df_sorted = df.sort_values('applied_date', ascending=False)
            
            # Show recent applications
            st.dataframe(
                df_sorted[['job_title', 'company', 'location', 'applied_date', 'status']].head(10),
                use_container_width=True
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'source' in df.columns:
                st.markdown("### <i class='fa fa-chart-bar'></i> Applications by Source", unsafe_allow_html=True)
                source_counts = df['source'].value_counts()
                st.bar_chart(source_counts)
        
        with col2:
            if 'applied_date' in df.columns:
                st.markdown("### <i class='fa fa-calendar'></i> Applications Over Time", unsafe_allow_html=True)
                df['date'] = pd.to_datetime(df['applied_date']).dt.date
                daily_counts = df.groupby('date').size()
                st.line_chart(daily_counts)
        
        # Export functionality
        st.markdown("### <i class='fa fa-download'></i> Export Data", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download applications.csv",
                    data=csv,
                    file_name=f"applications_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Refresh Data"):
                load_applications_from_csv()
                st.success("Data refreshed!")
                st.rerun()
    
    else:
        st.info("No applications yet. Start by searching for jobs in the Job Search section!")
        
        # Sample data for demonstration
        st.markdown("### <i class='fa fa-bullseye'></i> Sample Metrics", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Jobs Found", "0")
        with col2:
            st.metric("Applied", "0")
        with col3:
            st.metric("Interviews", "0")
        with col4:
            st.metric("Success Rate", "0%")
        
        st.progress(0)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>JOBscraper | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True) 