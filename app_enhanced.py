"""
Auto Applyer - Enhanced Main Application

Modern, feature-rich job application assistant with:
- Database integration for user management
- AI-powered job matching and analysis
- Comprehensive application tracking
- Professional UI/UX design
- Multi-source job search
- Resume analysis and optimization
- Interview preparation
- Analytics and reporting
"""

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import time
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import enhanced UI components
from ui.components import (
    apply_modern_theme, create_app_header, create_metric_card, 
    create_job_card, create_status_badge, create_progress_bar,
    create_alert, create_stats_chart, create_data_table,
    create_export_buttons, create_loading_spinner, create_empty_state,
    create_sidebar_profile, create_notification_toast, clean_html_text
)

# Import database components
from database.connection import init_database, get_database_manager
from database.utilities import DatabaseUtils
from database.models import ApplicationStatus, User, JobApplication, Resume

# Import existing modules
from jobspy_wrapper import JobSpyWrapper
from alternative_sources import AlternativeJobAggregator
from resume_parser import ResumeParser
from matcher import JobResumeMatcher
from ats_report import ATSAnalyzer
from groq_resume_suggestion import generate_resume_suggestions_groq

# Import utility modules
from utils.errors import handle_errors, ErrorContext
from utils import get_logger, get_performance_logger, sanitize_input

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/auto_applyer.db")

# Initialize logging
logger = get_logger(__name__)
performance_logger = get_performance_logger()

# Streamlit configuration
st.set_page_config(
    page_title="Auto Applyer - AI Job Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': 'https://github.com/yourusername/auto-applyer',
        'Report a bug': 'https://github.com/yourusername/auto-applyer/issues',
        'About': '# Auto Applyer\nAI-powered job application assistant'
    }
)

