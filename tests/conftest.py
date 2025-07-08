"""
Test fixtures and configuration for Auto Applyer test suite.

This module provides shared fixtures, utilities, and configuration
for all tests in the Auto Applyer application.
"""

import pytest
import tempfile
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
import pandas as pd

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test data constants
SAMPLE_JOB_DATA = {
    "title": "IT Support Specialist",
    "company": "TechCorp Inc.",
    "location": "Cape Town, South Africa",
    "description": "We are seeking an experienced IT Support Specialist to join our team. "
                  "The ideal candidate will have experience with Windows 10, Active Directory, "
                  "Office 365, and help desk operations. Strong troubleshooting skills required.",
    "url": "https://example.com/job/123",
    "job_url": "https://example.com/job/123",
    "salary": "R25,000 - R35,000 per month",
    "posted_date": "2025-01-08",
    "source": "JobSpy",
    "remote": False,
    "easy_apply": True,
    "job_type": "Full-time",
    "company_url": "https://example.com/company/techcorp",
    "job_level": "Mid Level",
    "company_industry": "Information Technology"
}

SAMPLE_RESUME_TEXT = """
John Doe
IT Support Specialist

Contact Information:
Email: john.doe@email.com
Phone: +27 11 123 4567
Location: Johannesburg, South Africa

Professional Summary:
Experienced IT Support Specialist with 5+ years in help desk operations, 
system administration, and user support. Proven track record in Windows 
environments, Active Directory management, and Office 365 administration.

Work Experience:
Senior IT Support Technician | ABC Company | 2020-2023
- Provided Level 2 technical support for 500+ users
- Managed Active Directory user accounts and group policies
- Administered Office 365 environment including Exchange Online
- Resolved hardware and software issues with 95% success rate
- Trained junior support staff on troubleshooting procedures

IT Help Desk Analyst | XYZ Corp | 2018-2020
- Handled Level 1 support tickets via phone, email, and chat
- Supported Windows 10 deployment and migration project
- Maintained ITIL-based ticketing system (ServiceNow)
- Achieved 98% customer satisfaction rating

Technical Skills:
- Operating Systems: Windows 10/11, Windows Server 2016/2019
- Cloud Services: Office 365, Azure AD, Exchange Online
- Networking: TCP/IP, DNS, DHCP, VPN
- Tools: Active Directory, Group Policy, PowerShell, SCCM
- Ticketing: ServiceNow, Remedy, Jira Service Desk
- Hardware: Desktop/laptop repair, printer configuration

Certifications:
- CompTIA A+ (2018)
- Microsoft 365 Certified: Fundamentals (2021)
- ITIL Foundation v4 (2019)

Education:
Bachelor of Information Technology
University of the Witwatersrand | 2017
"""


# ==============================================================================
# Core Fixtures
# ==============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_job():
    """Provide a sample job posting for testing."""
    return SAMPLE_JOB_DATA.copy()


@pytest.fixture
def sample_jobs_list():
    """Provide a list of sample job postings."""
    jobs = []
    for i in range(3):
        job = SAMPLE_JOB_DATA.copy()
        job["title"] = f"IT Support Specialist {i+1}"
        job["company"] = f"Company {i+1}"
        job["url"] = f"https://example.com/job/{i+1}"
        jobs.append(job)
    return jobs


@pytest.fixture
def sample_resume_text():
    """Provide sample resume text for testing."""
    return SAMPLE_RESUME_TEXT


@pytest.fixture
def sample_resume_file(temp_dir, sample_resume_text):
    """Create a temporary resume file for testing."""
    resume_file = temp_dir / "test_resume.txt"
    resume_file.write_text(sample_resume_text, encoding='utf-8')
    return str(resume_file)


@pytest.fixture
def sample_pdf_resume(temp_dir):
    """Create a minimal PDF resume file for testing."""
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open()
        page = doc.new_page()
        text = SAMPLE_RESUME_TEXT
        page.insert_text((72, 72), text, fontsize=12)
        
        pdf_file = temp_dir / "test_resume.pdf"
        doc.save(str(pdf_file))
        doc.close()
        return str(pdf_file)
    except ImportError:
        # If PyMuPDF is not available, create a dummy file
        pdf_file = temp_dir / "test_resume.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<>>\nstartxref\n0\n%%EOF")
        return str(pdf_file)


@pytest.fixture
def assets_dir(temp_dir):
    """Create a temporary assets directory."""
    assets_path = temp_dir / "assets"
    assets_path.mkdir()
    return str(assets_path)


@pytest.fixture
def sample_applications():
    """Provide sample application data."""
    return [
        {
            "job_title": "IT Support Specialist",
            "company": "TechCorp Inc.",
            "location": "Cape Town",
            "source": "JobSpy",
            "applied_date": "2025-01-08 10:30:00",
            "status": "Applied",
            "job_url": "https://example.com/job/123",
            "easy_apply": True,
            "salary": "R25,000 - R35,000",
            "job_type": "Full-time"
        },
        {
            "job_title": "Help Desk Analyst",
            "company": "DataCorp Ltd.",
            "location": "Johannesburg",
            "source": "RemoteOK",
            "applied_date": "2025-01-07 15:45:00",
            "status": "Interview Scheduled",
            "job_url": "https://example.com/job/456",
            "easy_apply": False,
            "salary": "Not specified",
            "job_type": "Contract"
        }
    ]


