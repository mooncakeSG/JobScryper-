import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will rely on system environment variables

# Import our custom modules
from indeed_scraper import IndeedScraper
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

# Configure page
st.set_page_config(
    page_title="Auto Apply for Tech Jobs",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'applications' not in st.session_state:
    st.session_state.applications = []
if 'jobs_data' not in st.session_state:
    st.session_state.jobs_data = {
        'jobspy': [],
        'indeed': [], 
        'linkedin': [], 
        'alternatives': []
    }
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
required_keys = ['jobspy', 'indeed', 'linkedin', 'alternatives']
for key in required_keys:
    if key not in st.session_state.jobs_data:
        st.session_state.jobs_data[key] = []

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
                st.sidebar.success(f"📄 Resume parsed successfully! ({parsed_resume.get('cleaned_text_length', 0)} chars)")
            else:
                st.sidebar.warning("⚠️ Resume parsing had issues, but file was saved")
                
        except Exception as e:
            st.sidebar.warning(f"⚠️ Resume parsing failed: {str(e)}")
            st.session_state.resume_parsed = None
        
        return str(file_path)
    return None

def load_applications():
    """Load applications from CSV file"""
    csv_path = "applications.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            return df.to_dict('records')
        except Exception as e:
            st.error(f"Error loading applications: {e}")
    return []

def save_applications(applications):
    """Save applications to CSV file"""
    try:
        df = pd.DataFrame(applications)
        df.to_csv("applications.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Error saving applications: {e}")
        return False

def display_job_card(job, source, index):
    """Display an enhanced job card with AI analysis and apply button"""
    # Add source indicator in the title
    source_emoji = {
        'jobspy': '🚀',
        'indeed': '📰',
        'linkedin': '💼', 
        'alternatives': '🌐'
    }
    
    source_name = job.get('source', source.title())
    title_prefix = f"{source_emoji.get(source, '📋')} [{source_name}]"
    
    # Add match score to title if available
    match_score = job.get('match_percentage', 0)
    ats_score = job.get('ats_score', 0)
    
    score_display = ""
    if match_score > 0:
        score_display += f" | 🎯 Match: {match_score}%"
    if ats_score > 0:
        score_display += f" | 📊 ATS: {ats_score}%"
    
    card_title = f"{title_prefix} {job['title']} at {job['company']}{score_display}"
    
    with st.expander(card_title):
        # AI Analysis Section (if resume is available)
        if st.session_state.resume_path and st.session_state.resume_parsed:
            # Calculate or retrieve analysis
            job_key = f"{job.get('title', '')}_{job.get('company', '')}_{index}"
            
            if job_key not in st.session_state.ats_reports:
                # Generate ATS report for this job
                try:
                    ats_report = generate_ats_report_for_job(job, st.session_state.resume_path)
                    st.session_state.ats_reports[job_key] = ats_report
                except Exception as e:
                    st.warning(f"Could not generate ATS analysis: {str(e)}")
                    ats_report = None
            else:
                ats_report = st.session_state.ats_reports[job_key]
            
            # Display AI Analysis
            if ats_report and 'error' not in ats_report:
                st.markdown("### 🤖 AI Analysis")
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    match_percentage = job.get('match_percentage', 0)
                    if match_percentage > 80:
                        match_color = "🟢"
                    elif match_percentage > 60:
                        match_color = "🟡"
                    else:
                        match_color = "🔴"
                    st.metric("Resume Match", f"{match_color} {match_percentage}%")
                
                with col2:
                    ats_score = ats_report['ats_analysis']['ats_score']
                    if ats_score > 70:
                        ats_color = "🟢"
                    elif ats_score > 50:
                        ats_color = "🟡"
                    else:
                        ats_color = "🔴"
                    st.metric("ATS Score", f"{ats_color} {ats_score}%")
                
                with col3:
                    missing_count = len(ats_report['missing_keywords'])
                    st.metric("Missing Keywords", f"⚠️ {missing_count}")
                
                with col4:
                    bias_flags = len(ats_report['bias_analysis']['bias_flags'])
                    if bias_flags == 0:
                        bias_indicator = "✅ Clean"
                    elif bias_flags <= 2:
                        bias_indicator = f"⚠️ {bias_flags} flags"
                    else:
                        bias_indicator = f"❌ {bias_flags} flags"
                    st.metric("Bias Check", bias_indicator)
                
                # Missing Keywords (if any)
                if ats_report['missing_keywords']:
                    st.markdown("**🔍 Top Missing Keywords:**")
                    missing_kw = ats_report['missing_keywords'][:5]  # Top 5
                    missing_text = ", ".join([kw['keyword'] for kw in missing_kw])
                    st.markdown(f"_{missing_text}_")
                
                # Match factors (if available)
                if job.get('key_factors'):
                    st.markdown(f"**✨ Key Match Factors:** {', '.join(job['key_factors'])}")
                
                # Bias warnings (if any)
                if ats_report['bias_analysis']['bias_flags']:
                    st.warning(f"⚠️ {len(ats_report['bias_analysis']['bias_flags'])} potential bias concern(s) detected in job posting")
                
                # ATS Report Download
                col_download1, col_download2 = st.columns(2)
                with col_download1:
                    if st.button(f"📊 Download ATS Report (JSON)", key=f"download_json_{source}_{index}"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        job_title_clean = "".join(c for c in job.get('title', 'job') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        company_clean = "".join(c for c in job.get('company', 'company') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        filename = f"ats_report_{job_title_clean}_{company_clean}_{timestamp}.json"
                        
                        if save_ats_report(ats_report, f"reports/{filename}"):
                            st.success(f"✅ Report saved to reports/{filename}")
                
                with col_download2:
                    if st.button(f"📄 Download ATS Report (TXT)", key=f"download_txt_{source}_{index}"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        job_title_clean = "".join(c for c in job.get('title', 'job') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        company_clean = "".join(c for c in job.get('company', 'company') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        filename = f"ats_report_{job_title_clean}_{company_clean}_{timestamp}.txt"
                        
                        if export_ats_report_text(ats_report, f"reports/{filename}"):
                            st.success(f"✅ Report saved to reports/{filename}")
                
                # Groq AI Resume Suggestions
                st.markdown("---")
                st.markdown("### 🤖 AI Resume Optimization")
                
                col_groq1, col_groq2 = st.columns(2)
                with col_groq1:
                    if st.button(f"💡 Improve Resume for This Job", key=f"groq_suggest_{source}_{index}", type="secondary"):
                        with st.spinner("🤖 Generating AI-powered resume suggestions..."):
                            try:
                                # Get resume text
                                resume_text = get_resume_text_for_matching(st.session_state.resume_path)
                                
                                # Generate suggestions using Groq
                                suggestions = generate_resume_suggestions_groq(resume_text, job)
                                
                                if suggestions.get('success'):
                                    # Store in session state
                                    st.session_state.groq_suggestions[job_key] = suggestions
                                    st.success("✅ Resume suggestions generated!")
                                else:
                                    st.error(f"❌ Failed to generate suggestions: {suggestions.get('error', 'Unknown error')}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error generating suggestions: {str(e)}")
                                st.info("💡 Make sure GROQ_API_KEY is set in your environment variables")
                
                # Display Groq suggestions if available
                if job_key in st.session_state.groq_suggestions:
                    suggestions_data = st.session_state.groq_suggestions[job_key]
                    
                    if suggestions_data.get('success'):
                        st.markdown("### 🎯 AI Resume Improvement Suggestions")
                        
                        suggestions = suggestions_data['suggestions']
                        
                        # Fit Summary
                        if suggestions.get('fit_summary'):
                            st.markdown("**📝 Resume-Job Fit Summary:**")
                            st.info(suggestions['fit_summary'])
                        
                        # Missing Keywords
                        if suggestions.get('missing_keywords'):
                            st.markdown("**🔍 Missing ATS Keywords:**")
                            keywords_text = " • ".join([f"**{kw}**" for kw in suggestions['missing_keywords'][:8]])
                            st.markdown(keywords_text)
                        
                        # Improvement Suggestions
                        if suggestions.get('improvement_suggestions'):
                            st.markdown("**🚀 Resume Improvement Suggestions:**")
                            for i, suggestion in enumerate(suggestions['improvement_suggestions'][:6], 1):
                                st.markdown(f"{i}. {suggestion}")
                        
                        # Professional Advice
                        if suggestions.get('professional_advice'):
                            st.markdown("**💼 Professional Advice:**")
                            for advice in suggestions['professional_advice'][:3]:
                                st.markdown(f"• {advice}")
                        
                        # Download suggestions
                        with col_groq2:
                            if st.button(f"📥 Download Suggestions", key=f"download_groq_{source}_{index}"):
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                job_title_clean = "".join(c for c in job.get('title', 'job') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                                company_clean = "".join(c for c in job.get('company', 'company') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                                filename = f"groq_suggestions_{job_title_clean}_{company_clean}_{timestamp}.txt"
                                
                                if save_suggestions_to_file(suggestions_data, f"reports/{filename}"):
                                    st.success(f"✅ Suggestions saved to reports/{filename}")
                        
                        # Show model info
                        st.caption(f"✨ Generated by {suggestions_data.get('model_used', 'Groq AI')} | Tokens: {suggestions_data.get('tokens_used', 'N/A')}")
                    
                    else:
                        st.error(f"❌ Suggestion generation failed: {suggestions_data.get('error', 'Unknown error')}")
                
                # Show sample suggestions if no Groq key available
                elif not os.getenv('GROQ_API_KEY'):
                    st.info("💡 Set GROQ_API_KEY environment variable to unlock AI-powered resume suggestions")
                    st.markdown("**Sample AI suggestions would include:**")
                    st.markdown("• Resume-job fit analysis • Missing ATS keywords • Improvement recommendations • Professional advice")
                
                st.markdown("---")
        
        # Job Details Section
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 📋 Job Details")
            st.write(f"**Location:** {job['location']}")
            st.write(f"**Company:** {job['company']}")
            if 'salary' in job and job['salary']:
                st.write(f"**Salary:** {job['salary']}")
            if 'description' in job and job['description']:
                description_text = job['description']
                if len(description_text) > 300:
                    st.write(f"**Description:** {description_text[:300]}...")
                    show_full_key = f"show_full_desc_{source}_{index}"
                    show_full = st.checkbox("📄 Show full description", key=show_full_key)
                    if show_full:
                        st.markdown("**Full Description:**")
                        st.markdown(f"_{description_text}_")
                else:
                    st.write(f"**Description:** {description_text}")
            if 'url' in job:
                st.write(f"**Job URL:** [View Job]({job['url']})")
            
            # Show additional job info
            if job.get('remote'):
                st.write("🏠 **Remote Work Available**")
            if job.get('easy_apply'):
                st.write("⚡ **Easy Apply Available**")
            if job.get('experience_level'):
                st.write(f"📈 **Experience Level:** {job['experience_level']}")
            if job.get('key_requirements'):
                st.write(f"🔧 **Key Requirements:** {', '.join(job['key_requirements'][:5])}")
        
        with col2:
            st.markdown("### 🚀 Actions")
            
            # Auto Apply button for LinkedIn jobs
            if source in ['linkedin', 'jobspy'] and job.get('source', '').lower() == 'linkedin':
                apply_key = f"apply_{source}_{index}"
                if st.button(f"🚀 Auto Apply", key=apply_key, type="primary"):
                    apply_to_job(job, source)
            else:
                st.write("*Manual apply required*")
                
            # External links
            if 'url' in job:
                if source == 'indeed' or job.get('source', '').lower() == 'indeed':
                    st.link_button("View on Indeed", job['url'])
                elif job.get('source', '').lower() == 'linkedin':
                    st.link_button("View on LinkedIn", job['url'])
                elif job.get('source', '').lower() == 'glassdoor':
                    st.link_button("View on Glassdoor", job['url'])
                elif job.get('source', '').lower() == 'zip_recruiter':
                    st.link_button("View on ZipRecruiter", job['url'])
                else:
                    st.link_button("View Job", job['url'])
            
            # Application urgency indicator
            if job.get('application_urgency') == 'Urgent':
                st.error("🚨 Apply ASAP!")
            elif job.get('application_urgency') == 'High':
                st.warning("⏰ High Priority")
            
            # IT Support score (if available)
            if job.get('it_support_score'):
                score = job['it_support_score']
                if score > 80:
                    st.success(f"🎯 IT Match: {score:.0f}%")
                elif score > 60:
                    st.warning(f"🎯 IT Match: {score:.0f}%")
                else:
                    st.info(f"🎯 IT Match: {score:.0f}%")

def apply_to_job(job, source):
    """Apply to a LinkedIn job automatically"""
    if not st.session_state.get('linkedin_email') or not st.session_state.get('linkedin_password'):
        st.error("Please provide LinkedIn credentials first!")
        return
    
    if not st.session_state.resume_path:
        st.error("Please upload your resume first!")
        return
    
    with st.spinner("Applying to job..."):
        try:
            auto_apply = AutoApply(
                email=st.session_state.linkedin_email,
                password=st.session_state.linkedin_password,
                resume_path=st.session_state.resume_path
            )
            
            success = auto_apply.apply_to_job(job['url'])
            
            if success:
                # Track application
                application = {
                    'job_title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'source': source,
                    'applied_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'Applied',
                    'job_url': job['url']
                }
                
                st.session_state.applications.append(application)
                save_applications(st.session_state.applications)
                
                st.success(f"✅ Successfully applied to {job['title']} at {job['company']}!")
            else:
                st.error("❌ Failed to apply. Please try again or apply manually.")
                
        except Exception as e:
            st.error(f"❌ Error during application: {str(e)}")

def main():
    # Header
    st.markdown('<h1 class="main-header">💼 Auto Apply for Tech Jobs</h1>', unsafe_allow_html=True)
    
    # Sidebar for user inputs
    st.sidebar.header("🔧 Configuration")
    
    # Job search parameters
    st.sidebar.subheader("Job Search Settings")
    job_title = st.sidebar.text_input("Job Title", value="IT Support", help="e.g., IT Support, Helpdesk, Desktop Support")
    location = st.sidebar.selectbox(
        "Location", 
        options=[
            "Port Elizabeth, Eastern Cape, South Africa",
            "East London, Eastern Cape, South Africa", 
            "Grahamstown, Eastern Cape, South Africa",
            "Cape Town, South Africa",
            "Johannesburg, South Africa",
            "Durban, South Africa",
            "Remote"
        ],
        index=0,
        help="Select your preferred location for job search"
    )
    
    # LinkedIn credentials
    st.sidebar.subheader("LinkedIn Credentials")
    linkedin_email = st.sidebar.text_input("LinkedIn Email", type="default", help="Your LinkedIn login email")
    linkedin_password = st.sidebar.text_input("LinkedIn Password", type="password", help="Your LinkedIn password")
    
    # Store credentials in session state
    st.session_state.linkedin_email = linkedin_email
    st.session_state.linkedin_password = linkedin_password
    
    # Resume upload
    st.sidebar.subheader("Resume Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your resume", 
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )
    
    if uploaded_file is not None:
        with st.spinner("Saving resume..."):
            st.session_state.resume_path = save_uploaded_resume(uploaded_file)
            if st.session_state.resume_path:
                st.sidebar.success("✅ Resume uploaded successfully!")
    
    # Load existing applications
    if not st.session_state.applications:
        st.session_state.applications = load_applications()
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search Jobs", "🤖 AI Tech Matching", "📋 Applications", "ℹ️ About"])
    
    with tab1:
        st.header("Job Search")
        
        # Search controls
        col1, col2, col3 = st.columns([2, 2, 1])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_jobspy = st.checkbox("🚀 JobSpy (Recommended)", value=True, help="Advanced multi-site scraper: Indeed, LinkedIn, Glassdoor, ZipRecruiter")
        with col2:
            search_indeed = st.checkbox("Search Indeed", value=False, help="Our custom Indeed scraper (may face blocking)")
        with col3:
            search_linkedin = st.checkbox("Search LinkedIn", value=False, help="Our custom LinkedIn scraper (may face blocking)")
        with col4:
            search_alternatives = st.checkbox("Alternative Sources", value=False, help="RemoteOK, AngelCo, and curated flexible jobs")
        
        # JobSpy site selection (only show if JobSpy is selected)
        if search_jobspy:
            st.subheader("🔧 JobSpy Settings")
            col1, col2 = st.columns(2)
            with col1:
                jobspy_sites = st.multiselect(
                    "Select Job Sites for JobSpy",
                    options=['indeed', 'linkedin', 'glassdoor', 'zip_recruiter', 'google'],
                    default=['indeed', 'linkedin', 'glassdoor'],
                    help="Choose which job sites JobSpy should search"
                )
            with col2:
                jobspy_max_results = st.slider(
                    "Max Results per Site",
                    min_value=5,
                    max_value=100,
                    value=20,
                    help="Maximum number of jobs to fetch per site"
                )
        
        search_button = st.button("🔍 Search Jobs", type="primary")
        
        if search_button:
            if not job_title or not location:
                st.error("Please provide job title and location!")
                return
            
            # Check if at least one search option is selected
            if not any([search_jobspy, search_indeed, search_linkedin, search_alternatives]):
                st.error("Please select at least one search method!")
                return
            
            # Initialize job filter
            job_filter = JobFilter()
            
            # Search progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Calculate progress steps
            search_methods = []
            if search_jobspy: search_methods.append("jobspy")
            if search_indeed: search_methods.append("indeed")
            if search_linkedin: search_methods.append("linkedin")
            if search_alternatives: search_methods.append("alternatives")
            
            total_steps = len(search_methods)
            current_step = 0
            
            # Search JobSpy (Recommended)
            if search_jobspy:
                current_step += 1
                status_text.text("🚀 Searching with JobSpy (Advanced Multi-Site Scraper)...")
                try:
                    if not jobspy_sites:
                        st.warning("⚠️ No JobSpy sites selected. Using default sites.")
                        jobspy_sites = ['indeed', 'linkedin']
                    
                    jobspy_wrapper = JobSpyWrapper()
                    jobspy_jobs = jobspy_wrapper.search_jobs(
                        job_title=job_title,
                        location=location, 
                        sites=jobspy_sites,
                        max_results=jobspy_max_results
                    )
                    filtered_jobspy_jobs = job_filter.filter_jobs(jobspy_jobs)
                    if 'jobspy' not in st.session_state.jobs_data:
                        st.session_state.jobs_data['jobspy'] = []
                    st.session_state.jobs_data['jobspy'] = filtered_jobspy_jobs
                    progress_bar.progress(int((current_step / total_steps) * 100))
                    
                    if len(filtered_jobspy_jobs) == 0:
                        st.warning("⚠️ JobSpy search returned no results. Try different search terms or locations.")
                    else:
                        st.success(f"🎉 JobSpy found {len(filtered_jobspy_jobs)} jobs from {len(jobspy_sites)} sites!")
                        
                except Exception as e:
                    st.error(f"❌ Error with JobSpy: {str(e)}")
                    if 'jobspy' not in st.session_state.jobs_data:
                        st.session_state.jobs_data['jobspy'] = []
                    st.session_state.jobs_data['jobspy'] = []
            
            # Search Indeed (Custom Scraper)
            if search_indeed:
                current_step += 1
                status_text.text("Searching Indeed (Custom Scraper)...")
                try:
                    indeed_scraper = IndeedScraper()
                    indeed_jobs = indeed_scraper.search_jobs(job_title, location)
                    filtered_indeed_jobs = job_filter.filter_jobs(indeed_jobs)
                    if 'indeed' not in st.session_state.jobs_data:
                        st.session_state.jobs_data['indeed'] = []
                    st.session_state.jobs_data['indeed'] = filtered_indeed_jobs
                    progress_bar.progress(int((current_step / total_steps) * 100))
                    
                    if len(filtered_indeed_jobs) == 0:
                        st.warning("⚠️ Custom Indeed scraper returned no results. This is expected due to anti-bot measures.")
                        st.info("💡 Tip: Use JobSpy instead for reliable Indeed access.")
                    else:
                        st.success(f"✅ Custom Indeed scraper found {len(filtered_indeed_jobs)} jobs")
                        
                except Exception as e:
                    st.error(f"❌ Error with custom Indeed scraper: {str(e)}")
                    st.info("💡 Tip: JobSpy provides more reliable Indeed access.")
                    if 'indeed' not in st.session_state.jobs_data:
                        st.session_state.jobs_data['indeed'] = []
                    st.session_state.jobs_data['indeed'] = []
            
            # Search LinkedIn (Custom Scraper)
            if search_linkedin:
                current_step += 1
                status_text.text("Searching LinkedIn (Custom Scraper)...")
                try:
                    linkedin_bot = LinkedInBot()
                    linkedin_jobs = linkedin_bot.search_jobs(job_title, location)
                    filtered_linkedin_jobs = job_filter.filter_jobs(linkedin_jobs)
                    if 'linkedin' not in st.session_state.jobs_data:
                        st.session_state.jobs_data['linkedin'] = []
                    st.session_state.jobs_data['linkedin'] = filtered_linkedin_jobs
                    progress_bar.progress(int((current_step / total_steps) * 100))
                    
                    if len(filtered_linkedin_jobs) == 0:
                        st.warning("⚠️ Custom LinkedIn scraper returned no results. This is expected due to anti-bot measures.")
                        st.info("💡 Tip: Use JobSpy instead for reliable LinkedIn access.")
                    else:
                        st.success(f"✅ Custom LinkedIn scraper found {len(filtered_linkedin_jobs)} jobs")
                        
                except Exception as e:
                    st.error(f"❌ Error with custom LinkedIn scraper: {str(e)}")
                    st.info("💡 Tip: JobSpy provides more reliable LinkedIn access.")
                    if 'linkedin' not in st.session_state.jobs_data:
                        st.session_state.jobs_data['linkedin'] = []
                    st.session_state.jobs_data['linkedin'] = []
            
            # Search Alternative Sources
            if search_alternatives:
                current_step += 1
                status_text.text("Searching alternative sources...")
                try:
                    alt_aggregator = AlternativeJobAggregator()
                    alt_jobs = alt_aggregator.search_all_sources(job_title, location)
                    filtered_alt_jobs = job_filter.filter_jobs(alt_jobs)
                    if 'alternatives' not in st.session_state.jobs_data:
                        st.session_state.jobs_data['alternatives'] = []
                    st.session_state.jobs_data['alternatives'] = filtered_alt_jobs
                    progress_bar.progress(int((current_step / total_steps) * 100))
                    
                    if len(filtered_alt_jobs) == 0:
                        st.warning("⚠️ Alternative sources search returned no results.")
                    else:
                        st.success(f"✅ Found {len(filtered_alt_jobs)} jobs from alternative sources")
                        
                except Exception as e:
                    st.error(f"❌ Error searching alternative sources: {str(e)}")
                    st.session_state.jobs_data['alternatives'] = []
            
            # Perform AI matching if resume is available
            if st.session_state.resume_path and st.session_state.resume_parsed:
                status_text.text("🤖 Performing AI resume matching...")
                try:
                    # Collect all jobs
                    all_jobs = []
                    for job_source, jobs in st.session_state.jobs_data.items():
                        for job in jobs:
                            job['search_source'] = job_source
                            all_jobs.append(job)
                    
                    if all_jobs:
                        # Perform resume matching
                        matcher = JobResumeMatcher()
                        top_matches = matcher.get_top_matches(
                            st.session_state.resume_path, 
                            all_jobs, 
                            top_n=min(len(all_jobs), 10)
                        )
                        
                        # Update jobs with match scores
                        for match_data in top_matches:
                            job_data = match_data['job_data']
                            job_data['match_score'] = match_data['match_score']
                            job_data['match_percentage'] = match_data['match_percentage']
                            job_data['match_quality'] = match_data['match_quality']
                            job_data['key_factors'] = match_data['key_factors']
                        
                        st.session_state.matched_jobs = top_matches
                        st.success(f"🎯 AI matching completed! Analyzed {len(all_jobs)} jobs")
                    
                except Exception as e:
                    st.warning(f"⚠️ AI matching failed: {str(e)}")
            
            status_text.text("Search completed!")
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
        
        # Display results
        any_results = any([
            st.session_state.jobs_data.get('jobspy', []),
            st.session_state.jobs_data.get('indeed', []),
            st.session_state.jobs_data.get('linkedin', []), 
            st.session_state.jobs_data.get('alternatives', [])
        ])
        
        if any_results:
            st.header("Search Results")
            
            # Results summary
            jobspy_count = len(st.session_state.jobs_data.get('jobspy', []))
            indeed_count = len(st.session_state.jobs_data.get('indeed', []))
            linkedin_count = len(st.session_state.jobs_data.get('linkedin', []))
            alternatives_count = len(st.session_state.jobs_data.get('alternatives', []))
            total_count = jobspy_count + indeed_count + linkedin_count + alternatives_count
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("🚀 JobSpy", jobspy_count, help="Multi-site scraper results")
            with col2:
                st.metric("📰 Indeed", indeed_count, help="Custom scraper results")
            with col3:
                st.metric("💼 LinkedIn", linkedin_count, help="Custom scraper results")
            with col4:
                st.metric("🌐 Alternatives", alternatives_count, help="Alternative sources")
            with col5:
                st.metric("📊 Total", total_count, help="All jobs combined")
            
            # Display JobSpy jobs (prioritized)
            jobspy_jobs = st.session_state.jobs_data.get('jobspy', [])
            if jobspy_jobs:
                st.subheader("🚀 JobSpy Results (Multi-Site)")
                st.info("✨ These results come from JobSpy's advanced scraping across multiple job boards")
                for i, job in enumerate(jobspy_jobs):
                    display_job_card(job, 'jobspy', i)
            
            # Display Indeed jobs
            indeed_jobs = st.session_state.jobs_data.get('indeed', [])
            if indeed_jobs:
                st.subheader("📰 Indeed Jobs (Custom Scraper)")
                for i, job in enumerate(indeed_jobs):
                    display_job_card(job, 'indeed', i)
            
            # Display LinkedIn jobs
            linkedin_jobs = st.session_state.jobs_data.get('linkedin', [])
            if linkedin_jobs:
                st.subheader("💼 LinkedIn Jobs (Custom Scraper)")
                for i, job in enumerate(linkedin_jobs):
                    display_job_card(job, 'linkedin', i)
            
            # Display Alternative jobs
            alternative_jobs = st.session_state.jobs_data.get('alternatives', [])
            if alternative_jobs:
                st.subheader("🌐 Alternative Sources")
                for i, job in enumerate(alternative_jobs):
                    display_job_card(job, 'alternatives', i)
    
    with tab2:
        st.header("🤖 AI-Powered Job Matching")
        
        if not st.session_state.resume_path:
            st.warning("⚠️ Please upload your resume first to use AI job matching features.")
            st.info("💡 Upload your resume in the sidebar to unlock intelligent job matching, ATS scoring, and bias detection.")
            return
        
        if not st.session_state.resume_parsed:
            st.error("❌ Resume parsing failed. Please try uploading your resume again.")
            return
        
        # Resume analysis summary
        with st.expander("📄 Resume Analysis Summary", expanded=True):
            parsed_resume = st.session_state.resume_parsed
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Characters Extracted", f"{parsed_resume.get('cleaned_text_length', 0):,}")
            with col2:
                sections_count = len([k for k, v in parsed_resume.get('sections', {}).items() if v])
                st.metric("Resume Sections", sections_count)
            with col3:
                tech_skills = parsed_resume.get('sections', {}).get('technical_skills', '')
                tech_count = len(tech_skills.split(',')) if tech_skills else 0
                st.metric("Tech Skills Found", tech_count)
            
            if parsed_resume.get('sections', {}).get('technical_skills'):
                st.markdown("**🔧 Detected Technical Skills:**")
                st.write(parsed_resume['sections']['technical_skills'])
        
        # AI Job Search with broad tech focus
        st.subheader("🎯 AI-Powered Technology Job Search")
        st.info("This search uses our specialized tech job scraper with intelligent resume matching across multiple domains.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            ai_location = st.selectbox(
                "Location for AI Search", 
                options=[
                    "Port Elizabeth, Eastern Cape, South Africa",
                    "East London, Eastern Cape, South Africa", 
                    "Grahamstown, Eastern Cape, South Africa",
                    "Cape Town, South Africa",
                    "Johannesburg, South Africa",
                    "Durban, South Africa",
                    "Remote"
                ],
                index=0,
                help="Select your preferred location for tech jobs"
            )
        with col2:
            ai_max_results = st.slider("Max Results", 10, 100, 30, help="Number of jobs to analyze")
        with col3:
            include_remote = st.checkbox("Include International Remote Jobs", value=True, help="Search for remote tech positions worldwide")
        
        # Job category selection
        st.markdown("**🎯 Select Job Categories:**")
        job_categories = st.multiselect(
            "Choose tech job categories to search",
            options=['software_developer', 'data_science', 'devops_cloud', 'cybersecurity', 'it_support', 
                    'product_management', 'qa_testing', 'ui_ux_design', 'network_engineering'],
            default=['software_developer', 'it_support', 'data_science'],
            help="Select multiple categories for broader search coverage"
        )
        
        if st.button("🚀 Start AI Job Search & Matching", type="primary"):
            if not job_categories:
                st.warning("⚠️ Please select at least one job category to search.")
            else:
                with st.spinner("🤖 AI-powered job search and resume matching in progress..."):
                    try:
                        # Use the specialized Technology scraper
                        tech_scraper = TechJobScraper()
                        tech_jobs = tech_scraper.fetch_tech_jobs(
                            location=ai_location,
                            job_categories=job_categories,
                            results_per_site=ai_max_results // 4,
                            include_remote=include_remote
                        )
                        
                        if tech_jobs:
                            category_names = [cat.replace('_', ' ').title() for cat in job_categories]
                            st.success(f"✅ Found {len(tech_jobs)} technology jobs across {', '.join(category_names)}")
                            
                            # Perform intelligent matching
                            matcher = JobResumeMatcher()
                            matched_jobs = matcher.get_top_matches(
                                st.session_state.resume_path,
                                tech_jobs,
                                top_n=min(len(tech_jobs), 15)
                            )
                            
                            st.session_state.matched_jobs = matched_jobs
                            st.success(f"🎯 Resume matching completed! Found {len(matched_jobs)} ranked matches")
                            
                        else:
                            category_names = [cat.replace('_', ' ').title() for cat in job_categories]
                            st.warning(f"⚠️ No jobs found for {', '.join(category_names)}. Try adjusting your search criteria or selecting different categories.")
                            
                    except Exception as e:
                        st.error(f"❌ AI job search failed: {str(e)}")
        
        # Display matched jobs if available
        if st.session_state.matched_jobs:
            st.subheader("🏆 Top Job Matches for Your Resume")
            
            # Matching summary
            total_matches = len(st.session_state.matched_jobs)
            excellent_matches = len([m for m in st.session_state.matched_jobs if m['match_score'] >= 0.8])
            good_matches = len([m for m in st.session_state.matched_jobs if 0.6 <= m['match_score'] < 0.8])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Matches", total_matches)
            with col2:
                st.metric("Excellent Matches", excellent_matches, help="80%+ match score")
            with col3:
                st.metric("Good Matches", good_matches, help="60-79% match score")
            with col4:
                avg_score = sum(m['match_score'] for m in st.session_state.matched_jobs) / len(st.session_state.matched_jobs)
                st.metric("Avg Match Score", f"{avg_score:.1%}")
            
            # Display top matches
            for i, match_data in enumerate(st.session_state.matched_jobs):
                job_data = match_data['job_data']
                
                # Add match information to job data for display
                job_data['match_score'] = match_data['match_score']
                job_data['match_percentage'] = match_data['match_percentage'] 
                job_data['match_quality'] = match_data['match_quality']
                job_data['key_factors'] = match_data['key_factors']
                
                # Display using enhanced job card
                display_job_card(job_data, 'ai_match', i)
        
        # Resume optimization suggestions
        if st.session_state.matched_jobs:
            st.subheader("📈 Resume Optimization Insights")
            
            # Analyze missing keywords across all matched jobs
            all_missing_keywords = {}
            for match_data in st.session_state.matched_jobs[:5]:  # Top 5 matches
                job_data = match_data['job_data']
                try:
                    ats_analyzer = ATSAnalyzer()
                    job_text = ats_analyzer.extract_job_text(job_data)
                    resume_text = get_resume_text_for_matching(st.session_state.resume_path)
                    missing_kw = ats_analyzer.identify_missing_keywords(job_text, resume_text)
                    
                    for kw_data in missing_kw:
                        keyword = kw_data['keyword']
                        if keyword in all_missing_keywords:
                            all_missing_keywords[keyword] += kw_data['importance']
                        else:
                            all_missing_keywords[keyword] = kw_data['importance']
                            
                except Exception:
                    continue
            
            if all_missing_keywords:
                # Sort by frequency/importance
                sorted_missing = sorted(all_missing_keywords.items(), key=lambda x: x[1], reverse=True)
                
                st.markdown("**🔍 Most Frequently Missing Keywords (Top 10):**")
                missing_display = [f"**{kw}** ({score})" for kw, score in sorted_missing[:10]]
                st.write(" • ".join(missing_display))
                
                st.info("💡 Consider adding these skills to your resume if you have experience with them.")

    with tab3:
        st.header("Application History")
        
        if st.session_state.applications:
            df = pd.DataFrame(st.session_state.applications)
            
            # Display summary metrics
            total_applications = len(df)
            recent_applications = len(df[df['applied_date'].str.contains(datetime.now().strftime("%Y-%m-%d"))])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Applications", total_applications)
            with col2:
                st.metric("Today's Applications", recent_applications)
            
            # Display applications table
            st.subheader("Application Details")
            
            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                company_filter = st.selectbox("Filter by Company", ["All"] + list(df['company'].unique()))
            with col2:
                status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
            
            # Apply filters
            filtered_df = df.copy()
            if company_filter != "All":
                filtered_df = filtered_df[filtered_df['company'] == company_filter]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            # Display filtered results
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "job_url": st.column_config.LinkColumn("Job URL"),
                    "applied_date": st.column_config.DatetimeColumn("Applied Date")
                }
            )
            
            # Download applications as CSV
            if st.button("📥 Download Applications CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"job_applications_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No applications yet. Start searching and applying to jobs!")
    
    with tab4:
        st.header("About Auto Apply for Tech Jobs")
        
        # Troubleshooting section first
        with st.expander("🔧 Troubleshooting & Recommendations", expanded=False):
            st.markdown("""
            ### ✅ Recommended: Use JobSpy
            - **Best Option**: Enable "🚀 JobSpy (Recommended)" for reliable results
            - **Why**: Professional anti-blocking technology and multi-site support
            - **Coverage**: Indeed, LinkedIn, Glassdoor, ZipRecruiter, Google Jobs
            - **Reliability**: Bypasses most bot detection systems
            
            ### Custom Scraper Issues
            #### Indeed Search Issues (403 Forbidden)
            - **Problem**: Indeed blocks automated requests from custom scrapers
            - **Solution**: Use JobSpy instead - it has better anti-blocking
            - **Workaround**: Sample data is provided when custom scrapers fail
            
            #### LinkedIn/Playwright Issues
            - **Problem**: Browser initialization errors with custom LinkedIn scraper
            - **Solution**: Use JobSpy for LinkedIn access, or install Playwright:
            ```bash
            pip install playwright
            playwright install
            ```
            
            ### General Tips
            - **Primary**: Always try JobSpy first for best results
            - **Secondary**: Use custom scrapers as backup sources
            - **Location**: Use broader terms (e.g., "Remote" instead of specific cities)
            - **Terms**: Try variations like "IT Support", "Help Desk", "Desktop Support"
            - **Sites**: Select multiple JobSpy sites for maximum coverage
            """)
        
        st.markdown("""
        This application helps you automatically search and apply for IT support jobs from multiple sources using advanced scraping technology.
        
        ### 🚀 Features:
        - **🤖 AI-Powered Resume Matching**: Intelligent TF-IDF analysis to rank jobs by compatibility with your resume
        - **📊 ATS Keyword Scoring**: Analyze how well your resume matches Applicant Tracking System requirements
        - **🔍 Bias Detection**: Identify potentially biased language in job postings for inclusive job targeting
        - **🎯 JobSpy Integration**: Professional-grade multi-site scraper (Indeed, LinkedIn, Glassdoor, ZipRecruiter, Google Jobs)
        - **🛡️ Anti-blocking Technology**: Bypasses rate limiting and bot detection
        - **🔧 Smart IT Support Filtering**: Specialized filtering for IT Support, Helpdesk, and Desktop Support roles
        - **⚡ Auto-apply**: Automatically apply to LinkedIn jobs with your uploaded resume
        - **📈 Resume Optimization**: Get suggestions on missing keywords to improve your resume
        - **📋 ATS Report Downloads**: Export detailed analysis reports in JSON and TXT formats
        - **📊 Application tracking**: Keep track of all your applications in one place
        - **💼 Resume management**: Upload, parse, and analyze your resume automatically
        - **🌐 Multiple sources**: Custom scrapers + alternative job boards
        
        ### 📋 How to use:
        1. **Configure settings** in the sidebar:
           - Enter your desired job title and location
           - Provide your LinkedIn credentials for auto-apply
           - **Upload your resume (PDF or DOCX format)** - This unlocks AI features!
        
        2. **Choose your search method**:
                       - **🤖 AI Job Matching Tab**: Use specialized technology job search with intelligent resume matching across multiple tech domains
           - **🔍 Search Jobs Tab**: Traditional multi-source job search with optional AI enhancements
        
        3. **Analyze and optimize**:
           - Review AI match scores and ATS compatibility for each job
           - Download detailed ATS reports with missing keywords and bias analysis
           - Use resume optimization insights to improve your profile
        
        4. **Apply strategically**:
           - Focus on high-match jobs (80%+ compatibility)
           - Click "Auto Apply" on LinkedIn jobs for instant applications
           - Monitor your applications in the Applications tab
        
        ### ⚠️ Important Notes:
        - LinkedIn credentials are only stored in your browser session
        - Auto-apply works only for LinkedIn "Easy Apply" jobs
        - Always review job requirements before applying
        - Be respectful of application limits on job platforms
        
        ### 🔧 Technical Requirements:
        - Python 3.8+
        - Streamlit
        - BeautifulSoup4
        - Playwright
        - Pandas
        """)
        
        # System status
        st.subheader("🔧 System Status")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Resume Status:**")
            if st.session_state.resume_path:
                st.success("✅ Resume uploaded")
            else:
                st.warning("⚠️ No resume uploaded")
        
        with col2:
            st.write("**LinkedIn Status:**")
            if st.session_state.linkedin_email and st.session_state.linkedin_password:
                st.success("✅ Credentials provided")
            else:
                st.warning("⚠️ No credentials provided")

if __name__ == "__main__":
    main() 