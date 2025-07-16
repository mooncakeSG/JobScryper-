"""
Unit tests for AI features including Groq integration and resume suggestions.

Tests the AI-powered features like resume analysis, job matching, and suggestions.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import os

# Import modules under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from groq_resume_suggestion import (
        generate_resume_suggestions_groq,
        GroqResumeAnalyzer,
        create_groq_client
    )
    from matcher import JobResumeMatcher, calculate_match_score
    from ats_report import ATSAnalyzer, calculate_ats_score
except ImportError as e:
    pytest.skip(f"Skipping AI feature tests due to import error: {e}", allow_module_level=True)


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    IT Support Specialist
    
    Professional Summary:
    Experienced IT Support Specialist with 3+ years in help desk operations and system administration.
    
    Technical Skills:
    - Windows 10/11, Windows Server 2019
    - Active Directory, Group Policy
    - Microsoft Office 365, Exchange Online
    - ServiceNow, Remote Desktop
    - TCP/IP networking, DNS, DHCP
    - PowerShell scripting basics
    
    Work Experience:
    IT Support Technician | ABC Company | 2021-2024
    - Provided Level 1 and Level 2 technical support for 300+ users
    - Managed user accounts in Active Directory
    - Resolved hardware and software issues with 95% success rate
    - Supported Office 365 migration project
    
    Help Desk Analyst | XYZ Corp | 2020-2021
    - Handled support tickets via phone, email, and chat
    - Documented solutions in knowledge base
    - Maintained 98% customer satisfaction rating
    
    Education:
    Bachelor of Information Technology | University of Cape Town | 2019
    
    Certifications:
    - CompTIA A+ (2020)
    - Microsoft 365 Fundamentals (2022)
    """


@pytest.fixture
def sample_job_posting():
    """Sample job posting for testing."""
    return {
        'title': 'Senior IT Support Specialist',
        'company': 'TechCorp Inc.',
        'location': 'Cape Town, South Africa',
        'description': """
        We are seeking a Senior IT Support Specialist to join our growing IT team.
        
        Key Requirements:
        - 5+ years of IT support experience
        - Advanced Windows 10/11 and Windows Server administration
        - Active Directory and Group Policy management
        - Office 365 administration including Exchange Online
        - ITIL certification preferred
        - Azure AD experience a plus
        - PowerShell scripting experience
        - Excellent troubleshooting and communication skills
        
        Responsibilities:
        - Provide Level 2/3 technical support
        - Manage Azure AD and on-premises Active Directory
        - Support Office 365 environment
        - Create and maintain PowerShell scripts
        - Mentor junior support staff
        - Participate in infrastructure projects
        
        Preferred Qualifications:
        - ITIL Foundation certification
        - Azure fundamentals certification
        - Experience with SCCM/Intune
        - VMware or Hyper-V experience
        """,
        'job_type': 'Full-time',
        'salary': 'R35,000 - R45,000 per month'
    }


@pytest.fixture
def mock_groq_response():
    """Mock Groq API response."""
    return {
        "fit_summary": "Good match for IT Support role with strong technical foundation. Candidate has relevant experience but lacks some senior-level requirements.",
        "missing_keywords": [
            "ITIL certification",
            "Azure AD",
            "SCCM",
            "Intune",
            "VMware",
            "PowerShell scripting (advanced)"
        ],
        "improvement_suggestions": [
            "Obtain ITIL Foundation certification to meet preferred qualifications",
            "Gain experience with Azure AD and cloud identity management",
            "Develop advanced PowerShell scripting skills",
            "Learn Microsoft SCCM/Intune for endpoint management",
            "Consider Azure Fundamentals certification",
            "Highlight any mentoring or leadership experience"
        ],
        "strengths": [
            "Solid Windows administration experience",
            "Active Directory and Group Policy knowledge",
            "Office 365 experience",
            "Help desk and user support background",
            "Good success rates and customer satisfaction"
        ],
        "recommended_actions": [
            "Enroll in ITIL Foundation course",
            "Set up Azure AD lab environment for hands-on experience",
            "Complete PowerShell scripting tutorials",
            "Highlight any project leadership or mentoring experience",
            "Update resume to emphasize cloud experience"
        ],
        "match_percentage": 75,
        "experience_gap": "2 years",
        "key_improvements": [
            "Obtain ITIL certification",
            "Gain Azure experience",
            "Develop advanced scripting skills"
        ]
    }


