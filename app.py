import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import os
from datetime import datetime
import time
from pathlib import Path
import requests

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
            "model": "mixtral-8x7b-32768",
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

def search_jobs(job_title, location, job_type, keywords):
    """Search for jobs using multiple scrapers"""
    all_jobs = []
    
    # JobSpy Search
    try:
        with st.spinner("Searching JobSpy (LinkedIn, Indeed, ZipRecruiter, Glassdoor)..."):
            jobspy_wrapper = JobSpyWrapper()
            jobspy_jobs = jobspy_wrapper.search_jobs(
                job_title=job_title,
                location=location,
                sites=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                max_results=20
            )
            if jobspy_jobs:
                st.session_state.jobs_data['jobspy'] = jobspy_jobs
                all_jobs.extend(jobspy_jobs)
                st.success(f"✅ JobSpy: Found {len(jobspy_jobs)} jobs (from LinkedIn and other sources)")
            else:
                st.info("ℹ️ JobSpy: No jobs found - some sites may be blocking requests")
    except Exception as e:
        st.warning(f"⚠️ JobSpy: Search encountered an issue, continuing with other sources...")
        with st.expander("JobSpy Error Details"):
            st.write(str(e))
    
    # Indeed is already covered by JobSpy (which successfully searches Indeed + LinkedIn + others)
    # Removed standalone Indeed scraper due to consistent blocking and slow performance
    # Alternative Sources
    try:
        with st.spinner("Searching enhanced APIs (RemoteOK, Adzuna, Jooble, AngelCo, FlexJobs)..."):
            alt_aggregator = AlternativeJobAggregator()
            alt_jobs = alt_aggregator.search_all_sources(job_title, location, max_per_source=10)
            if alt_jobs:
                st.session_state.jobs_data['alternatives'] = alt_jobs
                all_jobs.extend(alt_jobs)
                st.success(f"✅ Alternative Sources: Found {len(alt_jobs)} jobs")
            else:
                st.info("ℹ️ Alternative Sources: No matching jobs found")
    except Exception as e:
        st.warning(f"⚠️ Alternative Sources: Search encountered an issue...")
        with st.expander("Alternative Sources Error Details"):
            st.write(str(e))
    
    return all_jobs

def display_job_card(job, source):
    """Display a job card with apply functionality"""
    # Add source indicator
    source_icon = {
        'jobspy': '<i class="fa fa-rocket"></i>',
        'linkedin': '<i class="fa fa-linkedin"></i>', 
        'alternatives': '<i class="fa fa-globe"></i>'
    }
    
    source_name = job.get('source', source.title())
    title_prefix = f"{source_icon.get(source, '<i class=\"fa fa-clipboard\"></i>')} [{source_name}]"
    
    # Get job details
    title = job.get('title', 'N/A')
    company = job.get('company', 'N/A')
    location = job.get('location', 'N/A')
    date_posted = job.get('date_posted', job.get('posted_date', 'N/A'))
    
    # Display job card
    st.markdown(f"""
    <div style='border:1px solid #eee; padding:15px; border-radius:10px; margin-bottom:15px; background-color: #f9f9f9;'>
        <h5><i class='fa fa-briefcase'></i> {title}</h5>
        <p><i class='fa fa-building'></i> <strong>{company}</strong></p>
        <p><i class='fa fa-map-marker-alt'></i> {location} | <i class='fa fa-clock'></i> {date_posted}</p>
        <p><i class='fa fa-tag'></i> {title_prefix}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Apply button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Apply", key=f"apply_{job.get('id', hash(str(job)))}"):
            apply_to_job(job, source)
    
    with col2:
        if st.button("Analyze", key=f"analyze_{job.get('id', hash(str(job)))}"):
            analyze_job(job)

def apply_to_job(job, source):
    """Apply to a job and track the application"""
    try:
        # Create application record
        application = {
            'job_title': job.get('title', 'N/A'),
            'company': job.get('company', 'N/A'),
            'location': job.get('location', 'N/A'),
            'source': source,
            'applied_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Applied',
            'job_url': job.get('job_url', job.get('url', 'N/A'))
        }
        
        # Add to session state
        st.session_state.applications.append(application)
        
        # Save to file
        save_applications_to_csv()
        
        st.success(f"Applied to {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
        
    except Exception as e:
        st.error(f"Error applying to job: {str(e)}")

def analyze_job(job):
    """Analyze job compatibility with resume"""
    if not st.session_state.resume_path:
        st.warning("Please upload a resume first in the Resume Check section")
        return
    
    try:
        # Generate ATS report
        ats_report = generate_ats_report_for_job(job, st.session_state.resume_path)
        
        if ats_report:
            st.success("ATS Analysis Complete!")
            
            # Display analysis results
            with st.expander("ATS Analysis Results"):
                st.write("**Match Score:**", f"{ats_report.get('match_score', 0)}%")
                st.write("**Missing Keywords:**", ", ".join(ats_report.get('missing_keywords', [])))
                st.write("**Matched Keywords:**", ", ".join(ats_report.get('matched_keywords', [])))
                
                if 'suggestions' in ats_report:
                    st.write("**Improvement Suggestions:**")
                    for suggestion in ats_report['suggestions']:
                        st.write(f"• {suggestion}")
        else:
            st.error("Failed to generate ATS analysis")
            
    except Exception as e:
        st.error(f"Error analyzing job: {str(e)}")

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
        
        if jobs:
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem 0; background: #d4edda; border-radius: 8px; margin: 1rem 0;'>
                <h4><i class="fa fa-check-circle" style="color: #155724;"></i> Found {len(jobs)} Jobs Total</h4>
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
            for i, job in enumerate(jobs):
                source = job.get('source', 'unknown')
                display_job_card(job, source)
                
        else:
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
                    st.metric("Words", len(parsed_data.get('cleaned_text', '').split()))
                
                # AI Analysis
                st.markdown("### <i class='fa fa-robot'></i> AI Analysis & Suggestions", unsafe_allow_html=True)
                
                if st.button("Generate AI Suggestions", use_container_width=True):
                    with st.spinner("Analyzing resume..."):
                        try:
                            resume_text = parsed_data.get('cleaned_text', '')
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
    
    # Skills input form
    with st.form("ai_form"):
        skills = st.text_area(
            "Describe your skills, experience, and career goals:",
            placeholder="e.g. I have 3 years of IT support experience, skilled in Windows, networking, troubleshooting...",
            height=150
        )
        
        focus_area = st.selectbox(
            "Focus Area",
            ["IT Support", "Software Development", "Data Analysis", "Cybersecurity", "DevOps", "General Tech"]
        )
        
        submitted = st.form_submit_button("Generate Job Matches", use_container_width=True)

    if submitted and skills:
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
                
                st.markdown("### <i class='fa fa-bullseye'></i> Personalized Job Recommendations", unsafe_allow_html=True)
                st.write(recommendations)
                
                # Additional AI-powered suggestions
                if st.button("Get Interview Preparation Tips"):
                    with st.spinner("Generating interview tips..."):
                        interview_prompt = f"""
                        Based on this profile for {focus_area} roles, provide specific interview preparation tips:
                        
                        Skills: {skills}
                        
                        Include:
                        1. Technical questions to expect
                        2. Projects to mention
                        3. Skills to demonstrate
                        4. Common interview scenarios
                        5. Questions to ask the interviewer
                        """
                        
                        interview_tips = query_groq(interview_prompt)
                        
                        st.markdown("### <i class='fa fa-handshake'></i> Interview Preparation", unsafe_allow_html=True)
                        st.write(interview_tips)
                        
            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")

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
    <p> JOBscraper | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True) 