# ==============================================================================
# Mock Fixtures
# ==============================================================================

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for testing."""
    with patch('streamlit.session_state') as mock_session_state:
        mock_session_state.return_value = {}
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.warning') as mock_warning, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.info') as mock_info, \
             patch('streamlit.spinner') as mock_spinner:
            
            yield {
                'session_state': mock_session_state,
                'error': mock_error,
                'warning': mock_warning,
                'success': mock_success,
                'info': mock_info,
                'spinner': mock_spinner
            }


@pytest.fixture
def mock_groq_client():
    """Mock Groq API client for testing."""
    mock_client = MagicMock()
    
    # Mock successful response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "fit_summary": "Strong match for IT Support role",
        "missing_keywords": ["Azure", "PowerShell", "ITIL"],
        "improvement_suggestions": [
            "Add Azure cloud experience",
            "Highlight PowerShell scripting skills"
        ],
        "strengths": ["Windows expertise", "Help desk experience"],
        "recommended_actions": ["Obtain Azure certification"]
    })
    mock_response.usage.total_tokens = 150
    
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_jobspy():
    """Mock JobSpy for testing."""
    mock_jobspy = MagicMock()
    
    # Create mock DataFrame
    jobs_data = pd.DataFrame([
        {
            'title': 'IT Support Specialist',
            'company': 'TechCorp',
            'location': 'Cape Town',
            'description': 'IT support role requiring Windows experience',
            'job_url': 'https://example.com/job/1',
            'site': 'linkedin',
            'date_posted': '2025-01-08',
            'salary': 'R30,000',
            'job_type': 'Full-time'
        }
    ])
    
    with patch('jobspy.scrape_jobs') as mock_scrape:
        mock_scrape.return_value = jobs_data
        yield mock_scrape


@pytest.fixture
def mock_requests():
    """Mock requests library for API testing."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": []}
        mock_response.text = '{"status": "success"}'
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'response': mock_response
        }


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch('builtins.open', create=True) as mock_open, \
         patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs:
        
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = SAMPLE_RESUME_TEXT
        
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'makedirs': mock_makedirs
        }


# ==============================================================================
# Database and State Fixtures
# ==============================================================================

@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state for testing."""
    return {
        'jobs_data': {'jobspy': [], 'alternatives': []},
        'applications': [],
        'resume_path': None,
        'current_jobs': [],
        'ai_skills': '',
        'ai_focus_area': 'IT Support',
        'ai_recommendations': None,
        'interview_tips': None
    }


@pytest.fixture
def populated_session_state(mock_session_state, sample_jobs_list, sample_applications):
    """Session state populated with test data."""
    mock_session_state['jobs_data']['jobspy'] = sample_jobs_list
    mock_session_state['applications'] = sample_applications
    mock_session_state['current_jobs'] = sample_jobs_list
    mock_session_state['resume_path'] = '/tmp/test_resume.pdf'
    return mock_session_state


# ==============================================================================
# Performance Testing Fixtures
# ==============================================================================

@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during tests."""
    start_time = datetime.now()
    memory_start = None
    
    try:
        import psutil
        process = psutil.Process()
        memory_start = process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        pass
    
    yield {
        'start_time': start_time,
        'memory_start': memory_start
    }
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    memory_end = None
    if memory_start is not None:
        try:
            memory_end = process.memory_info().rss / 1024 / 1024  # MB
        except:
            pass
    
    print(f"\n⏱️  Test duration: {duration:.2f}s")
    if memory_start and memory_end:
        memory_diff = memory_end - memory_start
        print(f"💾 Memory usage: {memory_start:.1f}MB → {memory_end:.1f}MB (Δ{memory_diff:+.1f}MB)")


# ==============================================================================
# Utility Functions
# ==============================================================================

@pytest.fixture
def test_utilities():
    """Provide test utility functions."""
    
    class TestUtils:
        @staticmethod
        def create_temp_file(content: str, suffix: str = ".txt", directory: Path = None) -> Path:
            """Create a temporary file with given content."""
            if directory is None:
                fd, path = tempfile.mkstemp(suffix=suffix)
                with os.fdopen(fd, 'w') as f:
                    f.write(content)
                return Path(path)
            else:
                file_path = directory / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"
                file_path.write_text(content, encoding='utf-8')
                return file_path
        
        @staticmethod
        def assert_job_structure(job_dict: dict):
            """Assert that a job dictionary has the expected structure."""
            required_fields = ['title', 'company', 'location', 'description']
            for field in required_fields:
                assert field in job_dict, f"Missing required field: {field}"
                assert job_dict[field] is not None, f"Field {field} is None"
                assert str(job_dict[field]).strip(), f"Field {field} is empty"
        
        @staticmethod
        def assert_error_response(response: dict):
            """Assert that an error response has the expected structure."""
            assert 'error' in response
            assert response['error'] is True or isinstance(response['error'], str)
            if 'error_type' in response:
                assert isinstance(response['error_type'], str)
            if 'timestamp' in response:
                assert isinstance(response['timestamp'], str)
        
        @staticmethod
        def create_mock_response(status_code: int = 200, json_data: dict = None, text: str = None):
            """Create a mock HTTP response."""
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.json.return_value = json_data or {}
            mock_response.text = text or json.dumps(json_data or {})
            mock_response.raise_for_status = MagicMock()
            if status_code >= 400:
                import requests
                mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
            return mock_response
    
    return TestUtils()


# ==============================================================================
# Environment Setup
# ==============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables and configuration."""
    # Set test environment variables
    monkeypatch.setenv('GROQ_API_KEY', 'test_groq_api_key')
    monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
    monkeypatch.setenv('TESTING', 'true')
    
    # Mock external dependencies that might not be available in test environment
    try:
        import utils.logging_config
    except ImportError:
        pass
    
    yield
    
    # Cleanup after test
    # Any cleanup code can go here


# ==============================================================================
# Markers and Categories
# ==============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Mark slow tests (tests that might take longer)
        if any(keyword in item.name.lower() for keyword in ['performance', 'load', 'stress']):
            item.add_marker(pytest.mark.slow) 