class TestGroqIntegration:
    """Test Groq API integration functionality."""
    
    def test_create_groq_client_with_api_key(self):
        """Test Groq client creation with API key."""
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key'}):
            with patch('groq.Groq') as mock_groq:
                client = create_groq_client()
                mock_groq.assert_called_once_with(api_key='test_api_key')
    
    def test_create_groq_client_no_api_key(self):
        """Test Groq client creation without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                create_groq_client()
            assert "GROQ_API_KEY environment variable is required" in str(exc_info.value)
    
    @patch('groq_resume_suggestion.create_groq_client')
    def test_groq_resume_analyzer_initialization(self, mock_create_client):
        """Test GroqResumeAnalyzer initialization."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        analyzer = GroqResumeAnalyzer()
        
        assert analyzer.client == mock_client
        mock_create_client.assert_called_once()
    
    @patch('groq_resume_suggestion.create_groq_client')
    def test_generate_suggestions_success(self, mock_create_client, sample_resume_text, sample_job_posting, mock_groq_response):
        """Test successful resume suggestion generation."""
        # Setup mock client
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(mock_groq_response)
        mock_response.usage.total_tokens = 1500
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test the function
        result = generate_resume_suggestions_groq(sample_resume_text, sample_job_posting)
        
        # Verify the result
        assert result['success'] is True
        assert 'suggestions' in result
        assert 'api_usage' in result
        
        suggestions = result['suggestions']
        assert suggestions['fit_summary'] == mock_groq_response['fit_summary']
        assert suggestions['missing_keywords'] == mock_groq_response['missing_keywords']
        assert suggestions['match_percentage'] == mock_groq_response['match_percentage']
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == "llama-3.3-70b-versatile"
        assert call_args[1]['temperature'] == 0.3
    
    @patch('groq_resume_suggestion.create_groq_client')
    def test_generate_suggestions_api_error(self, mock_create_client, sample_resume_text, sample_job_posting):
        """Test handling of Groq API errors."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = generate_resume_suggestions_groq(sample_resume_text, sample_job_posting)
        
        assert result['success'] is False
        assert 'error' in result
        assert "API Error" in result['error']
    
    @patch('groq_resume_suggestion.create_groq_client')
    def test_generate_suggestions_invalid_json(self, mock_create_client, sample_resume_text, sample_job_posting):
        """Test handling of invalid JSON response from Groq."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        # Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Invalid JSON content"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = generate_resume_suggestions_groq(sample_resume_text, sample_job_posting)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'JSON' in result['error'] or 'parse' in result['error']


class TestJobResumeMatcher:
    """Test job-resume matching functionality."""
    
    def test_matcher_initialization(self):
        """Test JobResumeMatcher initialization."""
        matcher = JobResumeMatcher()
        
        # Check that the matcher has been initialized with expected attributes
        assert hasattr(matcher, 'tfidf_vectorizer')
        assert hasattr(matcher, 'skills_keywords')
        assert hasattr(matcher, 'experience_keywords')
    
    def test_calculate_match_score_high_match(self, sample_resume_text, sample_job_posting):
        """Test match score calculation for a good match."""
        score = calculate_match_score(sample_resume_text, sample_job_posting['description'])
        
        # Should be a reasonable score since the resume matches the job requirements
        assert 0 <= score <= 100
        assert score > 50  # Should be a decent match
    
    def test_calculate_match_score_low_match(self, sample_job_posting):
        """Test match score calculation for a poor match."""
        unrelated_resume = """
        Jane Smith
        Marketing Manager
        
        Experience in social media marketing, content creation, and brand management.
        Skilled in Facebook Ads, Google Analytics, and email marketing campaigns.
        
        No technical or IT experience.
        """
        
        score = calculate_match_score(unrelated_resume, sample_job_posting['description'])
        
        # Should be a low score since marketing resume doesn't match IT job
        assert 0 <= score <= 100
        assert score < 30  # Should be a poor match
    
    def test_get_top_matches(self, sample_resume_text):
        """Test getting top job matches for a resume."""
        matcher = JobResumeMatcher()
        
        jobs = [
            {
                'title': 'IT Support Specialist',
                'description': 'Windows 10, Active Directory, Office 365 support required',
                'company': 'TechCorp'
            },
            {
                'title': 'Marketing Manager',
                'description': 'Social media marketing and brand management experience needed',
                'company': 'MarketCorp'
            },
            {
                'title': 'Senior IT Administrator',
                'description': 'Advanced Windows Server, PowerShell, and Azure experience required',
                'company': 'CloudCorp'
            }
        ]
        
        # Create a temporary file with the resume
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_resume_text)
            resume_path = f.name
        
        try:
            matches = matcher.get_top_matches(resume_path, jobs, top_n=2)
            
            assert len(matches) <= 2
            assert len(matches) > 0
            
            # Check that results are sorted by match percentage
            if len(matches) > 1:
                assert matches[0]['match_percentage'] >= matches[1]['match_percentage']
            
            # Check that IT jobs score higher than marketing job
            match_titles = [match['title'] for match in matches]
            assert 'Marketing Manager' not in match_titles or \
                   any('IT' in title for title in match_titles[:1])  # IT job should be first
        
        finally:
            os.unlink(resume_path)
    
    def test_extract_skills_from_text(self):
        """Test skill extraction from text."""
        matcher = JobResumeMatcher()
        
        text = "Experience with Python, JavaScript, SQL, AWS, Docker, and Kubernetes"
        skills = matcher.extract_skills(text)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        
        # Should find some of the mentioned technologies
        skills_lower = [skill.lower() for skill in skills]
        assert any('python' in skill for skill in skills_lower)
    
    def test_calculate_experience_level(self):
        """Test experience level calculation."""
        matcher = JobResumeMatcher()
        
        senior_text = "10+ years of experience, senior developer, team lead, architecture"
        junior_text = "recent graduate, entry level, 1 year experience"
        mid_text = "3 years experience, intermediate level skills"
        
        senior_level = matcher.calculate_experience_level(senior_text)
        junior_level = matcher.calculate_experience_level(junior_text)
        mid_level = matcher.calculate_experience_level(mid_text)
        
        assert senior_level > mid_level > junior_level
        assert all(0 <= level <= 10 for level in [senior_level, mid_level, junior_level])