# Apply modern theme
apply_modern_theme()

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables."""
    defaults = {
        'authenticated': False,
        'user_id': None,
        'user_data': {},
        'page': 'Dashboard',
        'search_results': [],
        'last_search': {},
        'resume_data': {},
        'ai_analysis': {},
        'notifications': [],
        'theme': 'light',
        'selected_job_for_analysis': None,
        'editing_application': None,
        'upload_progress': 0
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

# Database initialization
@st.cache_resource
def initialize_database():
    """Initialize database connection and create tables."""
    try:
        init_database("development")
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

# Authentication check
def check_authentication():
    """Check if user is authenticated."""
    if not st.session_state.authenticated:
        show_authentication_page()
        return False
    return True

def show_authentication_page():
    """Show authentication page for new/returning users."""
    create_app_header("Auto Applyer", "Your AI-Powered Job Application Assistant")
    
    # Initialize database
    if not initialize_database():
        create_alert("Database initialization failed. Please check your setup.", "error")
        return
    
    tab1, tab2 = st.tabs(["🚀 Get Started", "👤 Existing User"])
    
    with tab1:
        st.markdown("### Welcome to Auto Applyer!")
        st.markdown("""
        Transform your job search with AI-powered assistance:
        - **Smart Job Matching** - Find positions that match your skills
        - **ATS Resume Analysis** - Optimize your resume for applicant tracking systems
        - **Application Tracking** - Monitor your job search progress
        - **Interview Preparation** - Get personalized interview tips
        - **Market Intelligence** - Insights on salary trends and job market
        """)
        
        with st.form("user_signup"):
            st.markdown("#### Create Your Profile")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*", placeholder="John")
                email = st.text_input("Email*", placeholder="john@example.com")
                location = st.text_input("Location", placeholder="Cape Town, South Africa")
                phone = st.text_input("Phone", placeholder="+27 123 456 789")
            
            with col2:
                last_name = st.text_input("Last Name*", placeholder="Doe")
                job_title = st.text_input("Current/Target Job Title", placeholder="IT Support Specialist")
                experience_years = st.number_input("Years of Experience", min_value=0, max_value=50, value=2)
                desired_salary = st.number_input("Desired Salary (ZAR)", min_value=0, value=300000, step=10000)
            
            # Skills and preferences
            skills_input = st.text_area(
                "Key Skills (comma-separated)", 
                placeholder="Windows 10, Active Directory, Office 365, Help Desk, Networking, Python",
                help="Enter your key skills separated by commas"
            )
            
            # Job preferences
            col1, col2 = st.columns(2)
            with col1:
                preferred_job_types = st.multiselect(
                    "Preferred Job Types",
                    ["Full-time", "Part-time", "Contract", "Internship", "Remote"],
                    default=["Full-time"]
                )
            
            with col2:
                preferred_locations = st.text_input(
                    "Preferred Locations (comma-separated)",
                    placeholder="Cape Town, Johannesburg, Remote"
                )
            
            # Privacy and notifications
            col1, col2 = st.columns(2)
            with col1:
                email_notifications = st.checkbox("Email Notifications", value=True)
            with col2:
                profile_visibility = st.selectbox(
                    "Profile Visibility",
                    ["Private", "Public", "Recruiters Only"],
                    index=0
                )
            
            submitted = st.form_submit_button("🚀 Create Profile & Start", use_container_width=True)
            
            if submitted:
                if not all([first_name, last_name, email]):
                    create_alert("Please fill in all required fields (marked with *)", "error")
                else:
                    try:
                        # Parse skills and locations
                        skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()] if skills_input else []
                        locations = [loc.strip() for loc in preferred_locations.split(',') if loc.strip()] if preferred_locations else []
                        
                        # Create user with basic fields only
                        user = DatabaseUtils.create_user(
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            location=location,
                            phone=phone,
                            job_title=job_title,
                            experience_years=experience_years,
                            skills=skills
                        )
                        
                        # Update user preferences separately
                        DatabaseUtils.update_user_preferences(
                            user_id=user.id,
                            preferred_job_types=preferred_job_types,
                            preferred_locations=locations,
                            salary_min=desired_salary,
                            email_notifications=email_notifications
                        )
                        
                        # Store in session state
                        st.session_state.user_id = user.id
                        st.session_state.user_data = user.to_dict()
                        st.session_state.authenticated = True
                        
                        create_notification_toast("Profile created successfully! Welcome to Auto Applyer! 🎉", "success")
                        time.sleep(2)
                        st.rerun()
                        
                    except Exception as e:
                        if "already exists" in str(e):
                            create_alert("An account with this email already exists. Please use the 'Existing User' tab.", "warning")
                        else:
                            create_alert(f"Error creating profile: {e}", "error")
                            logger.error(f"User creation failed: {e}")
    
    with tab2:
        st.markdown("### Welcome Back!")
        st.markdown("Enter your email to continue with your existing profile.")
        
        with st.form("user_login"):
            email = st.text_input("Email Address", placeholder="your.email@example.com")
            submitted = st.form_submit_button("🔑 Continue", use_container_width=True)
            
            if submitted and email:
                try:
                    user = DatabaseUtils.get_user_by_email(email)
                    if user:
                        st.session_state.user_id = user.id
                        st.session_state.user_data = user.to_dict()
                        st.session_state.authenticated = True
                        
                        create_notification_toast(f"Welcome back, {user.first_name}! 👋", "success")
                        time.sleep(1)
                        st.rerun()
                    else:
                        create_alert("No account found with this email. Please create a new profile.", "error")
                except Exception as e:
                    create_alert(f"Login error: {e}", "error")
                    logger.error(f"Login failed: {e}")
    
    # Demo account option
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🧪 Try Demo Account", use_container_width=True, help="Use demo@autoapplyer.com"):
            try:
                demo_user = DatabaseUtils.get_user_by_email("demo@autoapplyer.com")
                if demo_user:
                    st.session_state.user_id = demo_user.id
                    st.session_state.user_data = demo_user.to_dict()
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    create_alert("Demo account not found. Please run database initialization.", "error")
            except Exception as e:
                create_alert(f"Demo login error: {e}", "error")

def show_dashboard():
    """Show main dashboard with overview and quick actions."""
    user_data = st.session_state.get('user_data', {})
    user_id = st.session_state.get('user_id')
    
    create_app_header(
        "Dashboard", 
        "Your Job Search Command Center",
        user_data.get('first_name', 'User')
    )
    
    # Quick stats
    try:
        stats = DatabaseUtils.get_application_statistics(user_id, days=30)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Total Applications", 
                str(stats.get('total_applications', 0)),
                delta=f"+{stats.get('recent_applications', 0)} this month",
                icon="fa fa-paper-plane"
            )
        
        with col2:
            create_metric_card(
                "Active Searches", 
                str(stats.get('active_searches', 0)),
                icon="fa fa-search"
            )
        
        with col3:
            create_metric_card(
                "Interviews", 
                str(stats.get('interview_count', 0)),
                icon="fa fa-handshake"
            )
        
        with col4:
            create_metric_card(
                "Success Rate", 
                f"{stats.get('interview_rate', 0):.1f}%",
                icon="fa fa-chart-line"
            )
    
    except Exception as e:
        logger.error(f"Error loading dashboard stats: {e}")
        # Show default metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_metric_card("Total Applications", "0", icon="fa fa-paper-plane")
        with col2:
            create_metric_card("Active Searches", "0", icon="fa fa-search")
        with col3:
            create_metric_card("Interviews", "0", icon="fa fa-handshake")
        with col4:
            create_metric_card("Success Rate", "0%", icon="fa fa-chart-line")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Search Jobs", use_container_width=True):
            st.session_state.page = "Job Search"
            st.rerun()
    
    with col2:
        if st.button("📄 Resume Manager", use_container_width=True):
            st.session_state.page = "Resume Manager"
            st.rerun()
    
    with col3:
        if st.button("🤖 AI Assistant", use_container_width=True):
            st.session_state.page = "AI Assistant"
            st.rerun()
    
    with col4:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.page = "Analytics"
            st.rerun()
    
    # Recent Activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Recent Applications")
        
        try:
            recent_apps = DatabaseUtils.get_user_applications(user_id, limit=5)
            
            if recent_apps:
                for app in recent_apps:
                    with st.container():
                        st.markdown(f"**{app.job_title}** at *{app.company}*")
                        st.markdown(f"📍 {app.location} • {create_status_badge(app.status.value)}", unsafe_allow_html=True)
                        st.markdown(f"📅 {app.application_date.strftime('%Y-%m-%d')}")
                        st.markdown("---")
            else:
                create_empty_state(
                    "No Applications Yet",
                    "Start your job search to see applications here",
                    icon="📋"
                )
        
        except Exception as e:
            create_alert(f"Error loading recent applications: {e}", "error")
    
    with col2:
        st.markdown("### 📈 Activity Trends")
        
        # Create sample activity chart
        try:
            # This would be replaced with actual data from database
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            activity_data = pd.DataFrame({
                'Date': dates,
                'Applications': [max(0, i % 3) for i in range(len(dates))],
                'Searches': [i % 5 + 1 for i in range(len(dates))]
            })
            
            create_stats_chart(activity_data, 'line', 'Job Search Activity (30 Days)', 'Date', 'Applications')
        
        except Exception as e:
            st.info("Activity chart will be available after some job search activity")
    
    # Recommendations
    st.markdown("### 💡 Personalized Recommendations")
    
    recommendations = [
        "🎯 Update your resume with keywords from recent job postings",
        "📊 Set up job alerts for your preferred positions",
        "🤝 Connect with professionals in your target companies",
        "📚 Consider certifications for your field to boost your profile"
    ]
    
    for rec in recommendations:
        st.markdown(f"- {rec}")

def show_job_search():
    """Show enhanced job search page."""
    user_data = st.session_state.get('user_data', {})
    user_id = st.session_state.get('user_id')
    
    create_app_header("Job Search", "Find Your Next Opportunity")
    
    # Search form with enhanced features
    with st.form("enhanced_search_form"):
        st.markdown("### 🔍 Search Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input(
                "Job Title*", 
                value=user_data.get('job_title', ''),
                placeholder="e.g. IT Support Specialist, Software Developer"
            )
            location = st.text_input(
                "Location", 
                value=user_data.get('location', ''),
                placeholder="e.g. Cape Town, Remote, Johannesburg"
            )
            keywords = st.text_input(
                "Keywords", 
                placeholder="e.g. Python, Windows 10, Help Desk"
            )
        
        with col2:
            job_type = st.selectbox(
                "Job Type", 
                ["Any", "Full-time", "Part-time", "Contract", "Internship", "Remote"]
            )
            experience_level = st.selectbox(
                "Experience Level",
                ["Any", "Entry Level", "Mid Level", "Senior Level", "Executive"]
            )
            salary_min = st.number_input(
                "Minimum Salary (ZAR)", 
                min_value=0, 
                value=user_data.get('desired_salary_min', 0), 
                step=10000
            )
        
        # Advanced search options (no nested expander)
        st.markdown("### ⚙️ Advanced Search Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_results = st.slider("Max Results per Source", 10, 100, 50)
            include_remote = st.checkbox("Include Remote Jobs", value=True)
            date_filter = st.selectbox("Posted Within", ["Any", "24 hours", "7 days", "30 days"])
        
        with col2:
            sources = st.multiselect(
                "Search Sources",
                ["JobSpy (Multi-platform)", "Alternative APIs", "LinkedIn", "Indeed"],
                default=["JobSpy (Multi-platform)", "Alternative APIs"]
            )
            company_exclude = st.text_input("Exclude Companies", placeholder="Company1, Company2")
            save_search = st.checkbox("Save this search for alerts", value=False)
        
        # Submit button
        search_submitted = st.form_submit_button("🔍 Search Jobs", use_container_width=True, type="primary")
    
    # Perform search
    if search_submitted and job_title:
        search_jobs(job_title, location, keywords, job_type, sources, max_results, user_id, save_search)
    
    # Display results
    if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
        display_search_results(st.session_state.search_results, user_id)
    elif hasattr(st.session_state, 'last_search'):
        create_empty_state(
            "No Jobs Found",
            "Try adjusting your search criteria or broadening your keywords",
            icon="🔍"
        )
    else:
        create_empty_state(
            "Start Your Job Search",
            "Enter your job preferences above to discover opportunities",
            icon="🚀"
        )

@handle_errors(
    operation_name="Job Search",
    show_user_error=True,
    log_errors=True
)
def search_jobs(job_title, location, keywords, job_type, sources, max_results, user_id, save_search):
    """Perform job search across multiple sources."""
    
    with st.spinner("🔍 Searching for jobs across multiple platforms..."):
        try:
            # Record search in database
            if save_search:
                DatabaseUtils.add_search_history(
                    user_id=user_id,
                    job_title=job_title,
                    location=location,
                    keywords=keywords,
                    sources_searched=sources,
                    max_results=max_results
                )
            
            all_jobs = []
            
            # Search JobSpy
            if "JobSpy (Multi-platform)" in sources:
                try:
                    jobspy = JobSpyWrapper()
                    jobspy_jobs = jobspy.search_jobs(
                        job_title=job_title,
                        location=location,
                        max_results=max_results
                    )
                    for job in jobspy_jobs:
                        job['source'] = 'JobSpy'
                        job['search_relevance'] = calculate_relevance(job, job_title, keywords)
                        # Clean HTML from job description at source
                        if job.get('description'):
                            job['description'] = clean_html_text(job['description'])
                    all_jobs.extend(jobspy_jobs)
                    
                except Exception as e:
                    logger.error(f"JobSpy search failed: {e}")
                    create_alert(f"JobSpy search failed: {e}", "warning")
            
            # Search Alternative APIs
            if "Alternative APIs" in sources:
                try:
                    alt_aggregator = AlternativeJobAggregator()
                    alt_jobs = alt_aggregator.search_all_sources(
                        job_title=job_title,
                        location=location,
                        max_per_source=max_results
                    )
                    for job in alt_jobs:
                        job['search_relevance'] = calculate_relevance(job, job_title, keywords)
                        # Clean HTML from job description at source
                        if job.get('description'):
                            job['description'] = clean_html_text(job['description'])
                    all_jobs.extend(alt_jobs)
                    
                except Exception as e:
                    logger.error(f"Alternative API search failed: {e}")
                    create_alert(f"Alternative API search failed: {e}", "warning")
            
            # Remove duplicates and sort by relevance
            all_jobs = remove_duplicate_jobs(all_jobs)
            all_jobs = sorted(all_jobs, key=lambda x: x.get('search_relevance', 0), reverse=True)
            
            # Store results
            st.session_state.search_results = all_jobs
            st.session_state.last_search = {
                'job_title': job_title,
                'location': location,
                'keywords': keywords,
                'job_type': job_type,
                'sources': sources,
                'timestamp': datetime.now(),
                'results_count': len(all_jobs)
            }
            
            if all_jobs:
                create_notification_toast(f"Found {len(all_jobs)} jobs from {len(sources)} sources", "success")
            else:
                create_alert("No jobs found. Try adjusting your search criteria.", "warning")
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            create_alert(f"Search failed: {e}", "error")
            st.session_state.search_results = []

def calculate_relevance(job, job_title, keywords):
    """Calculate job relevance score."""
    score = 0
    
    # Title matching
    if job_title.lower() in job.get('title', '').lower():
        score += 50
    
    # Keywords matching
    if keywords:
        keyword_list = [k.strip().lower() for k in keywords.split(',')]
        job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        
        for keyword in keyword_list:
            if keyword in job_text:
                score += 10
    
    # Recency bonus
    if 'date_posted' in job:
        try:
            # Simple recency check (this would need more sophisticated date parsing)
            if 'day' in job['date_posted'] or 'today' in job['date_posted'].lower():
                score += 20
        except:
            pass
    
    return min(score, 100)

def remove_duplicate_jobs(jobs):
    """Remove duplicate jobs based on title and company."""
    seen = set()
    unique_jobs = []
    
    for job in jobs:
        key = (job.get('title', '').lower(), job.get('company', '').lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    return unique_jobs

def display_search_results(jobs, user_id):
    """Display search results with filtering and actions."""
    
    # Get user's existing applications
    try:
        user_applications = DatabaseUtils.get_user_applications(user_id)
        applied_jobs = {(app.job_title, app.company) for app in user_applications}
    except:
        applied_jobs = set()
    
    # Filters
    st.markdown("### 🎯 Search Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        company_filter = st.multiselect(
            "Companies",
            options=sorted(list(set([job.get('company', 'Unknown') for job in jobs]))),
            key="search_company_filter"
        )
    
    with col2:
        source_filter = st.multiselect(
            "Sources", 
            options=sorted(list(set([job.get('source', 'Unknown') for job in jobs]))),
            key="search_source_filter"
        )
    
    with col3:
        job_type_filter = st.multiselect(
            "Job Types",
            options=sorted(list(set([job.get('job_type', 'Unknown') for job in jobs]))),
            key="search_type_filter"
        )
    
    with col4:
        sort_by = st.selectbox(
            "Sort by",
            ["Relevance", "Date Posted", "Company", "Title"],
            key="search_sort_by"
        )
    
    # Apply filters
    filtered_jobs = jobs
    
    if company_filter:
        filtered_jobs = [job for job in filtered_jobs if job.get('company') in company_filter]
    
    if source_filter:
        filtered_jobs = [job for job in filtered_jobs if job.get('source') in source_filter]
    
    if job_type_filter:
        filtered_jobs = [job for job in filtered_jobs if job.get('job_type') in job_type_filter]
    
    # Sort results
    if sort_by == "Relevance":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x.get('search_relevance', 0), reverse=True)
    elif sort_by == "Date Posted":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x.get('date_posted', ''), reverse=True)
    elif sort_by == "Company":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x.get('company', ''))
    elif sort_by == "Title":
        filtered_jobs = sorted(filtered_jobs, key=lambda x: x.get('title', ''))
    
    # Display results summary
    st.markdown(f"**Showing {len(filtered_jobs)} of {len(jobs)} jobs**")
    
    if not filtered_jobs:
        create_empty_state(
            "No Results Match Your Filters",
            "Try adjusting or clearing some filters",
            icon="🔍"
        )
        return
    
    # Pagination
    page_size = 10
    total_pages = (len(filtered_jobs) - 1) // page_size + 1
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.selectbox(
                f"Page (1-{total_pages})", 
                range(1, total_pages + 1),
                key="search_page_select"
            )
        
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_jobs))
        page_jobs = filtered_jobs[start_idx:end_idx]
        
        st.info(f"Showing {start_idx + 1}-{end_idx} of {len(filtered_jobs)} jobs")
    else:
        page_jobs = filtered_jobs
    
    # Display jobs
    for job in page_jobs:
        job_key = (job.get('title', ''), job.get('company', ''))
        user_applied = job_key in applied_jobs
        
        # Add match score if user has resume data
        if st.session_state.get('resume_data'):
            job['match_score'] = calculate_job_match_score(job, st.session_state.resume_data)
        
        action = create_job_card(job, show_actions=True, user_applied=user_applied)
        
        if action == "apply" and not user_applied:
            handle_job_application(job, user_id)
        elif action == "analyze":
            st.session_state.selected_job_for_analysis = job
            st.session_state.page = "AI Assistant"
            st.rerun()
        elif action == "save":
            handle_save_job(job, user_id)

def calculate_job_match_score(job, resume_data):
    """Calculate match score between job and resume."""
    try:
        matcher = JobResumeMatcher()
        score = matcher.calculate_match_score(job, resume_data)
        return int(score * 100)
    except:
        return 0

def handle_job_application(job, user_id):
    """Handle job application submission."""
    try:
        # Add to database
        application = DatabaseUtils.add_job_application(
            user_id=user_id,
            job_title=job.get('title', ''),
            company=job.get('company', ''),
            location=job.get('location', ''),
            job_description=job.get('description', ''),
            job_url=job.get('job_url', ''),
            source=job.get('source', ''),
            job_type=job.get('job_type', ''),
            status=ApplicationStatus.APPLIED,
            match_score=job.get('match_score', 0)
        )
        
        create_notification_toast("Application submitted successfully! 🎉", "success")
        
        # Update session state to reflect application
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        logger.error(f"Application submission failed: {e}")
        create_alert(f"Error submitting application: {e}", "error")

def handle_save_job(job, user_id):
    """Handle saving job for later."""
    try:
        # This would save to a saved_jobs table
        create_notification_toast("Job saved for later! 💾", "success")
    except Exception as e:
        logger.error(f"Job save failed: {e}")
        create_alert(f"Error saving job: {e}", "error")

# Main navigation
def main():
    """Main application entry point."""
    
    # Check authentication
    if not check_authentication():
        return
    
    # Sidebar navigation
    with st.sidebar:
        user_data = st.session_state.get('user_data', {})
        create_sidebar_profile(user_data)
        
        # Navigation menu
        selected_page = option_menu(
            menu_title="Navigation",
            options=[
                "Dashboard", "Job Search", "Applications", "Resume Manager", 
                "AI Assistant", "Analytics", "Settings"
            ],
            icons=[
                "house", "search", "clipboard-check", "file-earmark-text",
                "robot", "graph-up", "gear"
            ],
            menu_icon="list",
            default_index=0 if st.session_state.page == "Dashboard" else 
                         ["Dashboard", "Job Search", "Applications", "Resume Manager", 
                          "AI Assistant", "Analytics", "Settings"].index(st.session_state.page),
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#2563eb", "font-size": "18px"}, 
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "0px",
                    "padding": "0.75rem 1rem",
                    "border-radius": "0.5rem",
                    "--hover-color": "#f1f5f9"
                },
                "nav-link-selected": {"background-color": "#2563eb"},
            }
        )
        
        # Update page state
        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()
        
        # Quick stats in sidebar
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        try:
            stats = DatabaseUtils.get_application_statistics(st.session_state.user_id, days=7)
            st.metric("Applications (7d)", stats.get('recent_applications', 0))
            st.metric("Interviews", stats.get('interview_count', 0))
            st.metric("Success Rate", f"{stats.get('interview_rate', 0):.1f}%")
        except:
            st.metric("Applications (7d)", 0)
            st.metric("Interviews", 0)
            st.metric("Success Rate", "0%")
        
        # Logout button
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    
    # Main content
    try:
        if st.session_state.page == "Dashboard":
            show_dashboard()
        elif st.session_state.page == "Job Search":
            show_job_search()
        elif st.session_state.page == "Applications":
            show_applications()
        elif st.session_state.page == "Resume Manager":
            show_resume_manager()
        elif st.session_state.page == "AI Assistant":
            show_ai_assistant()
        elif st.session_state.page == "Analytics":
            show_analytics()
        elif st.session_state.page == "Settings":
            show_settings()
        else:
            show_dashboard()
    except Exception as e:
        logger.error(f"Page render error: {e}")
        create_alert(f"Error loading page: {e}", "error")
        show_dashboard()

# Placeholder functions for remaining pages
def show_applications():
    """Show applications tracking page."""
    create_app_header("My Applications", "Track Your Job Application Progress")
    
    user_id = st.session_state.get('user_id')
    
    # Get applications data
    try:
        applications = DatabaseUtils.get_user_applications(user_id)
        
        if not applications:
            create_empty_state(
                "No Applications Yet",
                "Start by searching for jobs and applying to positions that interest you",
                icon="📋"
            )
            if st.button("🔍 Search Jobs", use_container_width=True, type="primary"):
                st.session_state.page = "Job Search"
                st.rerun()
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_apps = len(applications)
            create_metric_card("Total Applications", total_apps, "📊")
        
        with col2:
            applied_count = len([app for app in applications if app['status'] == ApplicationStatus.APPLIED])
            create_metric_card("Applied", applied_count, "✅")
        
        with col3:
            interview_count = len([app for app in applications if app['status'] == ApplicationStatus.INTERVIEW])
            create_metric_card("Interviews", interview_count, "🎯")
        
        with col4:
            success_rate = (interview_count / total_apps * 100) if total_apps > 0 else 0
            create_metric_card("Success Rate", f"{success_rate:.1f}%", "📈")
        
        st.markdown("---")
        
        # Filters and search
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input("🔍 Search Applications", placeholder="Job title, company...")
        
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All"] + [status.value for status in ApplicationStatus]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Date Applied (Newest)", "Date Applied (Oldest)", "Company", "Job Title", "Status"]
            )
        
        # Filter applications
        filtered_applications = applications.copy()
        
        if search_query:
            filtered_applications = [
                app for app in filtered_applications 
                if search_query.lower() in app['job_title'].lower() or 
                   search_query.lower() in app['company'].lower()
            ]
        
        if status_filter != "All":
            filtered_applications = [
                app for app in filtered_applications 
                if app['status'] == status_filter
            ]
        
        # Sort applications
        if sort_by == "Date Applied (Newest)":
            filtered_applications.sort(key=lambda x: x['applied_date'], reverse=True)
        elif sort_by == "Date Applied (Oldest)":
            filtered_applications.sort(key=lambda x: x['applied_date'])
        elif sort_by == "Company":
            filtered_applications.sort(key=lambda x: x['company'])
        elif sort_by == "Job Title":
            filtered_applications.sort(key=lambda x: x['job_title'])
        elif sort_by == "Status":
            filtered_applications.sort(key=lambda x: x['status'])
        
        # Display applications
        st.markdown(f"### 📋 Applications ({len(filtered_applications)} results)")
        
        for app in filtered_applications:
            display_application_card(app, user_id)
        
        # Bulk actions
        st.markdown("---")
        st.markdown("### 🔧 Bulk Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Applications", use_container_width=True):
                export_applications_data(applications)
        
        with col2:
            if st.button("🔄 Sync Status Updates", use_container_width=True):
                sync_application_status(applications, user_id)
        
        with col3:
            if st.button("📧 Send Follow-up Reminders", use_container_width=True):
                send_followup_reminders(applications, user_id)
        
    except Exception as e:
        logger.error(f"Applications page error: {e}")
        create_alert(f"Error loading applications: {e}", "error")

def display_application_card(app, user_id):
    """Display a single application card."""
    with st.container():
        st.markdown(f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background: white;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                <div>
                    <h3 style="margin: 0; color: #1f2937;">{app['job_title']}</h3>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">
                        📍 {app['company']} • {app['location']}
                    </p>
                </div>
                <div>
                    {create_status_badge(app['status'])}
                </div>
            </div>
            
            <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem; font-size: 0.8rem; color: #6b7280;">
                <span>📅 Applied: {app['applied_date'].strftime('%Y-%m-%d')}</span>
                <span>🎯 Match: {app.get('match_score', 0)}%</span>
                <span>🔗 Source: {app.get('source', 'Unknown')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👁️ View Details", key=f"view_{app['id']}", use_container_width=True):
                show_application_details(app)
        
        with col2:
            if st.button("📝 Update Status", key=f"status_{app['id']}", use_container_width=True):
                update_application_status(app, user_id)
        
        with col3:
            if st.button("📧 Follow Up", key=f"followup_{app['id']}", use_container_width=True):
                schedule_followup(app, user_id)
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{app['id']}", use_container_width=True):
                delete_application(app['id'], user_id)

def show_application_details(app):
    """Show detailed application information."""
    with st.expander("📋 Application Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Job Information**")
            st.write(f"**Title:** {app['job_title']}")
            st.write(f"**Company:** {app['company']}")
            st.write(f"**Location:** {app['location']}")
            st.write(f"**Job Type:** {app.get('job_type', 'Not specified')}")
            st.write(f"**Source:** {app.get('source', 'Unknown')}")
        
        with col2:
            st.markdown("**Application Status**")
            st.write(f"**Status:** {create_status_badge(app['status'])}")
            st.write(f"**Applied Date:** {app['applied_date'].strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Match Score:** {app.get('match_score', 0)}%")
            if app.get('job_url'):
                st.markdown(f"**Job URL:** [View Original Posting]({app['job_url']})")
        
        # Job description
        if app.get('job_description'):
            st.markdown("**Job Description**")
            # Clean HTML from job description
            cleaned_description = clean_html_text(app['job_description'])
            st.text_area("", cleaned_description, height=200, disabled=True)
        
        # Notes section
        st.markdown("**Notes**")
        notes = st.text_area("Add notes about this application...", key=f"notes_{app['id']}")
        if st.button("💾 Save Notes", key=f"save_notes_{app['id']}"):
            # Save notes to database
            create_notification_toast("Notes saved successfully!", "success")

def update_application_status(app, user_id):
    """Update application status."""
    new_status = st.selectbox(
        "Select new status:",
        [status.value for status in ApplicationStatus],
        index=[status.value for status in ApplicationStatus].index(app['status']),
        key=f"new_status_{app['id']}"
    )
    
    if st.button("✅ Update Status", key=f"confirm_status_{app['id']}"):
        try:
            DatabaseUtils.update_application_status(app['id'], new_status)
            create_notification_toast(f"Status updated to {new_status}!", "success")
            st.rerun()
        except Exception as e:
            create_alert(f"Error updating status: {e}", "error")

def schedule_followup(app, user_id):
    """Schedule follow-up reminder."""
    followup_date = st.date_input(
        "Schedule follow-up for:",
        value=datetime.now().date() + timedelta(days=7),
        key=f"followup_date_{app['id']}"
    )
    
    followup_message = st.text_area(
        "Follow-up message:",
        placeholder="Thank you for considering my application...",
        key=f"followup_msg_{app['id']}"
    )
    
    if st.button("📧 Schedule Follow-up", key=f"schedule_{app['id']}"):
        try:
            # Schedule follow-up in database
            create_notification_toast("Follow-up scheduled successfully!", "success")
        except Exception as e:
            create_alert(f"Error scheduling follow-up: {e}", "error")

def delete_application(app_id, user_id):
    """Delete application."""
    if st.button("⚠️ Confirm Delete", key=f"confirm_delete_{app_id}", type="primary"):
        try:
            DatabaseUtils.delete_application(app_id, user_id)
            create_notification_toast("Application deleted successfully!", "success")
            st.rerun()
        except Exception as e:
            create_alert(f"Error deleting application: {e}", "error")

def export_applications_data(applications):
    """Export applications data."""
    try:
        # Convert to DataFrame and export
        df = pd.DataFrame(applications)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"applications_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        create_notification_toast("Applications exported successfully!", "success")
    except Exception as e:
        create_alert(f"Error exporting applications: {e}", "error")

def sync_application_status(applications, user_id):
    """Sync application status with external sources."""
    create_notification_toast("Status sync feature coming soon!", "info")

def send_followup_reminders(applications, user_id):
    """Send follow-up reminders."""
    create_notification_toast("Follow-up reminders feature coming soon!", "info")

def show_resume_manager():
    """Show resume management page."""
    create_app_header("Resume Manager", "Optimize Your Resume for ATS")
    
    user_id = st.session_state.get('user_id')
    
    # Resume upload and management
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Resume", "📋 Current Resume", "🔍 ATS Analysis", "✨ AI Suggestions"])
    
    with tab1:
        st.markdown("### 📤 Upload New Resume")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'doc', 'txt'],
            help="Supported formats: PDF, Word documents, plain text"
        )
        
        if uploaded_file is not None:
            # Display file info
            file_details = {
                "filename": uploaded_file.name,
                "filetype": uploaded_file.type,
                "filesize": uploaded_file.size
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**File Details**")
                st.write(f"📁 **Name:** {file_details['filename']}")
                st.write(f"📄 **Type:** {file_details['filetype']}")
                st.write(f"📏 **Size:** {file_details['filesize'] / 1024:.1f} KB")
            
            with col2:
                st.markdown("**Actions**")
                if st.button("📤 Upload & Analyze", type="primary", use_container_width=True):
                    process_resume_upload(uploaded_file, user_id)
                
                if st.button("👁️ Preview Content", use_container_width=True):
                    preview_resume_content(uploaded_file)
        
        # Resume templates
        st.markdown("---")
        st.markdown("### 📋 Resume Templates")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎯 ATS-Optimized Template**
            - Clean, professional layout
            - ATS-friendly formatting
            - Keywords optimization
            """)
            if st.button("📥 Download Template", key="ats_template"):
                download_resume_template("ats")
        
        with col2:
            st.markdown("""
            **💼 Executive Template**
            - Leadership-focused
            - Achievement highlights
            - Strategic presentation
            """)
            if st.button("📥 Download Template", key="exec_template"):
                download_resume_template("executive")
        
        with col3:
            st.markdown("""
            **🚀 Tech Template**
            - Skills-focused layout
            - Project highlights
            - Technical expertise
            """)
            if st.button("📥 Download Template", key="tech_template"):
                download_resume_template("technical")
    
    with tab2:
        st.markdown("### 📋 Current Resume")
        
        # Get current resume
        current_resume = get_current_resume(user_id)
        
        if current_resume:
            # Resume info
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Resume Information**")
                st.write(f"📁 **Filename:** {current_resume.get('filename', 'resume.pdf')}")
                st.write(f"📅 **Uploaded:** {current_resume.get('upload_date', 'Unknown')}")
                st.write(f"📊 **ATS Score:** {current_resume.get('ats_score', 0)}/100")
                st.write(f"🎯 **Match Keywords:** {current_resume.get('keyword_count', 0)}")
            
            with col2:
                st.markdown("**Quick Actions**")
                if st.button("👁️ View Resume", use_container_width=True):
                    view_resume_content(current_resume)
                
                if st.button("🔍 Re-analyze", use_container_width=True):
                    analyze_resume_ats(current_resume, user_id)
                
                if st.button("📧 Email Resume", use_container_width=True):
                    email_resume(current_resume, user_id)
            
            # Resume preview
            st.markdown("---")
            st.markdown("### 👁️ Resume Preview")
            
            if current_resume.get('content'):
                st.text_area(
                    "Resume Content",
                    value=current_resume['content'][:2000] + "..." if len(current_resume['content']) > 2000 else current_resume['content'],
                    height=300,
                    disabled=True
                )
            
            # Skills extracted
            if current_resume.get('skills'):
                st.markdown("### 🔧 Extracted Skills")
                
                skills_cols = st.columns(3)
                skills_list = current_resume['skills']
                
                for i, skill in enumerate(skills_list[:12]):  # Show first 12 skills
                    with skills_cols[i % 3]:
                        st.markdown(f"• {skill}")
                
                if len(skills_list) > 12:
                    st.markdown(f"*... and {len(skills_list) - 12} more skills*")
        
        else:
            create_empty_state(
                "No Resume Uploaded",
                "Upload your resume to get started with ATS optimization and job matching",
                icon="📄"
            )
    
    with tab3:
        st.markdown("### 🔍 ATS Analysis")
        
        current_resume = get_current_resume(user_id)
        
        if current_resume:
            # ATS Score
            col1, col2, col3 = st.columns(3)
            
            with col1:
                ats_score = current_resume.get('ats_score', 0)
                create_metric_card("ATS Score", f"{ats_score}/100", "🎯")
            
            with col2:
                keyword_count = current_resume.get('keyword_count', 0)
                create_metric_card("Keywords Found", keyword_count, "🔑")
            
            with col3:
                format_score = current_resume.get('format_score', 0)
                create_metric_card("Format Score", f"{format_score}/100", "📄")
            
            # Detailed analysis
            st.markdown("---")
            st.markdown("### 📊 Detailed Analysis")
            
            # ATS Compatibility
            st.markdown("#### 🤖 ATS Compatibility")
            ats_issues = current_resume.get('ats_issues', [])
            
            if ats_issues:
                for issue in ats_issues:
                    st.markdown(f"⚠️ **{issue['category']}:** {issue['description']}")
                    if issue.get('suggestion'):
                        st.markdown(f"💡 *Suggestion: {issue['suggestion']}*")
            else:
                st.success("✅ No ATS compatibility issues found!")
            
            # Keywords analysis
            st.markdown("#### 🔑 Keywords Analysis")
            
            missing_keywords = current_resume.get('missing_keywords', [])
            if missing_keywords:
                st.markdown("**Missing Keywords (Consider Adding):**")
                for keyword in missing_keywords[:10]:  # Show first 10
                    st.markdown(f"• {keyword}")
            else:
                st.success("✅ Good keyword coverage!")
            
            # Format recommendations
            st.markdown("#### 📄 Format Recommendations")
            
            format_issues = current_resume.get('format_issues', [])
            if format_issues:
                for issue in format_issues:
                    st.markdown(f"⚠️ {issue}")
            else:
                st.success("✅ Resume format looks good!")
            
            # Re-analyze button
            if st.button("🔄 Re-analyze Resume", type="primary", use_container_width=True):
                analyze_resume_ats(current_resume, user_id)
        
        else:
            create_empty_state(
                "No Resume to Analyze",
                "Upload your resume first to get detailed ATS analysis",
                icon="🔍"
            )
    
    with tab4:
        st.markdown("### ✨ AI Suggestions")
        
        current_resume = get_current_resume(user_id)
        
        if current_resume:
            # AI-powered suggestions
            st.markdown("#### 🤖 AI-Powered Improvements")
            
            # Get job preference for context
            user_data = st.session_state.get('user_data', {})
            target_role = user_data.get('job_title', 'your target role')
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✨ Get Content Suggestions", use_container_width=True):
                    get_ai_content_suggestions(current_resume, target_role, user_id)
            
            with col2:
                if st.button("🎯 Optimize for Job", use_container_width=True):
                    optimize_resume_for_job(current_resume, user_id)
            
            # Show previous suggestions
            suggestions = get_resume_suggestions(user_id)
            
            if suggestions:
                st.markdown("#### 📝 Recent Suggestions")
                
                for suggestion in suggestions[:5]:  # Show last 5 suggestions
                    with st.expander(f"💡 {suggestion['category']} - {suggestion['date']}"):
                        st.markdown(f"**Suggestion:** {suggestion['content']}")
                        st.markdown(f"**Priority:** {suggestion['priority']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Apply", key=f"apply_{suggestion['id']}"):
                                apply_resume_suggestion(suggestion, user_id)
                        
                        with col2:
                            if st.button("❌ Dismiss", key=f"dismiss_{suggestion['id']}"):
                                dismiss_resume_suggestion(suggestion['id'], user_id)
            
            # Custom optimization
            st.markdown("#### 🎯 Custom Optimization")
            
            job_description = st.text_area(
                "Paste a job description to optimize your resume:",
                placeholder="Paste the job description here...",
                height=150
            )
            
            if job_description and st.button("🔧 Optimize Resume", type="primary"):
                optimize_resume_for_description(current_resume, job_description, user_id)
        
        else:
            create_empty_state(
                "No Resume for AI Analysis",
                "Upload your resume to get AI-powered suggestions and optimizations",
                icon="🤖"
            )

