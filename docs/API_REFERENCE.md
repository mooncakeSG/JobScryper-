# Auto Applyer - API Reference

## Overview

This document provides detailed information about the Auto Applyer's internal APIs, classes, and functions.

## Table of Contents

1. [Core Application](#core-application)
2. [Job Scraping APIs](#job-scraping-apis)
3. [AI & Machine Learning APIs](#ai--machine-learning-apis)
4. [Document Processing APIs](#document-processing-apis)
5. [Data Management APIs](#data-management-apis)
6. [Utility Functions](#utility-functions)

## Core Application

### Main Application (`app.py`)

#### `search_jobs(job_title, location, job_type, keywords)`
Searches for jobs using multiple scrapers.

**Parameters:**
- `job_title` (str): Job title to search for
- `location` (str): Location for the search
- `job_type` (str): Type of job (Full-time, Part-time, etc.)
- `keywords` (str): Additional keywords

**Returns:**
- `List[Dict]`: List of job dictionaries

**Example:**
```python
jobs = search_jobs("Software Developer", "Cape Town", "Full-time", "Python React")
```

#### `display_job_card(job, source)`
Displays a formatted job card in the Streamlit interface.

**Parameters:**
- `job` (Dict): Job data dictionary
- `source` (str): Source of the job listing

#### `apply_to_job(job, source)`
Handles job application tracking and provides application guidance.

**Parameters:**
- `job` (Dict): Job data dictionary
- `source` (str): Source of the job listing

#### `analyze_job(job)`
Analyzes job compatibility with uploaded resume using ATS scoring.

**Parameters:**
- `job` (Dict): Job data dictionary

## Job Scraping APIs

### JobSpy Wrapper (`jobspy_wrapper.py`)

#### Class: `JobSpyWrapper`

##### `search_jobs(job_title, location, sites, max_results)`
Searches for jobs using the JobSpy library.

**Parameters:**
- `job_title` (str): Job title to search for
- `location` (str): Location for the search (default: "Remote")
- `sites` (List[str]): List of job sites to search (default: ['indeed', 'linkedin', 'glassdoor'])
- `max_results` (int): Maximum number of results per site (default: 50)

**Returns:**
- `List[Dict]`: Standardized job listings

**Example:**
```python
wrapper = JobSpyWrapper()
jobs = wrapper.search_jobs("Data Analyst", "Johannesburg", ["linkedin", "indeed"], 20)
```

### Alternative Sources (`alternative_sources.py`)

#### Class: `AlternativeJobAggregator`

##### `search_all_sources(job_title, location, max_per_source)`
Searches multiple alternative job sources.

**Parameters:**
- `job_title` (str): Job title to search for
- `location` (str): Location for the search
- `max_per_source` (int): Maximum results per source (default: 10)

**Returns:**
- `List[Dict]`: Combined job listings from all sources

#### Class: `RemoteOKScraper`

##### `search_jobs(keywords, location, max_results)`
Searches RemoteOK for remote job opportunities.

#### Class: `AdzunaAPIScraper`

##### `search_jobs(job_title, location, max_results)`
Searches Adzuna job board using their API.

**Required Environment Variables:**
- `ADZUNA_APP_ID`: Your Adzuna application ID
- `ADZUNA_APP_KEY`: Your Adzuna application key

#### Class: `JoobleAPIScraper`

##### `search_jobs(job_title, location, max_results)`
Searches Jooble job aggregator using their API.

**Required Environment Variables:**
- `JOOBLE_API_KEY`: Your Jooble API key

### LinkedIn Bot (`linkedin_bot.py`)

#### Class: `LinkedInBot`

##### `search_jobs(job_title, location, max_pages)`
Scrapes LinkedIn job listings (requires careful rate limiting).

**Parameters:**
- `job_title` (str): Job title to search for
- `location` (str): Location for the search
- `max_pages` (int): Maximum number of pages to scrape (default: 3)

**Returns:**
- `List[Dict]`: LinkedIn job listings

## AI & Machine Learning APIs

### Groq Resume Suggestions (`groq_resume_suggestion.py`)

#### Class: `GroqResumeSuggestionGenerator`

##### `__init__(api_key, config)`
Initializes the Groq AI client.

**Parameters:**
- `api_key` (str, optional): Groq API key (reads from environment if not provided)
- `config` (GroqResumeSuggestionConfig, optional): Configuration object

##### `generate_suggestions(resume_text, job_data)`
Generates AI-powered resume suggestions for a specific job.

**Parameters:**
- `resume_text` (str): Parsed resume text
- `job_data` (Dict): Job posting information

**Returns:**
- `Dict`: Detailed suggestions and analysis

**Example:**
```python
generator = GroqResumeSuggestionGenerator()
suggestions = generator.generate_suggestions(resume_text, job_data)
```

#### Function: `generate_resume_suggestions_groq(resume_text, job_data, api_key)`
Convenience function for generating resume suggestions.

### ATS Analyzer (`ats_report.py`)

#### Class: `ATSAnalyzer`

##### `generate_ats_report(job_data, resume_path)`
Generates comprehensive ATS analysis report.

**Parameters:**
- `job_data` (Dict): Job posting data
- `resume_path` (str): Path to resume file

**Returns:**
- `Dict`: Complete ATS analysis including:
  - ATS keyword scoring
  - Missing keywords identification
  - Bias detection in job postings
  - Improvement recommendations

##### `calculate_ats_keyword_score(job_text, resume_text)`
Calculates ATS keyword match score.

**Returns:**
- `Dict`: Scoring details with matched/missing keywords

##### `detect_bias(job_text)`
Detects potential bias in job posting language.

**Returns:**
- `Dict`: Bias analysis with flags and recommendations

### Job-Resume Matcher (`matcher.py`)

#### Class: `JobResumeMatcher`

##### `calculate_compatibility_score(job_data, resume_text)`
Calculates compatibility score between job and resume.

**Parameters:**
- `job_data` (Dict): Job posting data
- `resume_text` (str): Parsed resume text

**Returns:**
- `float`: Compatibility score (0.0 to 1.0)

## Document Processing APIs

### Resume Parser (`resume_parser.py`)

#### Class: `ResumeParser`

##### `parse_resume(file_path)`
Parses resume from various file formats.

**Parameters:**
- `file_path` (str): Path to resume file

**Returns:**
- `Dict`: Parsed resume data including:
  - `cleaned_text`: Processed text content
  - `sections`: Identified resume sections
  - `contact_info`: Extracted contact information
  - `skills`: Identified skills and keywords

**Supported Formats:**
- PDF (.pdf)
- Word Documents (.docx, .doc)
- Text Files (.txt)

#### Function: `get_resume_text_for_matching(file_path)`
Extracts clean text from resume for job matching.

**Parameters:**
- `file_path` (str): Path to resume file

**Returns:**
- `str`: Clean text suitable for analysis

## Data Management APIs

### Application Tracking

#### `save_applications_to_csv()`
Saves application history to CSV file.

**Returns:**
- `bool`: Success status

#### `load_applications_from_csv()`
Loads application history from CSV file.

**Returns:**
- `bool`: Success status

### Session Management

Session state variables used throughout the application:

- `st.session_state.applications`: List of job applications
- `st.session_state.jobs_data`: Current job search results
- `st.session_state.current_jobs`: Jobs being displayed
- `st.session_state.resume_path`: Path to uploaded resume
- `st.session_state.resume_parsed`: Parsed resume data
- `st.session_state.ai_recommendations`: AI-generated recommendations
- `st.session_state.interview_tips`: Generated interview tips

## Utility Functions

### Job Filters (`filters.py`)

#### Class: `JobFilter`

##### `filter_jobs_by_category(jobs, category)`
Filters jobs by technology category.

**Parameters:**
- `jobs` (List[Dict]): List of job postings
- `category` (str): Technology category to filter by

**Returns:**
- `List[Dict]`: Filtered job listings

### Data Quality Assessment

#### `calculate_job_data_quality(job)`
Calculates data completeness score for job postings.

**Parameters:**
- `job` (Dict): Job posting data

**Returns:**
- `int`: Quality score (0-100%)

## Error Handling

### Common Exceptions

#### `APIKeyError`
Raised when required API keys are missing or invalid.

#### `ParseError`
Raised when document parsing fails.

#### `NetworkError`
Raised when network requests fail or timeout.

### Error Response Format

```python
{
    "error": "Error description",
    "error_type": "APIKeyError|ParseError|NetworkError",
    "timestamp": "2025-01-08T10:30:00Z",
    "details": "Additional error details"
}
```

## Rate Limiting

### API Limits

- **Groq API**: 10,000 requests/month (free tier)
- **Adzuna API**: 1,000 requests/month (free tier)
- **Jooble API**: Free tier available
- **JobSpy**: Built-in rate limiting (2-5 seconds between requests)

### Best Practices

1. **Implement exponential backoff** for retries
2. **Cache API responses** when possible
3. **Monitor API usage** to avoid limits
4. **Handle rate limit errors** gracefully

## Environment Variables

### Required

- `GROQ_API_KEY`: For AI-powered features

### Optional

- `ADZUNA_APP_ID`: For Adzuna job search
- `ADZUNA_APP_KEY`: For Adzuna job search
- `JOOBLE_API_KEY`: For Jooble job search

### Configuration

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `MAX_JOBS_PER_SEARCH`: Maximum jobs to return per search
- `CACHE_TIMEOUT`: API response cache timeout in seconds

## Testing

### Unit Tests

Tests are located in the `tests/` directory:

- `tests/test_job_scraping.py`: Job scraping functionality
- `tests/test_ai_features.py`: AI and ML features
- `tests/test_document_processing.py`: Resume parsing
- `tests/test_data_management.py`: Data handling

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_job_scraping.py

# Run with coverage
pytest --cov=. tests/
```

## Performance Considerations

### Optimization Tips

1. **Limit concurrent requests** to avoid overwhelming APIs
2. **Use caching** for frequently accessed data
3. **Implement pagination** for large result sets
4. **Monitor memory usage** during document processing

### Benchmarks

- Resume parsing: ~2-5 seconds per document
- Job search: ~10-30 seconds per search
- AI suggestions: ~3-8 seconds per generation
- ATS analysis: ~1-3 seconds per job

---

*Last updated: July 8, 2025*
*Version: 1.0* 