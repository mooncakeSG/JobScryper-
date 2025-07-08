"""
Integration tests for complete Auto Applyer workflows.

Tests end-to-end functionality including job search, resume analysis,
AI recommendations, and application tracking.
"""

import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

# Import modules for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def sample_resume_file():
    """Create a temporary resume file for testing."""
    resume_content = """
    John Doe
    IT Support Specialist
    Email: john.doe@email.com
    Phone: +27 11 123 4567
    
    Professional Summary:
    Experienced IT Support Specialist with 3+ years in help desk operations,
    system administration, and user support. Proven expertise in Windows
    environments, Active Directory, and Office 365.
    
    Technical Skills:
    - Windows 10/11, Windows Server 2019
    - Active Directory, Group Policy
    - Office 365, Exchange Online
    - ServiceNow, Remote Desktop
    - TCP/IP, DNS, DHCP
    - PowerShell basics
    
    Work Experience:
    IT Support Technician | ABC Company | 2021-2024
    - Provided technical support for 300+ users
    - Managed Active Directory user accounts
    - Resolved hardware/software issues (95% success rate)
    - Supported Office 365 migration
    
    Help Desk Analyst | XYZ Corp | 2020-2021
    - Handled support tickets via multiple channels
    - Maintained knowledge base documentation
    - Achieved 98% customer satisfaction
    
    Education:
    Bachelor of Information Technology | UCT | 2019
    
    Certifications:
    - CompTIA A+ (2020)
    - Microsoft 365 Fundamentals (2022)
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(resume_content)
        yield f.name
    
    # Cleanup
    try:
        os.unlink(f.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_jobs_dataframe():
    """Sample jobs data as would be returned from JobSpy."""
    return pd.DataFrame([
        {
            'title': 'IT Support Specialist',
            'company': 'TechCorp Inc.',
            'location': 'Cape Town, South Africa',
            'description': 'Seeking IT Support Specialist with Windows 10, Active Directory, and Office 365 experience. Must have help desk background and troubleshooting skills.',
            'job_url': 'https://example.com/job/1',
            'site': 'linkedin',
            'date_posted': '2025-01-08',
            'salary_min': 25000,
            'salary_max': 35000,
            'job_type': 'Full-time'
        },
        {
            'title': 'Senior Help Desk Analyst',
            'company': 'DataCorp Ltd.',
            'location': 'Johannesburg, South Africa',
            'description': 'Senior help desk position requiring ITIL certification, ServiceNow experience, and 5+ years support experience.',
            'job_url': 'https://example.com/job/2',
            'site': 'indeed',
            'date_posted': '2025-01-07',
            'salary_min': 30000,
            'salary_max': 40000,
            'job_type': 'Full-time'
        },
        {
            'title': 'Desktop Support Technician',
            'company': 'SupportCorp',
            'location': 'Remote',
            'description': 'Remote desktop support role. Windows 10/11 expertise required. Hardware troubleshooting and user training.',
            'job_url': 'https://example.com/job/3',
            'site': 'glassdoor',
            'date_posted': '2025-01-06',
            'salary_min': 22000,
            'salary_max': 28000,
            'job_type': 'Contract'
        },
        {
            'title': 'Marketing Manager',
            'company': 'AdCorp',
            'location': 'Cape Town, South Africa',
            'description': 'Marketing manager position requiring digital marketing experience.',
            'job_url': 'https://example.com/job/4',
            'site': 'linkedin',
            'date_posted': '2025-01-05',
            'salary_min': 35000,
            'salary_max': 45000,
            'job_type': 'Full-time'
        }
    ])


@pytest.mark.integration
class TestCompleteJobSearchWorkflow:
    """Test the complete job search workflow."""
    
    @patch('jobspy.scrape_jobs')
    def test_end_to_end_job_search(self, mock_jobspy, sample_jobs_dataframe):
        """Test complete job search from JobSpy to filtered results."""
        # Mock JobSpy response
        mock_jobspy.return_value = sample_jobs_dataframe
        
        try:
            from jobspy_wrapper import JobSpyWrapper
            from filters import filter_it_jobs
            
            # Step 1: Search for jobs using JobSpy wrapper
            wrapper = JobSpyWrapper()
            raw_jobs = wrapper.search_jobs(
                site_name='linkedin',
                search_term='IT Support',
                location='Cape Town'
            )
            
            # Step 2: Convert to format for filtering
            jobs_list = raw_jobs.to_dict('records')
            
            # Step 3: Filter for IT jobs
            filtered_jobs = filter_it_jobs(jobs_list)
            
            # Verify the workflow
            assert isinstance(raw_jobs, pd.DataFrame)
            assert len(raw_jobs) == 4  # Original sample data
            
            assert isinstance(filtered_jobs, list)
            assert len(filtered_jobs) > 0
            assert len(filtered_jobs) < len(jobs_list)  # Should filter out marketing job
            
            # Check that filtered jobs have relevance scores
            for job in filtered_jobs:
                assert 'relevance_score' in job
                assert isinstance(job['relevance_score'], (int, float))
                assert job['relevance_score'] >= 0
            
            # Check that jobs are sorted by relevance
            if len(filtered_jobs) > 1:
                scores = [job['relevance_score'] for job in filtered_jobs]
                assert scores == sorted(scores, reverse=True)
            
            # Verify that non-IT jobs are filtered out
            job_titles = [job['title'] for job in filtered_jobs]
            assert 'Marketing Manager' not in job_titles
            
        except ImportError:
            pytest.skip("Required modules not available")
    
    @patch('requests.get')
    @patch('jobspy.scrape_jobs')
    def test_multiple_source_integration(self, mock_jobspy, mock_requests, sample_jobs_dataframe):
        """Test integration of multiple job sources."""
        try:
            from jobspy_wrapper import JobSpyWrapper
            from alternative_sources import get_remote_ok_jobs, get_adzuna_jobs
            from filters import filter_it_jobs
            
            # Mock JobSpy
            mock_jobspy.return_value = sample_jobs_dataframe
            
            # Mock alternative sources
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {
                    'id': '123',
                    'position': 'Remote IT Support',
                    'company': 'RemoteCompany',
                    'location': 'Remote',
                    'description': 'Remote IT support with cloud experience',
                    'url': 'https://remoteok.io/jobs/123'
                }
            ]
            mock_requests.return_value = mock_response
            
            # Search multiple sources
            wrapper = JobSpyWrapper()
            jobspy_results = wrapper.search_jobs('linkedin', 'IT Support', 'Cape Town')
            
            remote_ok_jobs = get_remote_ok_jobs('IT Support', limit=10)
            
            # Combine and process results
            all_jobs = jobspy_results.to_dict('records')
            if remote_ok_jobs:
                all_jobs.extend(remote_ok_jobs)
            
            filtered_jobs = filter_it_jobs(all_jobs)
            
            # Verify integration
            assert len(all_jobs) >= len(jobspy_results)
            assert len(filtered_jobs) > 0
            
            # Check for jobs from different sources
            sources = set()
            for job in filtered_jobs:
                if 'source' in job:
                    sources.add(job['source'])
                elif 'site' in job:
                    sources.add(job['site'])
            
            assert len(sources) > 0  # Should have jobs from at least one source
            
        except ImportError:
            pytest.skip("Required modules not available")


@pytest.mark.integration
class TestResumeAnalysisWorkflow:
    """Test the complete resume analysis workflow."""
    
    def test_end_to_end_resume_analysis(self, sample_resume_file, sample_jobs_dataframe):
        """Test complete resume analysis from file to AI recommendations."""
        try:
            from resume_parser import parse_resume_from_file
            from matcher import JobResumeMatcher
            from ats_report import ATSAnalyzer
            
            # Step 1: Parse resume
            resume_data = parse_resume_from_file(sample_resume_file)
            
            # Step 2: Match with jobs
            matcher = JobResumeMatcher()
            jobs_list = sample_jobs_dataframe.to_dict('records')
            matches = matcher.get_top_matches(sample_resume_file, jobs_list, top_n=3)
            
            # Step 3: Generate ATS report for best match
            if matches:
                best_job = matches[0]
                analyzer = ATSAnalyzer()
                ats_report = analyzer.generate_ats_report(best_job, sample_resume_file)
            
            # Verify the workflow
            assert 'text' in resume_data
            assert 'sections' in resume_data
            assert len(resume_data['text']) > 0
            
            assert isinstance(matches, list)
            assert len(matches) > 0
            assert len(matches) <= 3
            
            # Check match structure
            for match in matches:
                assert 'title' in match
                assert 'company' in match
                assert 'match_percentage' in match
                assert 'match_quality' in match
                assert 0 <= match['match_percentage'] <= 100
            
            # Check ATS report structure
            if matches:
                assert 'ats_analysis' in ats_report
                assert 'missing_keywords' in ats_report
                assert 'keyword_density' in ats_report
                assert 0 <= ats_report['ats_analysis']['ats_score'] <= 100
            
        except ImportError:
            pytest.skip("Required modules not available")
    
    @patch('groq_resume_suggestion.create_groq_client')
    def test_ai_powered_resume_analysis(self, mock_create_client, sample_resume_file, sample_jobs_dataframe):
        """Test AI-powered resume analysis workflow."""
        try:
            from groq_resume_suggestion import generate_resume_suggestions_groq
            from resume_parser import parse_resume_from_file
            
            # Mock Groq client
            mock_client = MagicMock()
            mock_create_client.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({
                "fit_summary": "Good match for IT support role",
                "missing_keywords": ["ITIL", "Azure", "PowerShell"],
                "improvement_suggestions": ["Get ITIL certification", "Learn Azure"],
                "strengths": ["Windows experience", "Help desk background"],
                "match_percentage": 75
            })
            mock_response.usage.total_tokens = 1200
            mock_client.chat.completions.create.return_value = mock_response
            
            # Parse resume
            resume_data = parse_resume_from_file(sample_resume_file)
            
            # Get first IT job from sample data
            it_jobs = [job for job in sample_jobs_dataframe.to_dict('records') 
                      if 'IT' in job['title'] or 'Help Desk' in job['title']]
            
            if it_jobs:
                # Generate AI suggestions
                suggestions = generate_resume_suggestions_groq(resume_data['text'], it_jobs[0])
                
                # Verify AI analysis
                assert suggestions['success'] is True
                assert 'suggestions' in suggestions
                assert 'api_usage' in suggestions
                
                ai_suggestions = suggestions['suggestions']
                assert 'fit_summary' in ai_suggestions
                assert 'missing_keywords' in ai_suggestions
                assert 'improvement_suggestions' in ai_suggestions
                assert 'match_percentage' in ai_suggestions
                
                assert isinstance(ai_suggestions['missing_keywords'], list)
                assert isinstance(ai_suggestions['improvement_suggestions'], list)
                assert 0 <= ai_suggestions['match_percentage'] <= 100
            
        except ImportError:
            pytest.skip("Required modules not available")


@pytest.mark.integration
class TestApplicationTrackingWorkflow:
    """Test the application tracking workflow."""
    
    def test_application_lifecycle(self, sample_jobs_dataframe):
        """Test complete application lifecycle from search to tracking."""
        try:
            # Mock application tracking functions
            applications = []
            
            def track_application(job_data, status="Applied"):
                """Mock application tracking function."""
                application = {
                    'job_title': job_data['title'],
                    'company': job_data['company'],
                    'location': job_data['location'],
                    'source': job_data.get('site', 'Unknown'),
                    'applied_date': '2025-01-08 10:30:00',
                    'status': status,
                    'job_url': job_data['job_url'],
                    'salary': f"R{job_data.get('salary_min', 0)} - R{job_data.get('salary_max', 0)}"
                }
                applications.append(application)
                return application
            
            # Simulate applying to jobs
            jobs_list = sample_jobs_dataframe.to_dict('records')
            it_jobs = [job for job in jobs_list if 'IT' in job['title'] or 'Help Desk' in job['title']]
            
            # Track applications
            for job in it_jobs[:2]:  # Apply to first 2 IT jobs
                track_application(job)
            
            # Update application status
            if applications:
                applications[0]['status'] = 'Interview Scheduled'
                applications[0]['interview_date'] = '2025-01-15 14:00:00'
            
            # Verify application tracking
            assert len(applications) == 2
            
            for app in applications:
                assert 'job_title' in app
                assert 'company' in app
                assert 'status' in app
                assert 'applied_date' in app
                assert app['status'] in ['Applied', 'Interview Scheduled']
            
            # Check status updates
            interview_apps = [app for app in applications if app['status'] == 'Interview Scheduled']
            assert len(interview_apps) == 1
            assert 'interview_date' in interview_apps[0]
            
        except Exception as e:
            pytest.fail(f"Application tracking test failed: {e}")


@pytest.mark.integration
class TestStreamlitIntegration:
    """Test Streamlit app integration (mocked)."""
    
    @patch('streamlit.session_state')
    @patch('streamlit.file_uploader')
    @patch('streamlit.selectbox')
    @patch('streamlit.text_input')
    @patch('streamlit.button')
    def test_streamlit_workflow_simulation(self, mock_button, mock_text_input, 
                                          mock_selectbox, mock_file_uploader, 
                                          mock_session_state, sample_resume_file,
                                          sample_jobs_dataframe):
        """Test simulated Streamlit workflow."""
        try:
            # Mock Streamlit session state
            mock_session_state.return_value = {
                'jobs_data': {'jobspy': [], 'alternatives': []},
                'applications': [],
                'resume_path': None,
                'current_jobs': []
            }
            
            # Mock file upload
            mock_file = Mock()
            mock_file.name = 'test_resume.pdf'
            mock_file.read.return_value = b'PDF content'
            mock_file_uploader.return_value = mock_file
            
            # Mock form inputs
            mock_text_input.side_effect = ['IT Support', 'Cape Town']
            mock_selectbox.return_value = 'linkedin'
            mock_button.return_value = True
            
            # Simulate the workflow that would happen in Streamlit
            
            # 1. User uploads resume
            uploaded_file = mock_file_uploader()
            if uploaded_file:
                resume_path = sample_resume_file  # Use our test file
                mock_session_state()['resume_path'] = resume_path
            
            # 2. User enters search criteria
            job_title = mock_text_input()
            location = mock_text_input()
            source = mock_selectbox()
            
            # 3. User clicks search button
            if mock_button():
                # Simulate job search
                with patch('jobspy.scrape_jobs') as mock_jobspy:
                    mock_jobspy.return_value = sample_jobs_dataframe
                    
                    from jobspy_wrapper import JobSpyWrapper
                    from filters import filter_it_jobs
                    
                    wrapper = JobSpyWrapper()
                    jobs = wrapper.search_jobs(source, job_title, location)
                    filtered_jobs = filter_it_jobs(jobs.to_dict('records'))
                    
                    # Store in session state
                    mock_session_state()['jobs_data']['jobspy'] = filtered_jobs
                    mock_session_state()['current_jobs'] = filtered_jobs
            
            # 4. Generate AI recommendations if resume is uploaded
            if mock_session_state()['resume_path'] and mock_session_state()['current_jobs']:
                # This would trigger AI analysis in the real app
                pass
            
            # Verify the workflow
            assert uploaded_file is not None
            assert job_title == 'IT Support'
            assert location == 'Cape Town'
            assert source == 'linkedin'
            
            # Verify that jobs were processed
            jobs_data = mock_session_state()['jobs_data']['jobspy']
            assert len(jobs_data) > 0
            
        except ImportError:
            pytest.skip("Required modules not available")


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across the complete workflow."""
    
    def test_graceful_error_handling(self, sample_resume_file):
        """Test that the system handles errors gracefully throughout the workflow."""
        try:
            from utils.errors import handle_errors, ErrorContext
            from utils.validation import validate_job_search
            
            # Test with invalid inputs
            with pytest.raises(Exception):  # Should raise validation error
                validate_job_search({'job_title': '', 'location': 'Cape Town'})
            
            # Test error context manager
            with ErrorContext("Test Operation", show_spinner=False) as ctx:
                # Simulate an operation that fails
                raise ValueError("Test error")
            
            assert ctx.error_occurred
            
            # Test error handling decorator
            @handle_errors(
                operation_name="Test Job Search",
                show_user_error=False,
                default_return_value=[]
            )
            def failing_job_search():
                raise ConnectionError("Network error")
            
            result = failing_job_search()
            assert result == []  # Should return default value
            
        except ImportError:
            pytest.skip("Error handling modules not available")


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance of integrated workflows."""
    
    def test_complete_workflow_performance(self, sample_resume_file, sample_jobs_dataframe):
        """Test performance of complete workflow with realistic data."""
        import time
        
        try:
            start_time = time.time()
            
            # Simulate complete workflow
            with patch('jobspy.scrape_jobs') as mock_jobspy:
                mock_jobspy.return_value = sample_jobs_dataframe
                
                from jobspy_wrapper import JobSpyWrapper
                from filters import filter_it_jobs
                from matcher import JobResumeMatcher
                from resume_parser import parse_resume_from_file
                
                # Job search
                wrapper = JobSpyWrapper()
                jobs = wrapper.search_jobs('linkedin', 'IT Support', 'Cape Town')
                
                # Filter jobs
                filtered_jobs = filter_it_jobs(jobs.to_dict('records'))
                
                # Resume analysis
                resume_data = parse_resume_from_file(sample_resume_file)
                
                # Job matching
                matcher = JobResumeMatcher()
                matches = matcher.get_top_matches(sample_resume_file, filtered_jobs, top_n=3)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Should complete within reasonable time
            assert total_time < 10.0  # 10 seconds for complete workflow
            
            # Verify results
            assert len(filtered_jobs) > 0
            assert len(matches) > 0
            assert 'text' in resume_data
            
        except ImportError:
            pytest.skip("Required modules not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 