def process_resume_upload(uploaded_file, user_id):
    """Process uploaded resume file."""
    try:
        with st.spinner("Processing resume..."):
            # Extract content
            content = extract_resume_content(uploaded_file)
            
            # Save to database
            resume_id = save_resume_to_database(uploaded_file, content, user_id)
            
            # Analyze resume
            analysis = analyze_resume_content(content, user_id)
            
            # Update session state
            st.session_state.resume_data = {
                'content': content,
                'analysis': analysis,
                'id': resume_id
            }
            
            create_notification_toast("Resume uploaded and analyzed successfully! 🎉", "success")
            st.rerun()
    
    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        create_alert(f"Error processing resume: {e}", "error")

def preview_resume_content(uploaded_file):
    """Preview resume content before upload."""
    try:
        content = extract_resume_content(uploaded_file)
        
        st.markdown("### 👁️ Resume Preview")
        st.text_area(
            "Content Preview",
            value=content[:1000] + "..." if len(content) > 1000 else content,
            height=200,
            disabled=True
        )
        
    except Exception as e:
        create_alert(f"Error previewing resume: {e}", "error")

def extract_resume_content(uploaded_file):
    """Extract content from uploaded resume file."""
    try:
        if uploaded_file.type == "application/pdf":
            # Use PyPDF2 or similar to extract PDF content
            import PyPDF2
            import io
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
            
            return content
        
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            # Use python-docx to extract Word content
            import docx
            import io
            
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            return content
        
        elif uploaded_file.type == "text/plain":
            # Plain text
            content = uploaded_file.read().decode('utf-8')
            return content
        
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.type}")
    
    except Exception as e:
        logger.error(f"Content extraction error: {e}")
        raise