class TestATSAnalyzer:
    """Test ATS (Applicant Tracking System) analysis functionality."""
    
    def test_ats_analyzer_initialization(self):
        """Test ATSAnalyzer initialization."""
        analyzer = ATSAnalyzer()
        
        assert hasattr(analyzer, 'keyword_extractor')
        assert hasattr(analyzer, 'bias_detector')
    
    def test_calculate_ats_score_good_match(self, sample_resume_text, sample_job_posting):
        """Test ATS score calculation for a good match."""
        score = calculate_ats_score(sample_resume_text, sample_job_posting['description'])
        
        assert 0 <= score <= 100
        assert score > 40  # Should be a reasonable score for matching content
    
    def test_calculate_ats_score_poor_match(self, sample_job_posting):
        """Test ATS score calculation for a poor match."""
        unrelated_resume = "Marketing experience with social media and content creation."
        
        score = calculate_ats_score(unrelated_resume, sample_job_posting['description'])
        
        assert 0 <= score <= 100
        assert score < 50  # Should be lower for unrelated content
    
    def test_generate_ats_report(self, sample_resume_text, sample_job_posting):
        """Test complete ATS report generation."""
        analyzer = ATSAnalyzer()
        
        # Create temporary resume file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_resume_text)
            resume_path = f.name
        
        try:
            report = analyzer.generate_ats_report(sample_job_posting, resume_path)
            
            # Check report structure
            assert 'ats_analysis' in report
            assert 'missing_keywords' in report
            assert 'keyword_density' in report
            assert 'bias_analysis' in report
            assert 'improvement_suggestions' in report
            
            # Check ATS analysis
            ats_analysis = report['ats_analysis']
            assert 'ats_score' in ats_analysis
            assert 0 <= ats_analysis['ats_score'] <= 100
            
            # Check keyword analysis
            assert isinstance(report['missing_keywords'], list)
            assert isinstance(report['keyword_density'], dict)
            
            # Check bias analysis
            bias_analysis = report['bias_analysis']
            assert 'bias_score' in bias_analysis
            assert 'bias_flags' in bias_analysis
            assert isinstance(bias_analysis['bias_flags'], list)
        
        finally:
            os.unlink(resume_path)
    
    def test_keyword_extraction(self):
        """Test keyword extraction from job descriptions."""
        analyzer = ATSAnalyzer()
        
        job_description = """
        Looking for a Python developer with Django experience.
        Must have SQL database knowledge and AWS cloud experience.
        Docker and Kubernetes skills preferred.
        """
        
        keywords = analyzer.extract_keywords(job_description)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        
        # Should find technical keywords
        keywords_lower = [kw.lower() for kw in keywords]
        expected_keywords = ['python', 'django', 'sql', 'aws', 'docker', 'kubernetes']
        found_keywords = sum(1 for kw in expected_keywords if any(kw in k for k in keywords_lower))
        assert found_keywords >= 3  # Should find at least half of the expected keywords
    
    def test_bias_detection(self):
        """Test bias detection in job descriptions."""
        analyzer = ATSAnalyzer()
        
        biased_description = """
        Looking for a young, energetic developer who is a culture fit.
        Native English speaker preferred. Must be able to work late nights.
        Ideal candidate is a recent graduate with fresh ideas.
        """
        
        neutral_description = """
        Looking for a skilled developer with 3+ years experience.
        Strong programming skills required. Ability to work collaboratively.
        Experience with version control systems preferred.
        """
        
        biased_flags = analyzer.detect_bias(biased_description)
        neutral_flags = analyzer.detect_bias(neutral_description)
        
        assert isinstance(biased_flags, list)
        assert isinstance(neutral_flags, list)
        assert len(biased_flags) > len(neutral_flags)


