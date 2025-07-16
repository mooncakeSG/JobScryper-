"""
Auto Applyer - Enhanced UI Pages

Individual page components for the enhanced Streamlit interface with
database integration, modern design, and comprehensive functionality.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
import time

# Import database components
from database.connection import init_database, get_database_manager
from database.utilities import DatabaseUtils
from database.models import ApplicationStatus, User, JobApplication

# Import existing modules
from jobspy_wrapper import JobSpyWrapper
from alternative_sources import AlternativeJobAggregator
from resume_parser import ResumeParser
from matcher import JobResumeMatcher
from ats_report import ATSAnalyzer
from groq_resume_suggestion import generate_resume_suggestions_groq

# Import UI components
from ui.components import (
    create_app_header, create_quick_action_nav, create_metric_card, create_job_card, create_status_badge,
    create_progress_bar, create_alert, create_stats_chart, create_data_table,
    create_export_buttons, create_loading_spinner, create_empty_state, clean_html_text
)

from utils.errors import handle_errors, ErrorContext


class AuthenticationPage:
    """User authentication and onboarding page."""
    
    @staticmethod
    def render():
        """Render the authentication page."""
        create_app_header(
            "Auto Applyer", 
            "Your AI-Powered Job Application Assistant"
        )
        
        # Check if database is initialized
        try:
            init_database("development")
        except Exception as e:
            create_alert(f"Database initialization failed: {e}", "error")
            return
        
        tab1, tab2 = st.tabs(["🚀 Get Started", "👤 Existing User"])
        
        with tab1:
            st.markdown("### Welcome to Auto Applyer!")
            st.markdown("""
            Get started with your personalized job search experience:
            - **AI-Powered Job Matching** - Find jobs that match your skills
            - **Resume Analysis** - Get ATS optimization suggestions  
            - **Application Tracking** - Monitor your job search progress
            - **Interview Preparation** - AI-generated interview tips
            """)
            
            with st.form("user_signup"):
                st.markdown("#### Create Your Profile")
                
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name*", placeholder="John")
                    email = st.text_input("Email*", placeholder="john@example.com")
                    location = st.text_input("Location", placeholder="Cape Town, South Africa")
                
                with col2:
                    last_name = st.text_input("Last Name*", placeholder="Doe")
                    job_title = st.text_input("Current/Target Job Title", placeholder="IT Support Specialist")
                    experience_years = st.number_input("Years of Experience", min_value=0, max_value=50, value=2)
                
                # Skills input
                skills_input = st.text_area(
                    "Key Skills (comma-separated)", 
                    placeholder="Windows 10, Active Directory, Office 365, Help Desk, Networking",
                    help="Enter your key skills separated by commas"
                )
                
                submitted = st.form_submit_button("🚀 Create Profile & Start", use_container_width=True)
                
                if submitted:
                    if not all([first_name, last_name, email]):
                        create_alert("Please fill in all required fields (marked with *)", "error")
                    else:
                        try:
                            # Parse skills
                            skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()] if skills_input else []
                            
                            # Create user
                            user = DatabaseUtils.create_user(
                                email=email,
                                first_name=first_name,
                                last_name=last_name,
                                location=location,
                                job_title=job_title,
                                experience_years=experience_years,
                                skills=skills
                            )
                            
                            # Store in session state
                            st.session_state.user_id = user.id
                            st.session_state.user_data = user.to_dict()
                            st.session_state.authenticated = True
                            
                            create_alert("Profile created successfully! Welcome to Auto Applyer! 🎉", "success")
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as e:
                            if "already exists" in str(e):
                                create_alert("An account with this email already exists. Please use the 'Existing User' tab.", "warning")
                            else:
                                create_alert(f"Error creating profile: {e}", "error")
        
        with tab2:
            st.markdown("### Welcome Back!")
            
            with st.form("user_login"):
                email = st.text_input("Email Address", placeholder="your.email@example.com")
                submitted = st.form_submit_button("🔑 Continue", use_container_width=True)
                
                if submitted and email:
                    user = DatabaseUtils.get_user_by_email(email)
                    if user:
                        st.session_state.user_id = user.id
                        st.session_state.user_data = user.to_dict()
                        st.session_state.authenticated = True
                        
                        create_alert(f"Welcome back, {user.first_name}! 👋", "success")
                        time.sleep(1)
                        st.rerun()
                    else:
                        create_alert("No account found with this email. Please create a new profile.", "error")
        
        # Demo account option
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🧪 Try Demo Account", use_container_width=True, help="Use demo@autoapplyer.com"):
                demo_user = DatabaseUtils.get_user_by_email("demo@autoapplyer.com")
                if demo_user:
                    st.session_state.user_id = demo_user.id
                    st.session_state.user_data = demo_user.to_dict()
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    create_alert("Demo account not found. Please run database initialization.", "error")


class DashboardPage:
    """Main dashboard with overview and quick actions."""
    
    @staticmethod
    def render():
        """Render the dashboard page."""
        user_data = st.session_state.get('user_data', {})
        user_id = st.session_state.get('user_id')
        
        create_app_header(
            "Dashboard", 
            "Your Job Search Overview",
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
                    icon="fa fa-paper-plane"
                )
            
            with col2:
                create_metric_card(
                    "This Month", 
                    str(stats.get('recent_applications', 0)),
                    icon="fa fa-calendar"
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
                    f"{stats.get('interview_rate', 0)}%",
                    icon="fa fa-chart-line"
                )
        
        except Exception as e:
            create_alert(f"Error loading statistics: {e}", "error")
            # Show default metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                create_metric_card("Total Applications", "0", icon="fa fa-paper-plane")
            with col2:
                create_metric_card("This Month", "0", icon="fa fa-calendar")
            with col3:
                create_metric_card("Interviews", "0", icon="fa fa-handshake")
            with col4:
                create_metric_card("Success Rate", "0%", icon="fa fa-chart-line")
        
        st.markdown("---")
        
        # Quick Actions Navigation
        create_quick_action_nav([
            {"label": "Search Jobs", "target": "Job Search"},
            {"label": "Upload Resume", "target": "Resume Manager"},
            {"label": "AI Matching", "target": "AI Assistant"},
            {"label": "View Analytics", "target": "Analytics"}
        ])
        
        # Recent Applications
        st.markdown("### 📋 Recent Applications")
        
        try:
            recent_apps = DatabaseUtils.get_user_applications(user_id, limit=5)
            
            if recent_apps:
                for app in recent_apps:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{app.job_title}**")
                        st.markdown(f"*{app.company}*")
                    
                    with col2:
                        st.markdown(f"📍 {app.location}")
                        st.markdown(f"💰 {app.salary_range}")
                    
                    with col3:
                        st.markdown(create_status_badge(app.status.value), unsafe_allow_html=True)
                        st.markdown(f"📅 {app.application_date.strftime('%Y-%m-%d')}")
                    
                    with col4:
                        if st.button("View", key=f"view_app_{app.id}"):
                            st.session_state.selected_application = app.id
                            st.session_state.page = "Applications"
                            st.rerun()
                    
                    st.markdown("---")
            else:
                create_empty_state(
                    "No Applications Yet",
                    "Start your job search to see your applications here",
                    "Search Jobs",
                    "📋"
                )
        
        except Exception as e:
            create_alert(f"Error loading recent applications: {e}", "error")
        
        # Job Search Trends (placeholder for future implementation)
        st.markdown("### 📈 Search Trends")
        
        # Create sample trend data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        trend_data = pd.DataFrame({
            'date': dates,
            'searches': [i % 5 + 1 for i in range(len(dates))],
            'applications': [max(0, (i % 5) - 1) for i in range(len(dates))]
        })
        
        fig = px.line(
            trend_data, 
            x='date', 
            y=['searches', 'applications'],
            title="Job Search Activity (Last 30 Days)",
            labels={'value': 'Count', 'variable': 'Activity Type'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


class JobSearchPage:
    """Enhanced job search page with multiple sources and filtering."""
    
    @staticmethod
    def render():
        """Render the job search page."""
        user_data = st.session_state.get('user_data', {})
        user_id = st.session_state.get('user_id')
        
        create_app_header(
            "Job Search", 
            "Find Your Next Opportunity"
        )
        
        # Search Form
        with st.expander("🔍 Search Parameters", expanded=True):
            with st.form("enhanced_search_form"):
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
                        ["Any", "Full-time", "Part-time", "Contract", "Internship"]
                    )
                    experience_level = st.selectbox(
                        "Experience Level",
                        ["Any", "Entry Level", "Mid Level", "Senior Level", "Executive"]
                    )
                    salary_min = st.number_input(
                        "Minimum Salary (ZAR)", 
                        min_value=0, 
                        value=0, 
                        step=5000
                    )
                
                # Advanced options
                with st.expander("⚙️ Advanced Options"):
                    col1, col2 = st.columns(2)
                    with col1:
                        max_results = st.slider("Max Results per Source", 10, 100, 50)
                        include_remote = st.checkbox("Include Remote Jobs", value=True)
                    with col2:
                        sources = st.multiselect(
                            "Job Sources",
                            ["JobSpy", "LinkedIn", "Indeed", "Alternative APIs"],
                            default=["JobSpy", "Alternative APIs"]
                        )
                
                search_submitted = st.form_submit_button("🔍 Search Jobs", use_container_width=True)
        
        # Perform Search
        if search_submitted and job_title:
            with st.spinner("Searching for jobs across multiple platforms..."):
                try:
                    # Record search in database
                    DatabaseUtils.add_search_history(
                        user_id=user_id,
                        job_title=job_title,
                        location=location,
                        keywords=keywords,
                        sources_searched=sources,
                        max_results=max_results
                    )
                    
                    # Perform search using existing modules
                    all_jobs = []
                    
                    if "JobSpy" in sources:
                        # Use JobSpy wrapper
                        jobspy = JobSpyWrapper()
                        jobspy_jobs = jobspy.search_jobs(
                            job_title=job_title,
                            location=location,
                            job_type=job_type.lower() if job_type != "Any" else None,
                            results_wanted=max_results
                        )
                        for job in jobspy_jobs:
                            job['source'] = 'JobSpy'
                        all_jobs.extend(jobspy_jobs)
                    
                    if "Alternative APIs" in sources:
                        # Use alternative sources
                        alt_aggregator = AlternativeJobAggregator()
                        alt_jobs = alt_aggregator.search_all_sources(
                            job_title=job_title,
                            location=location,
                            max_results=max_results
                        )
                        all_jobs.extend(alt_jobs)
                    
                    # Store results in session state
                    st.session_state.search_results = all_jobs
                    st.session_state.last_search = {
                        'job_title': job_title,
                        'location': location,
                        'keywords': keywords,
                        'job_type': job_type,
                        'sources': sources,
                        'timestamp': datetime.now()
                    }
                    
                    create_alert(f"Found {len(all_jobs)} jobs from {len(sources)} sources", "success")
                
                except Exception as e:
                    create_alert(f"Search error: {e}", "error")
                    st.session_state.search_results = []
        
        # Display Results
        if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
            jobs = st.session_state.search_results
            
            # Filters and sorting
            st.markdown("### 🎯 Search Results")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                company_filter = st.multiselect(
                    "Filter by Company",
                    options=list(set([job.get('company', 'Unknown') for job in jobs])),
                    key="company_filter"
                )
            
            with col2:
                source_filter = st.multiselect(
                    "Filter by Source", 
                    options=list(set([job.get('source', 'Unknown') for job in jobs])),
                    key="source_filter"
                )
            
            with col3:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Date Posted", "Company", "Match Score"],
                    key="sort_by"
                )
            
            # Apply filters
            filtered_jobs = jobs
            
            if company_filter:
                filtered_jobs = [job for job in filtered_jobs if job.get('company') in company_filter]
            
            if source_filter:
                filtered_jobs = [job for job in filtered_jobs if job.get('source') in source_filter]
            
            # Display filtered results
            st.markdown(f"**Showing {len(filtered_jobs)} of {len(jobs)} jobs**")
            
            # Check user's existing applications
            user_applications = DatabaseUtils.get_user_applications(user_id)
            applied_jobs = {(app.job_title, app.company) for app in user_applications}
            
            for i, job in enumerate(filtered_jobs[:20]):  # Limit to 20 for performance
                job_key = (job.get('title', ''), job.get('company', ''))
                user_applied = job_key in applied_jobs
                
                action = create_job_card(job, show_actions=True, user_applied=user_applied)
                
                if action == "apply" and not user_applied:
                    # Add to applications
                    try:
                        DatabaseUtils.add_job_application(
                            user_id=user_id,
                            job_title=job.get('title', ''),
                            company=job.get('company', ''),
                            location=job.get('location', ''),
                            job_description=job.get('description', ''),
                            job_url=job.get('job_url', ''),
                            source=job.get('source', ''),
                            salary_min=None,  # Parse from job data if available
                            salary_max=None,
                            job_type=job.get('job_type', ''),
                            status=ApplicationStatus.APPLIED
                        )
                        
                        create_alert("Application submitted successfully! 🎉", "success")
                        time.sleep(1)
                        st.rerun()
                        
                    except Exception as e:
                        create_alert(f"Error submitting application: {e}", "error")
                
                elif action == "analyze":
                    st.session_state.selected_job_for_analysis = job
                    st.session_state.page = "AI Assistant"
                    st.rerun()
                
                elif action == "view_details":
                    with st.expander(f"📄 Job Details - {job.get('title', 'Unknown')}", expanded=True):
                        st.markdown(f"**Company:** {job.get('company', 'Unknown')}")
                        st.markdown(f"**Location:** {job.get('location', 'Unknown')}")
                        st.markdown(f"**Posted:** {job.get('date_posted', 'Unknown')}")
                        st.markdown(f"**Source:** {job.get('source', 'Unknown')}")
                        
                        if job.get('salary'):
                            st.markdown(f"**Salary:** {job.get('salary')}")
                        
                        if job.get('job_url'):
                            st.markdown(f"**Apply Link:** [{job.get('job_url')}]({job.get('job_url')})")
                        
                        st.markdown("**Description:**")
                        # Clean HTML from description
                        raw_desc = job.get('description', 'No description available')
                        if raw_desc and raw_desc != 'No description available':
                            clean_desc = clean_html_text(raw_desc)
                            st.markdown(clean_desc)
                        else:
                            st.markdown(raw_desc)
        
        elif hasattr(st.session_state, 'last_search'):
            create_empty_state(
                "No Jobs Found",
                "Try adjusting your search criteria or keywords",
                "Search Again",
                "🔍"
            )
        
        else:
            create_empty_state(
                "Start Your Job Search",
                "Enter your job title and preferences to find opportunities",
                icon="🚀"
            )


class ApplicationsPage:
    """Application tracking and management page."""
    
    @staticmethod
    def render():
        """Render the applications page."""
        user_id = st.session_state.get('user_id')
        
        create_app_header(
            "My Applications", 
            "Track Your Job Application Progress"
        )
        
        # Load applications
        try:
            applications = DatabaseUtils.get_user_applications(user_id)
            
            if applications:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                total_apps = len(applications)
                pending_apps = len([app for app in applications if app.status == ApplicationStatus.PENDING])
                interview_apps = len([app for app in applications if app.status in [ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.INTERVIEWED]])
                success_rate = (interview_apps / total_apps * 100) if total_apps > 0 else 0
                
                with col1:
                    create_metric_card("Total Applications", str(total_apps), icon="fa fa-paper-plane")
                with col2:
                    create_metric_card("Pending", str(pending_apps), icon="fa fa-clock")
                with col3:
                    create_metric_card("Interviews", str(interview_apps), icon="fa fa-handshake")
                with col4:
                    create_metric_card("Success Rate", f"{success_rate:.1f}%", icon="fa fa-chart-line")
                
                st.markdown("---")
                
                # Filters
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status_filter = st.multiselect(
                        "Filter by Status",
                        options=[status.value for status in ApplicationStatus],
                        key="app_status_filter"
                    )
                
                with col2:
                    company_filter = st.multiselect(
                        "Filter by Company",
                        options=list(set([app.company for app in applications])),
                        key="app_company_filter"
                    )
                
                with col3:
                    date_range = st.selectbox(
                        "Time Period",
                        ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
                        key="app_date_filter"
                    )
                
                # Apply filters
                filtered_apps = applications
                
                if status_filter:
                    filtered_apps = [app for app in filtered_apps if app.status.value in status_filter]
                
                if company_filter:
                    filtered_apps = [app for app in filtered_apps if app.company in company_filter]
                
                if date_range != "All Time":
                    days_back = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[date_range]
                    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
                    filtered_apps = [app for app in filtered_apps if app.application_date >= cutoff_date]
                
                # Display applications
                st.markdown(f"### 📋 Applications ({len(filtered_apps)})")
                
                for app in filtered_apps:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**{app.job_title}**")
                            st.markdown(f"*{app.company}*")
                            if app.match_score:
                                st.markdown(f"🎯 Match: {app.match_score}%")
                        
                        with col2:
                            st.markdown(f"📍 {app.location}")
                            st.markdown(f"📅 {app.application_date.strftime('%Y-%m-%d')}")
                        
                        with col3:
                            st.markdown(create_status_badge(app.status.value), unsafe_allow_html=True)
                            if app.salary_min or app.salary_max:
                                st.markdown(f"💰 {app.salary_range}")
                        
                        with col4:
                            if st.button("✏️ Edit", key=f"edit_app_{app.id}"):
                                st.session_state.editing_application = app.id
                                st.rerun()
                        
                        # Edit form (if editing this application)
                        if st.session_state.get('editing_application') == app.id:
                            with st.form(f"edit_form_{app.id}"):
                                new_status = st.selectbox(
                                    "Status",
                                    options=[status.value for status in ApplicationStatus],
                                    index=list(ApplicationStatus).index(app.status)
                                )
                                
                                notes = st.text_area(
                                    "Notes",
                                    value=app.interview_notes or app.follow_up_notes or ""
                                )
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.form_submit_button("💾 Save"):
                                        try:
                                            DatabaseUtils.update_application_status(
                                                app.id,
                                                ApplicationStatus(new_status),
                                                notes=notes
                                            )
                                            st.session_state.editing_application = None
                                            create_alert("Application updated successfully!", "success")
                                            st.rerun()
                                        except Exception as e:
                                            create_alert(f"Error updating application: {e}", "error")
                                
                                with col2:
                                    if st.form_submit_button("❌ Cancel"):
                                        st.session_state.editing_application = None
                                        st.rerun()
                        
                        st.markdown("---")
                
                # Export functionality
                if filtered_apps:
                    st.markdown("### 📤 Export Applications")
                    
                    # Convert to DataFrame for export
                    export_data = []
                    for app in filtered_apps:
                        export_data.append({
                            'Job Title': app.job_title,
                            'Company': app.company,
                            'Location': app.location,
                            'Status': app.status.value,
                            'Application Date': app.application_date.strftime('%Y-%m-%d'),
                            'Match Score': app.match_score,
                            'Salary Range': app.salary_range,
                            'Source': app.source,
                            'Notes': app.interview_notes or app.follow_up_notes or ''
                        })
                    
                    df = pd.DataFrame(export_data)
                    create_export_buttons(df, "applications")
            
            else:
                create_empty_state(
                    "No Applications Yet",
                    "Start applying to jobs to track your progress here",
                    "Search Jobs",
                    "📋"
                )
                
                if st.button("🔍 Search Jobs"):
                    st.session_state.page = "Job Search"
                    st.rerun()
        
        except Exception as e:
            create_alert(f"Error loading applications: {e}", "error") 