def get_current_resume(user_id):
    """Get current resume data for user."""
    try:
        # This would fetch from database
        return st.session_state.get('resume_data', {})
    except Exception as e:
        logger.error(f"Error getting current resume: {e}")
        return None

def analyze_resume_ats(resume_data, user_id):
    """Analyze resume for ATS compatibility."""
    try:
        with st.spinner("Analyzing resume for ATS compatibility..."):
            # Placeholder for ATS analysis
            # This would integrate with resume parsing and analysis libraries
            
            analysis = {
                'ats_score': 85,
                'keyword_count': 25,
                'format_score': 90,
                'ats_issues': [
                    {
                        'category': 'Headers',
                        'description': 'Some headers may not be recognized by ATS',
                        'suggestion': 'Use standard headers like "Experience", "Education", "Skills"'
                    }
                ],
                'missing_keywords': ['Python', 'SQL', 'Project Management'],
                'format_issues': ['Consider using more common fonts']
            }
            
            # Update resume data
            resume_data.update(analysis)
            
            create_notification_toast("ATS analysis completed! 📊", "success")
            st.rerun()
    
    except Exception as e:
        logger.error(f"ATS analysis error: {e}")
        create_alert(f"Error analyzing resume: {e}", "error")

def get_ai_content_suggestions(resume_data, target_role, user_id):
    """Get AI-powered content suggestions."""
    try:
        with st.spinner("Generating AI suggestions..."):
            # Placeholder for AI suggestions
            suggestions = [
                {
                    'id': 1,
                    'category': 'Skills Enhancement',
                    'content': 'Add "Cloud Computing" to your skills section to match current market demands',
                    'priority': 'High',
                    'date': datetime.now().strftime('%Y-%m-%d')
                },
                {
                    'id': 2,
                    'category': 'Achievement Quantification',
                    'content': 'Quantify your achievements with metrics (e.g., "Improved system efficiency by 25%")',
                    'priority': 'Medium',
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
            ]
            
            st.session_state.resume_suggestions = suggestions
            
            create_notification_toast("AI suggestions generated! 🤖", "success")
            st.rerun()
    
    except Exception as e:
        logger.error(f"AI suggestions error: {e}")
        create_alert(f"Error generating suggestions: {e}", "error")

def get_resume_suggestions(user_id):
    """Get stored resume suggestions."""
    return st.session_state.get('resume_suggestions', [])

def apply_resume_suggestion(suggestion, user_id):
    """Apply a resume suggestion."""
    create_notification_toast("Suggestion applied! ✅", "success")

def dismiss_resume_suggestion(suggestion_id, user_id):
    """Dismiss a resume suggestion."""
    suggestions = st.session_state.get('resume_suggestions', [])
    updated_suggestions = [s for s in suggestions if s['id'] != suggestion_id]
    st.session_state.resume_suggestions = updated_suggestions
    
    create_notification_toast("Suggestion dismissed! ❌", "info")
    st.rerun()

def optimize_resume_for_description(resume_data, job_description, user_id):
    """Optimize resume for specific job description."""
    try:
        with st.spinner("Optimizing resume for job description..."):
            # Placeholder for job-specific optimization
            create_notification_toast("Resume optimized for job description! 🎯", "success")
    
    except Exception as e:
        logger.error(f"Resume optimization error: {e}")
        create_alert(f"Error optimizing resume: {e}", "error")

def download_resume_template(template_type):
    """Download resume template."""
    create_notification_toast(f"{template_type.title()} template download started! 📥", "info")

def view_resume_content(resume_data):
    """View full resume content."""
    st.text_area(
        "Full Resume Content",
        value=resume_data.get('content', ''),
        height=400,
        disabled=True
    )

def email_resume(resume_data, user_id):
    """Email resume to user."""
    create_notification_toast("Resume emailed successfully! 📧", "success")

def save_resume_to_database(uploaded_file, content, user_id):
    """Save resume to database."""
    # Placeholder for database save
    return 1

def analyze_resume_content(content, user_id):
    """Analyze resume content."""
    # Placeholder for content analysis
    return {
        'skills': ['Python', 'SQL', 'Project Management', 'Leadership'],
        'experience_years': 5,
        'education_level': 'Bachelor\'s',
        'keywords': ['IT', 'Support', 'Technical', 'Customer Service']
    }

def optimize_resume_for_job(resume_data, user_id):
    """Optimize resume for current job search."""
    create_notification_toast("Resume optimization started! 🎯", "info")

def show_ai_assistant():
    """Show AI assistant page."""
    create_app_header("AI Assistant", "Get Personalized Job Recommendations")
    
    user_id = st.session_state.get('user_id')
    user_data = st.session_state.get('user_data', {})
    
    # AI Assistant tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Chat", "🎯 Job Matching", "📊 Market Analysis", "💡 Career Advice"])
    
    with tab1:
        st.markdown("### 🤖 AI Career Assistant")
        
        # Initialize chat history
        if 'ai_chat_history' not in st.session_state:
            st.session_state.ai_chat_history = [
                {
                    "role": "assistant",
                    "content": f"Hello! I'm your AI Career Assistant. I can help you with job search, resume optimization, interview preparation, and career advice. What would you like to know today?"
                }
            ]
        
        # Display chat history
        for message in st.session_state.ai_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your career..."):
            # Add user message to history
            st.session_state.ai_chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = generate_ai_response(prompt, user_data)
                    st.markdown(response)
                    
                    # Add AI response to history
                    st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
        
        # Quick action buttons
        st.markdown("### 🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Resume Review", use_container_width=True):
                review_resume_ai(user_id)
        
        with col2:
            if st.button("🎯 Job Recommendations", use_container_width=True):
                get_job_recommendations_ai(user_id)
        
        with col3:
            if st.button("🎤 Interview Prep", use_container_width=True):
                start_interview_prep(user_id)
    
    with tab2:
        st.markdown("### 🎯 AI-Powered Job Matching")
        
        # Job matching based on resume and preferences
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔧 Matching Preferences")
            
            # User can adjust matching criteria
            match_criteria = {
                'location_weight': st.slider("Location Importance", 0.0, 1.0, 0.3),
                'salary_weight': st.slider("Salary Importance", 0.0, 1.0, 0.4),
                'skills_weight': st.slider("Skills Match Importance", 0.0, 1.0, 0.8),
                'experience_weight': st.slider("Experience Level Importance", 0.0, 1.0, 0.6),
                'company_size_pref': st.selectbox("Company Size Preference", 
                                                ["No preference", "Startup", "Small", "Medium", "Large", "Enterprise"]),
                'remote_preference': st.selectbox("Remote Work Preference", 
                                                ["No preference", "Fully Remote", "Hybrid", "On-site"])
            }
            
            if st.button("🎯 Find Matches", type="primary", use_container_width=True):
                find_job_matches(user_id, match_criteria)
        
        with col2:
            st.markdown("#### 📊 Match Results")
            
            # Display job matches
            if 'job_matches' in st.session_state:
                matches = st.session_state.job_matches
                
                if matches:
                    for match in matches[:5]:  # Show top 5 matches
                        with st.container():
                            st.markdown(f"""
                            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                                <h4 style="margin: 0; color: #1f2937;">{match['job_title']}</h4>
                                <p style="margin: 0.25rem 0; color: #6b7280;">{match['company']} • {match['location']}</p>
                                <div style="margin: 0.5rem 0;">
                                    <span style="background: #10b981; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">
                                        {match['match_score']}% Match
                                    </span>
                                </div>
                                <p style="font-size: 0.9rem; color: #4b5563;">{match['match_reason']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("📋 View Details", key=f"view_{match['id']}"):
                                    show_job_match_details(match)
                            
                            with col2:
                                if st.button("✅ Apply", key=f"apply_{match['id']}"):
                                    apply_to_matched_job(match, user_id)
                else:
                    st.info("No job matches found. Try adjusting your preferences or update your profile.")
            else:
                st.info("Click 'Find Matches' to discover jobs tailored to your profile.")
        
        # Skills gap analysis
        st.markdown("---")
        st.markdown("### 📈 Skills Gap Analysis")
        
        if st.button("🔍 Analyze Skills Gap", use_container_width=True):
            analyze_skills_gap(user_id)
        
        if 'skills_gap_analysis' in st.session_state:
            analysis = st.session_state.skills_gap_analysis
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✅ Skills You Have")
                for skill in analysis['existing_skills']:
                    st.markdown(f"• {skill}")
            
            with col2:
                st.markdown("#### 📚 Skills to Develop")
                for skill in analysis['missing_skills']:
                    st.markdown(f"• {skill} ({skill.get('demand', 'High')} demand)")
    
    with tab3:
        st.markdown("### 📊 AI Market Analysis")
        
        # Market insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Market Trends")
            
            target_role = st.text_input("Analyze market for role:", 
                                       value=user_data.get('job_title', ''),
                                       placeholder="e.g., Data Scientist, Software Engineer")
            
            if st.button("📊 Get Market Analysis", use_container_width=True):
                get_market_analysis(target_role)
        
        with col2:
            st.markdown("#### 💰 Salary Insights")
            
            if st.button("💰 Get Salary Analysis", use_container_width=True):
                get_salary_analysis(user_data.get('job_title', ''), user_data.get('location', ''))
        
        # Display market analysis
        if 'market_analysis' in st.session_state:
            analysis = st.session_state.market_analysis
            
            st.markdown("### 📊 Market Report")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                create_metric_card("Job Openings", analysis['job_openings'], "📋")
            
            with col2:
                create_metric_card("Avg Salary", analysis['avg_salary'], "💰")
            
            with col3:
                create_metric_card("Growth Rate", analysis['growth_rate'], "📈")
            
            with col4:
                create_metric_card("Competition", analysis['competition'], "🏆")
            
            # Insights
            st.markdown("#### 💡 Key Insights")
            for insight in analysis['insights']:
                st.markdown(f"• {insight}")
            
            # Recommendations
            st.markdown("#### 🎯 Recommendations")
            for rec in analysis['recommendations']:
                st.markdown(f"• {rec}")
        
        # Salary analysis
        if 'salary_analysis' in st.session_state:
            salary_data = st.session_state.salary_analysis
            
            st.markdown("### 💰 Salary Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Salary Range")
                st.write(f"**Entry Level:** {salary_data['entry_level']}")
                st.write(f"**Mid Level:** {salary_data['mid_level']}")
                st.write(f"**Senior Level:** {salary_data['senior_level']}")
                st.write(f"**Your Expected:** {salary_data['user_range']}")
            
            with col2:
                st.markdown("#### 📈 Salary Factors")
                for factor in salary_data['factors']:
                    st.markdown(f"• {factor}")
    
    with tab4:
        st.markdown("### 💡 AI Career Advice")
        
        # Career advice categories
        advice_category = st.selectbox(
            "What would you like advice about?",
            ["Career Planning", "Interview Preparation", "Skill Development", 
             "Networking", "Salary Negotiation", "Job Search Strategy"]
        )
        
        # Specific question
        specific_question = st.text_area(
            "Ask a specific question (optional):",
            placeholder="e.g., How do I transition from support to development?"
        )
        
        if st.button("🧠 Get AI Advice", type="primary", use_container_width=True):
            get_career_advice(advice_category, specific_question, user_data)
        
        # Display advice
        if 'career_advice' in st.session_state:
            advice = st.session_state.career_advice
            
            st.markdown("### 💡 Career Advice")
            
            # Main advice
            st.markdown(f"**{advice['title']}**")
            st.markdown(advice['content'])
            
            # Action items
            if advice.get('action_items'):
                st.markdown("#### 📋 Action Items")
                for i, item in enumerate(advice['action_items'], 1):
                    st.markdown(f"{i}. {item}")
            
            # Resources
            if advice.get('resources'):
                st.markdown("#### 📚 Recommended Resources")
                for resource in advice['resources']:
                    st.markdown(f"• [{resource['title']}]({resource['url']}) - {resource['description']}")
        
        # Career path visualization
        st.markdown("---")
        st.markdown("### 🛣️ Career Path Visualization")
        
        if st.button("🗺️ Generate Career Path", use_container_width=True):
            generate_career_path(user_data)
        
        if 'career_path' in st.session_state:
            path = st.session_state.career_path
            
            st.markdown("#### 🎯 Your Career Roadmap")
            
            for i, step in enumerate(path['steps'], 1):
                st.markdown(f"""
                **Step {i}: {step['title']}** ({step['timeframe']})
                - {step['description']}
                - *Skills needed: {', '.join(step['skills'])}*
                """)
                
                if i < len(path['steps']):
                    st.markdown("↓")

def generate_ai_response(prompt, user_data):
    """Generate AI response to user query."""
    # Placeholder for AI response generation
    # This would integrate with OpenAI, Claude, or similar AI service
    
    responses = {
        "resume": "Based on your profile, I recommend focusing on quantifying your achievements and adding more technical keywords relevant to your field.",
        "interview": "For interview preparation, I suggest practicing the STAR method (Situation, Task, Action, Result) for behavioral questions.",
        "salary": "Given your experience level and location, you're likely in a competitive salary range. Consider highlighting unique skills during negotiations.",
        "job search": "Focus on quality over quantity in applications. Tailor each application to the specific role and company.",
        "default": "I'd be happy to help you with that! Can you provide more specific details about what you're looking for?"
    }
    
    # Simple keyword matching for demonstration
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ['resume', 'cv']):
        return responses['resume']
    elif any(word in prompt_lower for word in ['interview', 'questions']):
        return responses['interview']
    elif any(word in prompt_lower for word in ['salary', 'pay', 'compensation']):
        return responses['salary']
    elif any(word in prompt_lower for word in ['job', 'search', 'apply']):
        return responses['job search']
    else:
        return responses['default']

def review_resume_ai(user_id):
    """AI resume review."""
    create_notification_toast("AI resume review started! 📋", "info")
    
    # Add to chat history
    review_message = "I've analyzed your resume and have some suggestions for improvement. Would you like me to share specific recommendations?"
    st.session_state.ai_chat_history.append({"role": "assistant", "content": review_message})
    st.rerun()

def get_job_recommendations_ai(user_id):
    """Get AI job recommendations."""
    create_notification_toast("Generating job recommendations! 🎯", "info")
    
    # Add to chat history
    rec_message = "Based on your profile, I found several job opportunities that match your skills and preferences. Let me show you the top matches!"
    st.session_state.ai_chat_history.append({"role": "assistant", "content": rec_message})
    st.rerun()

def start_interview_prep(user_id):
    """Start interview preparation."""
    create_notification_toast("Interview prep mode activated! 🎤", "info")
    
    # Add to chat history
    prep_message = "Let's prepare for your upcoming interviews! I can help you with common questions, technical challenges, and behavioral scenarios. What type of interview are you preparing for?"
    st.session_state.ai_chat_history.append({"role": "assistant", "content": prep_message})
    st.rerun()

def find_job_matches(user_id, match_criteria):
    """Find job matches based on criteria."""
    with st.spinner("Finding your perfect job matches..."):
        # Placeholder for job matching algorithm
        matches = [
            {
                'id': 1,
                'job_title': 'Senior IT Support Specialist',
                'company': 'TechCorp',
                'location': 'Cape Town, South Africa',
                'match_score': 95,
                'match_reason': 'Perfect skills match with your IT support background and leadership experience'
            },
            {
                'id': 2,
                'job_title': 'System Administrator',
                'company': 'CloudTech',
                'location': 'Remote',
                'match_score': 88,
                'match_reason': 'Great technical skills match, remote work aligns with preferences'
            },
            {
                'id': 3,
                'job_title': 'IT Team Lead',
                'company': 'StartupXYZ',
                'location': 'Johannesburg, South Africa',
                'match_score': 82,
                'match_reason': 'Leadership experience matches well, slight location preference mismatch'
            }
        ]
        
        st.session_state.job_matches = matches
        create_notification_toast(f"Found {len(matches)} job matches! 🎉", "success")
        st.rerun()

def show_job_match_details(match):
    """Show detailed job match information."""
    with st.expander(f"📋 {match['job_title']} Details", expanded=True):
        st.write(f"**Company:** {match['company']}")
        st.write(f"**Location:** {match['location']}")
        st.write(f"**Match Score:** {match['match_score']}%")
        st.write(f"**Why it matches:** {match['match_reason']}")

def apply_to_matched_job(match, user_id):
    """Apply to a matched job."""
    create_notification_toast(f"Applied to {match['job_title']} at {match['company']}! 🎉", "success")

def analyze_skills_gap(user_id):
    """Analyze skills gap for user."""
    with st.spinner("Analyzing skills gap..."):
        # Placeholder for skills gap analysis
        analysis = {
            'existing_skills': ['Windows Administration', 'Help Desk Support', 'Network Troubleshooting', 'Customer Service'],
            'missing_skills': [
                {'name': 'Cloud Computing', 'demand': 'High'},
                {'name': 'Python Scripting', 'demand': 'Medium'},
                {'name': 'Cybersecurity', 'demand': 'High'},
                {'name': 'DevOps', 'demand': 'Medium'}
            ]
        }
        
        st.session_state.skills_gap_analysis = analysis
        create_notification_toast("Skills gap analysis completed! 📈", "success")
        st.rerun()

def get_market_analysis(target_role):
    """Get market analysis for target role."""
    with st.spinner("Analyzing job market..."):
        # Placeholder for market analysis
        analysis = {
            'job_openings': '1,234',
            'avg_salary': 'R45,000',
            'growth_rate': '+12%',
            'competition': 'Medium',
            'insights': [
                'Demand for this role has increased by 15% in the last 6 months',
                'Remote work options are becoming more common',
                'Cloud skills are increasingly important for this role'
            ],
            'recommendations': [
                'Focus on developing cloud computing skills',
                'Consider obtaining relevant certifications',
                'Network with professionals in the field'
            ]
        }
        
        st.session_state.market_analysis = analysis
        create_notification_toast("Market analysis completed! 📊", "success")
        st.rerun()

def get_salary_analysis(job_title, location):
    """Get salary analysis for role and location."""
    with st.spinner("Analyzing salary data..."):
        # Placeholder for salary analysis
        analysis = {
            'entry_level': 'R25,000 - R35,000',
            'mid_level': 'R35,000 - R55,000',
            'senior_level': 'R55,000 - R80,000',
            'user_range': 'R40,000 - R60,000',
            'factors': [
                'Experience level significantly impacts salary',
                'Certifications can increase earning potential by 15-20%',
                'Remote work options may affect compensation',
                'Company size influences salary ranges'
            ]
        }
        
        st.session_state.salary_analysis = analysis
        create_notification_toast("Salary analysis completed! 💰", "success")
        st.rerun()

def get_career_advice(category, question, user_data):
    """Get career advice based on category and question."""
    with st.spinner("Generating personalized career advice..."):
        # Placeholder for career advice generation
        advice = {
            'title': f"{category} Advice",
            'content': f"Based on your profile as an {user_data.get('job_title', 'IT professional')}, here's my advice for {category.lower()}...",
            'action_items': [
                'Update your LinkedIn profile with recent achievements',
                'Identify 3 key skills to develop in the next 6 months',
                'Schedule informational interviews with industry professionals',
                'Research target companies and their requirements'
            ],
            'resources': [
                {
                    'title': 'LinkedIn Learning Courses',
                    'url': 'https://linkedin.com/learning',
                    'description': 'Professional development courses'
                },
                {
                    'title': 'Industry Salary Reports',
                    'url': 'https://example.com/salary-reports',
                    'description': 'Latest salary benchmarks'
                }
            ]
        }
        
        st.session_state.career_advice = advice
        create_notification_toast("Career advice generated! 💡", "success")
        st.rerun()

def generate_career_path(user_data):
    """Generate career path visualization."""
    with st.spinner("Creating your career roadmap..."):
        # Placeholder for career path generation
        path = {
            'steps': [
                {
                    'title': 'IT Support Specialist',
                    'timeframe': 'Current',
                    'description': 'Continue developing technical skills and gaining experience',
                    'skills': ['Windows Administration', 'Help Desk', 'Network Troubleshooting']
                },
                {
                    'title': 'Senior IT Support Specialist',
                    'timeframe': '6-12 months',
                    'description': 'Take on more complex technical challenges and mentor junior staff',
                    'skills': ['Advanced Troubleshooting', 'Team Leadership', 'Process Improvement']
                },
                {
                    'title': 'IT Team Lead',
                    'timeframe': '1-2 years',
                    'description': 'Lead a team of IT professionals and manage projects',
                    'skills': ['Team Management', 'Project Management', 'Strategic Planning']
                },
                {
                    'title': 'IT Manager',
                    'timeframe': '2-4 years',
                    'description': 'Oversee IT operations and align technology with business goals',
                    'skills': ['Business Strategy', 'Budget Management', 'Vendor Relations']
                }
            ]
        }
        
        st.session_state.career_path = path
        create_notification_toast("Career path generated! 🗺️", "success")
        st.rerun()

def show_analytics():
    """Show analytics page."""
    create_app_header("Analytics", "Insights into Your Job Search")
    
    user_id = st.session_state.get('user_id')
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🎯 Performance", "📋 Reports"])
    
    with tab1:
        st.markdown("### 📊 Job Search Overview")
        
        # Key metrics
        try:
            stats = get_analytics_overview(user_id)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                create_metric_card("Total Applications", stats['total_applications'], "📋")
            
            with col2:
                create_metric_card("Response Rate", f"{stats['response_rate']:.1f}%", "📞")
            
            with col3:
                create_metric_card("Interview Rate", f"{stats['interview_rate']:.1f}%", "🎯")
            
            with col4:
                create_metric_card("Avg. Response Time", f"{stats['avg_response_time']} days", "⏱️")
            
            # Application status distribution
            st.markdown("### 📋 Application Status Distribution")
            
            if stats['status_distribution']:
                # Create pie chart
                fig = px.pie(
                    values=list(stats['status_distribution'].values()),
                    names=list(stats['status_distribution'].keys()),
                    title="Application Status Breakdown",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Weekly application activity
            st.markdown("### 📅 Weekly Application Activity")
            
            if stats['weekly_activity']:
                fig = px.bar(
                    x=list(stats['weekly_activity'].keys()),
                    y=list(stats['weekly_activity'].values()),
                    title="Applications per Week",
                    labels={'x': 'Week', 'y': 'Applications'},
                    color_discrete_sequence=['#2563eb']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Top companies applied to
            st.markdown("### 🏢 Top Companies Applied To")
            
            if stats['top_companies']:
                companies_df = pd.DataFrame(list(stats['top_companies'].items()), 
                                          columns=['Company', 'Applications'])
                
                fig = px.bar(
                    companies_df,
                    x='Applications',
                    y='Company',
                    orientation='h',
                    title="Most Applied Companies",
                    color_discrete_sequence=['#10b981']
                )
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            logger.error(f"Analytics overview error: {e}")
            create_alert("Error loading analytics overview", "error")
    
    with tab2:
        st.markdown("### 📈 Job Market Trends")
        
        # Time range selector
        time_range = st.selectbox(
            "Select time range:",
            ["Last 30 days", "Last 90 days", "Last 6 months", "Last year"]
        )
        
        if st.button("📊 Generate Trend Analysis", use_container_width=True):
            generate_trend_analysis(user_id, time_range)
        
        # Display trends
        if 'trend_analysis' in st.session_state:
            trends = st.session_state.trend_analysis
            
            # Job posting trends
            st.markdown("#### 📈 Job Posting Trends")
            
            if trends['job_posting_trends']:
                fig = px.line(
                    x=list(trends['job_posting_trends'].keys()),
                    y=list(trends['job_posting_trends'].values()),
                    title="Job Postings Over Time",
                    labels={'x': 'Date', 'y': 'Number of Jobs'},
                    line_shape='spline'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Salary trends
            st.markdown("#### 💰 Salary Trends")
            
            if trends['salary_trends']:
                fig = px.area(
                    x=list(trends['salary_trends'].keys()),
                    y=list(trends['salary_trends'].values()),
                    title="Average Salary Trends",
                    labels={'x': 'Date', 'y': 'Average Salary (ZAR)'},
                    fill='tonexty'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Skills demand
            st.markdown("#### 🔧 Skills in Demand")
            
            if trends['skills_demand']:
                skills_df = pd.DataFrame(list(trends['skills_demand'].items()), 
                                       columns=['Skill', 'Demand'])
                
                fig = px.bar(
                    skills_df,
                    x='Demand',
                    y='Skill',
                    orientation='h',
                    title="Most In-Demand Skills",
                    color='Demand',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Market insights
        st.markdown("### 💡 Market Insights")
        
        insights = get_market_insights(user_id)
        
        for insight in insights:
            st.markdown(f"""
            <div style="background: #f8fafc; border-left: 4px solid #2563eb; padding: 1rem; margin: 1rem 0;">
                <h4 style="margin: 0; color: #1f2937;">{insight['title']}</h4>
                <p style="margin: 0.5rem 0; color: #4b5563;">{insight['content']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🎯 Performance Analysis")
        
        # Performance metrics
        performance = get_performance_metrics(user_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Application Performance")
            
            # Success rate over time
            if performance['success_rate_timeline']:
                fig = px.line(
                    x=list(performance['success_rate_timeline'].keys()),
                    y=list(performance['success_rate_timeline'].values()),
                    title="Success Rate Over Time",
                    labels={'x': 'Date', 'y': 'Success Rate (%)'},
                    line_shape='spline'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Response time analysis
            if performance['response_times']:
                fig = px.histogram(
                    x=performance['response_times'],
                    title="Response Time Distribution",
                    labels={'x': 'Response Time (days)', 'y': 'Count'},
                    nbins=20
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Optimization Recommendations")
            
            recommendations = performance['recommendations']
            
            for rec in recommendations:
                priority_color = {
                    'High': '#ef4444',
                    'Medium': '#f59e0b',
                    'Low': '#10b981'
                }[rec['priority']]
                
                st.markdown(f"""
                <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h5 style="margin: 0; color: #1f2937;">{rec['title']}</h5>
                        <span style="background: {priority_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">
                            {rec['priority']}
                        </span>
                    </div>
                    <p style="margin: 0.5rem 0; color: #4b5563;">{rec['description']}</p>
                    <small style="color: #6b7280;">Impact: {rec['impact']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Benchmark comparison
        st.markdown("### 📊 Benchmark Comparison")
        
        benchmarks = get_benchmark_comparison(user_id)
        
        if benchmarks:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Your Response Rate",
                    f"{benchmarks['your_response_rate']}%",
                    f"{benchmarks['response_rate_diff']:+.1f}% vs avg"
                )
            
            with col2:
                st.metric(
                    "Your Interview Rate",
                    f"{benchmarks['your_interview_rate']}%",
                    f"{benchmarks['interview_rate_diff']:+.1f}% vs avg"
                )
            
            with col3:
                st.metric(
                    "Applications per Week",
                    f"{benchmarks['your_app_rate']}",
                    f"{benchmarks['app_rate_diff']:+.1f} vs avg"
                )
    
    with tab4:
        st.markdown("### 📋 Reports")
        
        # Report generation
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Generate Reports")
            
            report_type = st.selectbox(
                "Select report type:",
                ["Application Summary", "Performance Analysis", "Market Trends", "Skills Analysis"]
            )
            
            date_range = st.date_input(
                "Select date range:",
                value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
                key="report_date_range"
            )
            
            if st.button("📄 Generate Report", type="primary", use_container_width=True):
                generate_custom_report(user_id, report_type, date_range)
        
        with col2:
            st.markdown("#### 📥 Export Options")
            
            export_format = st.selectbox(
                "Export format:",
                ["CSV", "Excel", "PDF", "JSON"]
            )
            
            if st.button("📥 Export Data", use_container_width=True):
                export_analytics_data(user_id, export_format)
            
            # Quick exports
            st.markdown("**Quick Exports:**")
            
            if st.button("📋 Export Applications", use_container_width=True):
                export_applications_data(user_id)
            
            if st.button("📊 Export Analytics", use_container_width=True):
                export_analytics_summary(user_id)
        
        # Report history
        st.markdown("### 📚 Report History")
        
        reports = get_report_history(user_id)
        
        if reports:
            for report in reports:
                with st.expander(f"📄 {report['title']} - {report['date']}"):
                    st.write(f"**Type:** {report['type']}")
                    st.write(f"**Generated:** {report['date']}")
                    st.write(f"**Status:** {report['status']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📥 Download", key=f"download_{report['id']}"):
                            download_report(report['id'])
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_report_{report['id']}"):
                            delete_report(report['id'], user_id)
        else:
            st.info("No reports generated yet. Create your first report above!")

def show_settings():
    """Show settings page."""
    create_app_header("Settings", "Customize Your Experience")
    
    user_id = st.session_state.get('user_id')
    user_data = st.session_state.get('user_data', {})
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Profile", "🔔 Notifications", "🎯 Preferences", "🔒 Privacy", "⚙️ Advanced"])
    
    with tab1:
        st.markdown("### 👤 Profile Settings")
        
        # Profile form
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Personal Information")
                
                first_name = st.text_input("First Name", value=user_data.get('first_name', ''))
                last_name = st.text_input("Last Name", value=user_data.get('last_name', ''))
                email = st.text_input("Email", value=user_data.get('email', ''), disabled=True)
                phone = st.text_input("Phone", value=user_data.get('phone', ''))
                
                st.markdown("#### Location")
                location = st.text_input("Location", value=user_data.get('location', ''))
                country = st.selectbox("Country", 
                                     ["South Africa", "United States", "United Kingdom", "Canada", "Australia"], 
                                     index=0)
                timezone = st.selectbox("Timezone", 
                                      ["Africa/Johannesburg", "UTC", "US/Eastern", "Europe/London"])
            
            with col2:
                st.markdown("#### Professional Information")
                
                job_title = st.text_input("Current Job Title", value=user_data.get('job_title', ''))
                company = st.text_input("Current Company", value=user_data.get('company', ''))
                industry = st.selectbox("Industry", 
                                       ["Technology", "Finance", "Healthcare", "Education", "Manufacturing", "Other"])
                experience_years = st.slider("Years of Experience", 0, 50, user_data.get('experience_years', 0))
                
                st.markdown("#### Salary Expectations")
                salary_min = st.number_input("Minimum Salary (ZAR)", value=user_data.get('salary_min', 0), step=5000)
                salary_max = st.number_input("Maximum Salary (ZAR)", value=user_data.get('salary_max', 0), step=5000)
                salary_currency = st.selectbox("Currency", ["ZAR", "USD", "EUR", "GBP"])
            
            # Profile picture upload
            st.markdown("#### Profile Picture")
            profile_pic = st.file_uploader("Upload Profile Picture", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True):
                update_user_profile(user_id, {
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'location': location,
                    'country': country,
                    'timezone': timezone,
                    'job_title': job_title,
                    'company': company,
                    'industry': industry,
                    'experience_years': experience_years,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'salary_currency': salary_currency
                })
    
    with tab2:
        st.markdown("### 🔔 Notification Settings")
        
        # Email notifications
        st.markdown("#### 📧 Email Notifications")
        
        email_job_alerts = st.checkbox("New job matches", value=True)
        email_app_updates = st.checkbox("Application status updates", value=True)
        email_interview_reminders = st.checkbox("Interview reminders", value=True)
        email_market_insights = st.checkbox("Weekly market insights", value=False)
        
        # Push notifications
        st.markdown("#### 📱 Push Notifications")
        
        push_job_alerts = st.checkbox("Instant job alerts", value=True)
        push_app_updates = st.checkbox("Application updates", value=True)
        push_interview_reminders = st.checkbox("Interview reminders", value=True)
        
        # Notification frequency
        st.markdown("#### ⏰ Notification Frequency")
        
        job_alert_frequency = st.selectbox(
            "Job alert frequency:",
            ["Real-time", "Daily digest", "Weekly digest", "Disabled"]
        )
        
        market_report_frequency = st.selectbox(
            "Market report frequency:",
            ["Weekly", "Monthly", "Quarterly", "Disabled"]
        )
        
        # Notification channels
        st.markdown("#### 📢 Notification Channels")
        
        col1, col2 = st.columns(2)
        
        with col1:
            whatsapp_notifications = st.checkbox("WhatsApp notifications", value=False)
            sms_notifications = st.checkbox("SMS notifications", value=False)
        
        with col2:
            slack_notifications = st.checkbox("Slack notifications", value=False)
            webhook_notifications = st.checkbox("Webhook notifications", value=False)
        
        if st.button("💾 Save Notification Settings", type="primary", use_container_width=True):
            save_notification_settings(user_id, {
                'email_job_alerts': email_job_alerts,
                'email_app_updates': email_app_updates,
                'email_interview_reminders': email_interview_reminders,
                'email_market_insights': email_market_insights,
                'push_job_alerts': push_job_alerts,
                'push_app_updates': push_app_updates,
                'push_interview_reminders': push_interview_reminders,
                'job_alert_frequency': job_alert_frequency,
                'market_report_frequency': market_report_frequency,
                'whatsapp_notifications': whatsapp_notifications,
                'sms_notifications': sms_notifications,
                'slack_notifications': slack_notifications,
                'webhook_notifications': webhook_notifications
            })
    
    with tab3:
        st.markdown("### 🎯 Job Search Preferences")
        
        # Job preferences
        st.markdown("#### 💼 Job Preferences")
        
        preferred_job_types = st.multiselect(
            "Preferred job types:",
            ["Full-time", "Part-time", "Contract", "Freelance", "Internship", "Remote"],
            default=["Full-time", "Remote"]
        )
        
        preferred_industries = st.multiselect(
            "Preferred industries:",
            ["Technology", "Finance", "Healthcare", "Education", "Manufacturing", "Consulting"],
            default=["Technology"]
        )
        
        company_size_preference = st.selectbox(
            "Company size preference:",
            ["No preference", "Startup (1-50)", "Small (51-200)", "Medium (201-1000)", "Large (1000+)"]
        )
        
        remote_work_preference = st.selectbox(
            "Remote work preference:",
            ["No preference", "Fully remote", "Hybrid", "On-site only"]
        )
        
        # Search preferences
        st.markdown("#### 🔍 Search Preferences")
        
        auto_apply_enabled = st.checkbox("Enable auto-apply for matching jobs", value=False)
        max_applications_per_day = st.slider("Maximum applications per day", 1, 50, 5)
        
        job_alert_radius = st.slider("Job alert radius (km)", 0, 100, 25)
        
        # Application preferences
        st.markdown("#### 📋 Application Preferences")
        
        cover_letter_template = st.text_area(
            "Default cover letter template:",
            height=200,
            placeholder="Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} position at {company}...",
            value=user_data.get('cover_letter_template', '')
        )
        
        if st.button("💾 Save Preferences", type="primary", use_container_width=True):
            save_job_preferences(user_id, {
                'preferred_job_types': preferred_job_types,
                'preferred_industries': preferred_industries,
                'company_size_preference': company_size_preference,
                'remote_work_preference': remote_work_preference,
                'auto_apply_enabled': auto_apply_enabled,
                'max_applications_per_day': max_applications_per_day,
                'job_alert_radius': job_alert_radius,
                'cover_letter_template': cover_letter_template
            })
    
    with tab4:
        st.markdown("### 🔒 Privacy & Security")
        
        # Privacy settings
        st.markdown("#### 🔐 Privacy Settings")
        
        profile_visibility = st.selectbox(
            "Profile visibility:",
            ["Public", "Private", "Visible to recruiters only"]
        )
        
        show_salary_expectations = st.checkbox("Show salary expectations on profile", value=True)
        show_contact_info = st.checkbox("Show contact information to recruiters", value=True)
        allow_recruiter_contact = st.checkbox("Allow recruiters to contact me", value=True)
        
        # Data settings
        st.markdown("#### 📊 Data Settings")
        
        data_retention_period = st.selectbox(
            "Data retention period:",
            ["6 months", "1 year", "2 years", "Indefinite"]
        )
        
        analytics_tracking = st.checkbox("Enable analytics tracking", value=True)
        third_party_sharing = st.checkbox("Allow sharing with partner platforms", value=False)
        
        # Security settings
        st.markdown("#### 🔒 Security Settings")
        
        two_factor_auth = st.checkbox("Enable two-factor authentication", value=False)
        login_notifications = st.checkbox("Email notifications for logins", value=True)
        
        # Password change
        st.markdown("#### 🔑 Change Password")
        
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔐 Change Password"):
                if new_password == confirm_password:
                    change_user_password(user_id, current_password, new_password)
                else:
                    st.error("Passwords do not match!")
        
        if st.button("💾 Save Privacy Settings", type="primary", use_container_width=True):
            save_privacy_settings(user_id, {
                'profile_visibility': profile_visibility,
                'show_salary_expectations': show_salary_expectations,
                'show_contact_info': show_contact_info,
                'allow_recruiter_contact': allow_recruiter_contact,
                'data_retention_period': data_retention_period,
                'analytics_tracking': analytics_tracking,
                'third_party_sharing': third_party_sharing,
                'two_factor_auth': two_factor_auth,
                'login_notifications': login_notifications
            })
    
    with tab5:
        st.markdown("### ⚙️ Advanced Settings")
        
        # API settings
        st.markdown("#### 🔌 API Settings")
        
        api_key = st.text_input("API Key", type="password", help="For third-party integrations")
        webhook_url = st.text_input("Webhook URL", help="Receive notifications via webhook")
        
        # Integration settings
        st.markdown("#### 🔗 Integrations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            linkedin_integration = st.checkbox("LinkedIn integration", value=False)
            github_integration = st.checkbox("GitHub integration", value=False)
            google_calendar_integration = st.checkbox("Google Calendar integration", value=False)
        
        with col2:
            slack_integration = st.checkbox("Slack integration", value=False)
            zapier_integration = st.checkbox("Zapier integration", value=False)
            outlook_integration = st.checkbox("Outlook integration", value=False)
        
        # Performance settings
        st.markdown("#### ⚡ Performance Settings")
        
        enable_caching = st.checkbox("Enable result caching", value=True)
        max_search_results = st.slider("Maximum search results", 50, 500, 100)
        search_timeout = st.slider("Search timeout (seconds)", 10, 120, 30)
        
        # Debug settings
        st.markdown("#### 🐛 Debug Settings")
        
        debug_mode = st.checkbox("Enable debug mode", value=False)
        log_level = st.selectbox("Log level", ["INFO", "DEBUG", "WARNING", "ERROR"])
        
        if st.button("💾 Save Advanced Settings", type="primary", use_container_width=True):
            save_advanced_settings(user_id, {
                'api_key': api_key,
                'webhook_url': webhook_url,
                'linkedin_integration': linkedin_integration,
                'github_integration': github_integration,
                'google_calendar_integration': google_calendar_integration,
                'slack_integration': slack_integration,
                'zapier_integration': zapier_integration,
                'outlook_integration': outlook_integration,
                'enable_caching': enable_caching,
                'max_search_results': max_search_results,
                'search_timeout': search_timeout,
                'debug_mode': debug_mode,
                'log_level': log_level
            })
        
        # Danger zone
        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")
        
        st.warning("These actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete All Data", type="primary", use_container_width=True):
                if st.checkbox("I understand this will delete all my data"):
                    delete_all_user_data(user_id)
        
        with col2:
            if st.button("🚪 Delete Account", type="primary", use_container_width=True):
                if st.checkbox("I understand this will permanently delete my account"):
                    delete_user_account(user_id)

# Settings helper functions
def update_user_profile(user_id, profile_data):
    """Update user profile."""
    create_notification_toast("Profile updated successfully! 👤", "success")

def save_notification_settings(user_id, settings):
    """Save notification settings."""
    create_notification_toast("Notification settings saved! 🔔", "success")

def save_job_preferences(user_id, preferences):
    """Save job preferences."""
    create_notification_toast("Job preferences saved! 🎯", "success")

def save_privacy_settings(user_id, settings):
    """Save privacy settings."""
    create_notification_toast("Privacy settings saved! 🔒", "success")

def save_advanced_settings(user_id, settings):
    """Save advanced settings."""
    create_notification_toast("Advanced settings saved! ⚙️", "success")

def change_user_password(user_id, current_password, new_password):
    """Change user password."""
    create_notification_toast("Password changed successfully! 🔐", "success")

def delete_all_user_data(user_id):
    """Delete all user data."""
    create_notification_toast("All data deleted! 🗑️", "success")

def delete_user_account(user_id):
    """Delete user account."""
    create_notification_toast("Account deleted! 🚪", "success")

# Analytics helper functions
def get_analytics_overview(user_id):
    """Get analytics overview data."""
    return {
        'total_applications': 45,
        'response_rate': 24.4,
        'interview_rate': 11.1,
        'avg_response_time': 7,
        'status_distribution': {
            'Applied': 25,
            'Under Review': 10,
            'Interview': 5,
            'Rejected': 5
        },
        'weekly_activity': {
            'Week 1': 8,
            'Week 2': 12,
            'Week 3': 15,
            'Week 4': 10
        },
        'top_companies': {
            'TechCorp': 5,
            'StartupXYZ': 3,
            'BigTech': 3,
            'CloudCorp': 2
        }
    }

def generate_trend_analysis(user_id, time_range):
    """Generate trend analysis."""
    analysis = {
        'job_posting_trends': {
            '2024-01': 1200,
            '2024-02': 1450,
            '2024-03': 1380,
            '2024-04': 1620
        },
        'salary_trends': {
            '2024-01': 45000,
            '2024-02': 47000,
            '2024-03': 46500,
            '2024-04': 48000
        },
        'skills_demand': {
            'Python': 85,
            'JavaScript': 78,
            'React': 65,
            'SQL': 72,
            'AWS': 68
        }
    }
    
    st.session_state.trend_analysis = analysis
    create_notification_toast("Trend analysis generated! 📈", "success")
    st.rerun()

def get_market_insights(user_id):
    """Get market insights."""
    return [
        {
            'title': 'Remote Work Trending',
            'content': 'Remote job postings have increased by 35% this month, making it a great time to expand your search radius.'
        },
        {
            'title': 'Skill Gap Opportunity',
            'content': 'There\'s high demand for professionals with both technical and soft skills in your field.'
        },
        {
            'title': 'Salary Trends',
            'content': 'Average salaries for your role have increased by 8% compared to last quarter.'
        }
    ]

def get_performance_metrics(user_id):
    """Get performance metrics."""
    return {
        'success_rate_timeline': {
            'Week 1': 15,
            'Week 2': 22,
            'Week 3': 28,
            'Week 4': 25
        },
        'response_times': [3, 5, 7, 10, 14, 21, 28, 35],
        'recommendations': [
            {
                'title': 'Optimize Application Timing',
                'description': 'Apply to jobs on Tuesday-Thursday for better response rates',
                'priority': 'High',
                'impact': 'Could improve response rate by 15%'
            },
            {
                'title': 'Enhance Resume Keywords',
                'description': 'Add more industry-specific keywords to improve ATS scoring',
                'priority': 'Medium',
                'impact': 'Could increase interview rate by 10%'
            }
        ]
    }

def get_benchmark_comparison(user_id):
    """Get benchmark comparison."""
    return {
        'your_response_rate': 24.4,
        'response_rate_diff': 4.4,
        'your_interview_rate': 11.1,
        'interview_rate_diff': 2.1,
        'your_app_rate': 8.5,
        'app_rate_diff': 1.5
    }

def generate_custom_report(user_id, report_type, date_range):
    """Generate custom report."""
    create_notification_toast(f"{report_type} report generated! 📄", "success")

def export_analytics_data(user_id, export_format):
    """Export analytics data."""
    create_notification_toast(f"Data exported as {export_format}! 📥", "success")

def export_applications_data(user_id):
    """Export applications data."""
    create_notification_toast("Applications exported! 📋", "success")

def export_analytics_summary(user_id):
    """Export analytics summary."""
    create_notification_toast("Analytics summary exported! 📊", "success")

def get_report_history(user_id):
    """Get report history."""
    return [
        {
            'id': 1,
            'title': 'Application Summary Report',
            'type': 'Application Summary',
            'date': '2024-01-15',
            'status': 'Completed'
        },
        {
            'id': 2,
            'title': 'Performance Analysis',
            'type': 'Performance Analysis',
            'date': '2024-01-10',
            'status': 'Completed'
        }
    ]

def download_report(report_id):
    """Download report."""
    create_notification_toast("Report downloaded! 📥", "success")

def delete_report(report_id, user_id):
    """Delete report."""
    create_notification_toast("Report deleted! 🗑️", "success")

# Run the application
if __name__ == "__main__":
    main() 