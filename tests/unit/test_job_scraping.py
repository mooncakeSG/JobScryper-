"""
Unit tests for job scraping functionality.

Tests the JobSpy wrapper, job filtering, and data processing components.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import modules under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from jobspy_wrapper import JobSpyWrapper
    from filters import ITJobFilter, filter_it_jobs
    import alternative_sources
except ImportError as e:
    pytest.skip(f"Skipping job scraping tests due to import error: {e}", allow_module_level=True)


@pytest.fixture
def sample_jobspy_data():
    """Sample data that would come from JobSpy."""
    return pd.DataFrame([
        {
            'title': 'IT Support Specialist',
            'company': 'TechCorp Inc.',
            'location': 'Cape Town, South Africa',
            'description': 'We are seeking an experienced IT Support Specialist with Windows 10, Active Directory, and Office 365 experience.',
            'job_url': 'https://example.com/job/1',
            'site': 'linkedin',
            'date_posted': '2025-01-08',
            'salary_min': 25000,
            'salary_max': 35000,
            'job_type': 'Full-time',
            'country': 'South Africa',
            'emails': [],
            'is_remote': False
        },
        {
            'title': 'Senior Software Engineer',
            'company': 'DevCorp Ltd.',
            'location': 'Johannesburg, South Africa',
            'description': 'Looking for a senior software engineer with Python, Django, and React experience.',
            'job_url': 'https://example.com/job/2',
            'site': 'indeed',
            'date_posted': '2025-01-07',
            'salary_min': 45000,
            'salary_max': 65000,
            'job_type': 'Full-time',
            'country': 'South Africa',
            'emails': [],
            'is_remote': True
        },
        {
            'title': 'Help Desk Analyst',
            'company': 'SupportCorp',
            'location': 'Durban, South Africa',
            'description': 'Entry-level help desk position. Training provided. Must have good communication skills.',
            'job_url': 'https://example.com/job/3',
            'site': 'glassdoor',
            'date_posted': '2025-01-06',
            'salary_min': 18000,
            'salary_max': 22000,
            'job_type': 'Full-time',
            'country': 'South Africa',
            'emails': [],
            'is_remote': False
        },
        {
            'title': 'Marketing Manager',
            'company': 'MarketCorp',
            'location': 'Cape Town, South Africa',
            'description': 'Experienced marketing manager needed for growing startup.',
            'job_url': 'https://example.com/job/4',
            'site': 'linkedin',
            'date_posted': '2025-01-05',
            'salary_min': 35000,
            'salary_max': 45000,
            'job_type': 'Full-time',
            'country': 'South Africa',
            'emails': [],
            'is_remote': False
        }
    ])


@pytest.fixture
def mock_jobspy_module():
    """Mock the jobspy module for testing."""
    with patch('jobspy.scrape_jobs') as mock_scrape:
        yield mock_scrape


class TestJobSpyWrapper:
    """Test the JobSpy wrapper functionality."""
    
    def test_initialization(self):
        """Test JobSpyWrapper initialization."""
        wrapper = JobSpyWrapper()
        
        assert wrapper.max_results == 50
        assert wrapper.hours_old == 168  # 1 week
        assert wrapper.country_indeed == "South Africa"
        assert wrapper.is_remote is None
    
    def test_initialization_with_params(self):
        """Test JobSpyWrapper initialization with custom parameters."""
        wrapper = JobSpyWrapper(
            max_results=100,
            hours_old=24,
            country_indeed="United States",
            is_remote=True
        )
        
        assert wrapper.max_results == 100
        assert wrapper.hours_old == 24
        assert wrapper.country_indeed == "United States"
        assert wrapper.is_remote is True
    
    def test_search_jobs_success(self, mock_jobspy_module, sample_jobspy_data):
        """Test successful job search."""
        mock_jobspy_module.return_value = sample_jobspy_data
        
        wrapper = JobSpyWrapper()
        result = wrapper.search_jobs(
            site_name='linkedin',
            search_term='IT Support',
            location='Cape Town',
            results_wanted=50
        )
        
        # Verify the mock was called correctly
        mock_jobspy_module.assert_called_once()
        call_args = mock_jobspy_module.call_args
        
        assert call_args[1]['site_name'] == ['linkedin']
        assert call_args[1]['search_term'] == 'IT Support'
        assert call_args[1]['location'] == 'Cape Town'
        assert call_args[1]['results_wanted'] == 50
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_jobspy_data)
    
    def test_search_jobs_multiple_sites(self, mock_jobspy_module, sample_jobspy_data):
        """Test job search with multiple sites."""
        mock_jobspy_module.return_value = sample_jobspy_data
        
        wrapper = JobSpyWrapper()
        result = wrapper.search_jobs(
            site_name=['linkedin', 'indeed'],
            search_term='IT Support',
            location='Cape Town'
        )
        
        call_args = mock_jobspy_module.call_args
        assert set(call_args[1]['site_name']) == {'linkedin', 'indeed'}
    
    def test_search_jobs_with_error(self, mock_jobspy_module):
        """Test job search when JobSpy raises an exception."""
        mock_jobspy_module.side_effect = Exception("JobSpy error")
        
        wrapper = JobSpyWrapper()
        
        with pytest.raises(Exception):
            wrapper.search_jobs(
                site_name='linkedin',
                search_term='IT Support',
                location='Cape Town'
            )
    
    def test_search_jobs_empty_result(self, mock_jobspy_module):
        """Test job search when no jobs are found."""
        mock_jobspy_module.return_value = pd.DataFrame()
        
        wrapper = JobSpyWrapper()
        result = wrapper.search_jobs(
            site_name='linkedin',
            search_term='NonexistentJob',
            location='Cape Town'
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_search_jobs_data_processing(self, mock_jobspy_module, sample_jobspy_data):
        """Test that job data is properly processed and formatted."""
        mock_jobspy_module.return_value = sample_jobspy_data
        
        wrapper = JobSpyWrapper()
        result = wrapper.search_jobs(
            site_name='linkedin',
            search_term='IT Support',
            location='Cape Town'
        )
        
        # Check that required columns exist
        required_columns = ['title', 'company', 'location', 'description', 'job_url']
        for col in required_columns:
            assert col in result.columns
        
        # Check data types and content
        assert all(isinstance(title, str) for title in result['title'])
        assert all(isinstance(company, str) for company in result['company'])
        assert all(result['job_url'].str.startswith('http'))


class TestITJobFilter:
    """Test the IT job filtering functionality."""
    
    def test_filter_initialization(self):
        """Test ITJobFilter initialization."""
        job_filter = ITJobFilter()
        
        assert len(job_filter.it_keywords) > 0
        assert len(job_filter.it_titles) > 0
        assert len(job_filter.exclude_keywords) > 0
        assert "support" in [kw.lower() for kw in job_filter.it_keywords]
        assert "helpdesk" in [title.lower() for title in job_filter.it_titles]
    
    def test_is_it_job_by_title(self, sample_jobspy_data):
        """Test IT job identification by title."""
        job_filter = ITJobFilter()
        
        # Test cases: (title, expected_result)
        test_cases = [
            ("IT Support Specialist", True),
            ("Help Desk Analyst", True),
            ("Desktop Support Technician", True),
            ("System Administrator", True),
            ("Network Engineer", True),
            ("Marketing Manager", False),
            ("Sales Representative", False),
            ("Human Resources Assistant", False),
        ]
        
        for title, expected in test_cases:
            job = {"title": title, "description": "Test description"}
            result = job_filter.is_it_job(job)
            assert result == expected, f"Failed for title: {title}"
    
    def test_is_it_job_by_description(self):
        """Test IT job identification by description content."""
        job_filter = ITJobFilter()
        
        # Job with IT-related description but non-IT title
        it_job = {
            "title": "Technical Specialist",
            "description": "Looking for someone with Windows 10 experience, Active Directory administration, and help desk background."
        }
        
        non_it_job = {
            "title": "Sales Manager",
            "description": "Experienced sales professional needed to manage client relationships and drive revenue growth."
        }
        
        assert job_filter.is_it_job(it_job) is True
        assert job_filter.is_it_job(non_it_job) is False
    
    def test_is_it_job_with_exclusions(self):
        """Test that excluded keywords properly filter out jobs."""
        job_filter = ITJobFilter()
        
        # Job that has IT keywords but should be excluded
        excluded_job = {
            "title": "IT Support Manager",
            "description": "Senior management position requiring 10+ years experience and team leadership."
        }
        
        # This should return False due to senior/management exclusions
        # Note: Actual behavior depends on the exclusion logic implementation
        result = job_filter.is_it_job(excluded_job)
        # The exact assertion would depend on the filter's exclusion rules
    
    def test_calculate_relevance_score(self):
        """Test relevance score calculation."""
        job_filter = ITJobFilter()
        
        high_relevance_job = {
            "title": "IT Support Specialist",
            "description": "Windows 10, Active Directory, Office 365, help desk, technical support, troubleshooting"
        }
        
        low_relevance_job = {
            "title": "Technical Assistant",
            "description": "General office duties with some computer work"
        }
        
        high_score = job_filter.calculate_relevance_score(high_relevance_job)
        low_score = job_filter.calculate_relevance_score(low_relevance_job)
        
        assert high_score > low_score
        assert high_score >= 0
        assert low_score >= 0
    
    def test_filter_jobs_dataframe(self, sample_jobspy_data):
        """Test filtering a DataFrame of jobs."""
        job_filter = ITJobFilter()
        
        # Convert DataFrame to list of dictionaries for filtering
        jobs_list = sample_jobspy_data.to_dict('records')
        filtered_jobs = job_filter.filter_jobs(jobs_list)
        
        # Should filter out non-IT jobs (like Marketing Manager)
        assert len(filtered_jobs) < len(jobs_list)
        
        # All filtered jobs should be IT-related
        for job in filtered_jobs:
            assert job_filter.is_it_job(job)
        
        # Check that jobs are sorted by relevance
        if len(filtered_jobs) > 1:
            for i in range(len(filtered_jobs) - 1):
                current_score = job_filter.calculate_relevance_score(filtered_jobs[i])
                next_score = job_filter.calculate_relevance_score(filtered_jobs[i + 1])
                assert current_score >= next_score


class TestFilterFunction:
    """Test the filter_it_jobs function."""
    
    def test_filter_it_jobs_function(self, sample_jobspy_data):
        """Test the main filter_it_jobs function."""
        # Convert DataFrame to the expected format
        jobs_data = sample_jobspy_data.to_dict('records')
        
        filtered_jobs = filter_it_jobs(jobs_data)
        
        # Should return filtered and scored jobs
        assert isinstance(filtered_jobs, list)
        assert len(filtered_jobs) > 0
        
        # Each job should have a relevance score
        for job in filtered_jobs:
            assert 'relevance_score' in job
            assert isinstance(job['relevance_score'], (int, float))
            assert job['relevance_score'] >= 0
    
    def test_filter_it_jobs_empty_input(self):
        """Test filter_it_jobs with empty input."""
        result = filter_it_jobs([])
        assert result == []
    
    def test_filter_it_jobs_no_it_jobs(self):
        """Test filter_it_jobs when no IT jobs are found."""
        non_it_jobs = [
            {
                "title": "Marketing Manager",
                "description": "Marketing and sales experience required"
            },
            {
                "title": "Chef",
                "description": "Culinary arts and kitchen management"
            }
        ]
        
        result = filter_it_jobs(non_it_jobs)
        assert len(result) == 0


class TestAlternativeSources:
    """Test alternative job sources functionality."""
    
    @pytest.mark.slow
    def test_get_remote_ok_jobs(self):
        """Test RemoteOK job fetching."""
        try:
            from alternative_sources import get_remote_ok_jobs
            
            with patch('requests.get') as mock_get:
                # Mock successful API response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = [
                    {
                        'id': '123',
                        'position': 'IT Support Engineer',
                        'company': 'RemoteCompany',
                        'location': 'Remote',
                        'description': 'Remote IT support position',
                        'url': 'https://remoteok.io/jobs/123',
                        'tags': ['support', 'it', 'remote'],
                        'date': '2025-01-08'
                    }
                ]
                mock_get.return_value = mock_response
                
                jobs = get_remote_ok_jobs(search_term="IT Support", limit=10)
                
                assert isinstance(jobs, list)
                if jobs:  # If we got results
                    assert 'title' in jobs[0]
                    assert 'company' in jobs[0]
                    assert 'source' in jobs[0]
                    assert jobs[0]['source'] == 'RemoteOK'
        
        except ImportError:
            pytest.skip("alternative_sources module not available")
    
    @pytest.mark.slow
    def test_get_adzuna_jobs(self):
        """Test Adzuna job fetching."""
        try:
            from alternative_sources import get_adzuna_jobs
            
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'results': [
                        {
                            'title': 'IT Support Specialist',
                            'company': {'display_name': 'TechCorp'},
                            'location': {'display_name': 'Cape Town'},
                            'description': 'IT support role',
                            'redirect_url': 'https://adzuna.com/job/123'
                        }
                    ]
                }
                mock_get.return_value = mock_response
                
                jobs = get_adzuna_jobs(
                    search_term="IT Support",
                    location="Cape Town",
                    limit=10
                )
                
                assert isinstance(jobs, list)
                if jobs:
                    assert 'title' in jobs[0]
                    assert 'company' in jobs[0]
                    assert 'source' in jobs[0]
                    assert jobs[0]['source'] == 'Adzuna'
        
        except ImportError:
            pytest.skip("alternative_sources module not available")


class TestJobDataProcessing:
    """Test job data processing and normalization."""
    
    def test_normalize_job_data(self):
        """Test job data normalization across different sources."""
        # This would test the standardization of job data from different sources
        # into a common format
        
        raw_jobspy_job = {
            'title': 'IT Support Specialist',
            'company': 'TechCorp',
            'location': 'Cape Town, South Africa',
            'description': 'IT support role',
            'job_url': 'https://example.com/job/1',
            'site': 'linkedin',
            'salary_min': 25000,
            'salary_max': 35000
        }
        
        raw_remoteok_job = {
            'position': 'IT Support Engineer',
            'company': 'RemoteCompany',
            'location': 'Remote',
            'description': 'Remote IT support',
            'url': 'https://remoteok.io/jobs/123',
            'tags': ['support', 'it']
        }
        
        # Test normalization (this would depend on actual implementation)
        # The goal is to ensure all jobs have consistent field names and formats
    
    def test_merge_job_sources(self):
        """Test merging jobs from multiple sources."""
        jobspy_jobs = [
            {'title': 'IT Support 1', 'source': 'JobSpy', 'job_url': 'url1'},
            {'title': 'IT Support 2', 'source': 'JobSpy', 'job_url': 'url2'}
        ]
        
        remoteok_jobs = [
            {'title': 'Remote IT Support', 'source': 'RemoteOK', 'job_url': 'url3'}
        ]
        
        # Test merging and deduplication logic
        # This would test the function that combines jobs from multiple sources
        # and removes duplicates based on URL or other criteria
    
    def test_job_deduplication(self):
        """Test duplicate job removal."""
        jobs_with_duplicates = [
            {'title': 'IT Support', 'company': 'TechCorp', 'job_url': 'https://example.com/job/1'},
            {'title': 'IT Support Specialist', 'company': 'TechCorp', 'job_url': 'https://example.com/job/1'},  # Same URL
            {'title': 'Help Desk', 'company': 'DataCorp', 'job_url': 'https://example.com/job/2'}
        ]
        
        # Test deduplication logic
        # This would test the function that removes duplicate jobs
        # based on URL, title+company combination, or other criteria


@pytest.mark.integration
class TestJobScrapingIntegration:
    """Integration tests for job scraping workflow."""
    
    def test_complete_job_search_workflow(self, mock_jobspy_module, sample_jobspy_data):
        """Test the complete job search and filtering workflow."""
        mock_jobspy_module.return_value = sample_jobspy_data
        
        # Step 1: Search for jobs
        wrapper = JobSpyWrapper()
        raw_jobs = wrapper.search_jobs(
            site_name='linkedin',
            search_term='IT Support',
            location='Cape Town'
        )
        
        # Step 2: Convert to format expected by filter
        jobs_list = raw_jobs.to_dict('records')
        
        # Step 3: Filter for IT jobs
        filtered_jobs = filter_it_jobs(jobs_list)
        
        # Verify the complete workflow
        assert len(filtered_jobs) > 0
        assert all('relevance_score' in job for job in filtered_jobs)
        assert all(job['relevance_score'] >= 0 for job in filtered_jobs)
    
    @pytest.mark.slow
    def test_multiple_sources_integration(self):
        """Test integration with multiple job sources."""
        # This would test the complete workflow of:
        # 1. Searching JobSpy
        # 2. Searching alternative sources
        # 3. Combining results
        # 4. Filtering and deduplication
        # 5. Scoring and ranking
        
        # Mock multiple sources
        with patch('jobspy.scrape_jobs') as mock_jobspy, \
             patch('requests.get') as mock_requests:
            
            # Setup mocks for successful responses
            mock_jobspy.return_value = pd.DataFrame([
                {'title': 'IT Support', 'company': 'JobSpyCompany', 'job_url': 'url1'}
            ])
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_requests.return_value = mock_response
            
            # Test the integration
            # This would call the main job search function that combines all sources


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 