class TestAIIntegration:
    """Test AI feature integration and workflows."""
    
    @patch('groq_resume_suggestion.create_groq_client')
    def test_complete_ai_analysis_workflow(self, mock_create_client, sample_resume_text, sample_job_posting, mock_groq_response):
        """Test the complete AI analysis workflow."""
        # Setup Groq mock
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(mock_groq_response)
        mock_response.usage.total_tokens = 1500
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create temporary resume file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_resume_text)
            resume_path = f.name
        
        try:
            # Step 1: Job-resume matching
            matcher = JobResumeMatcher()
            match_score = calculate_match_score(sample_resume_text, sample_job_posting['description'])
            
            # Step 2: ATS analysis
            analyzer = ATSAnalyzer()
            ats_report = analyzer.generate_ats_report(sample_job_posting, resume_path)
            
            # Step 3: AI suggestions
            ai_suggestions = generate_resume_suggestions_groq(sample_resume_text, sample_job_posting)
            
            # Verify all components work together
            assert 0 <= match_score <= 100
            assert ats_report['ats_analysis']['ats_score'] >= 0
            assert ai_suggestions['success'] is True
            
            # The results should be coherent
            if match_score > 70:
                assert ai_suggestions['suggestions']['match_percentage'] > 60
        
        finally:
            os.unlink(resume_path)
    
    def test_ai_error_handling(self):
        """Test error handling in AI components."""
        # Test with invalid inputs
        matcher = JobResumeMatcher()
        
        # Empty text should handle gracefully
        score = calculate_match_score("", "job description")
        assert score == 0
        
        score = calculate_match_score("resume text", "")
        assert score == 0
    
    @patch('groq_resume_suggestion.create_groq_client')
    def test_ai_performance_monitoring(self, mock_create_client, sample_resume_text, sample_job_posting):
        """Test performance monitoring for AI operations."""
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        
        # Mock response with usage data
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "fit_summary": "Test response",
            "missing_keywords": [],
            "improvement_suggestions": []
        })
        mock_response.usage.total_tokens = 1500
        mock_response.usage.prompt_tokens = 1000
        mock_response.usage.completion_tokens = 500
        mock_client.chat.completions.create.return_value = mock_response
        
        result = generate_resume_suggestions_groq(sample_resume_text, sample_job_posting)
        
        # Should track API usage
        assert 'api_usage' in result
        assert result['api_usage']['total_tokens'] == 1500
        assert result['api_usage']['prompt_tokens'] == 1000
        assert result['api_usage']['completion_tokens'] == 500


@pytest.mark.slow
class TestAIPerformance:
    """Performance tests for AI components."""
    
    def test_matching_performance(self, sample_resume_text):
        """Test performance of job matching with multiple jobs."""
        import time
        
        # Create multiple job postings
        jobs = []
        for i in range(10):
            jobs.append({
                'title': f'IT Job {i}',
                'description': f'IT support position {i} with Windows and networking requirements',
                'company': f'Company {i}'
            })
        
        matcher = JobResumeMatcher()
        
        start_time = time.time()
        
        # Create temporary resume file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_resume_text)
            resume_path = f.name
        
        try:
            matches = matcher.get_top_matches(resume_path, jobs, top_n=5)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            assert processing_time < 5.0  # 5 seconds for 10 jobs
            assert len(matches) <= 5
            
        finally:
            os.unlink(resume_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 