# Contributing to Auto Applyer

Thank you for your interest in contributing to Auto Applyer! This guide will help you get started with contributing to our AI-powered job search application.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Guidelines](#contributing-guidelines)
5. [Code Standards](#code-standards)
6. [Testing](#testing)
7. [Pull Request Process](#pull-request-process)
8. [Issue Reporting](#issue-reporting)
9. [Development Workflow](#development-workflow)
10. [Architecture Guidelines](#architecture-guidelines)

## Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic understanding of web scraping and AI concepts
- Familiarity with Streamlit framework

### Quick Setup
1. Fork the repository
2. Clone your fork locally
3. Set up the development environment
4. Create a feature branch
5. Make your changes
6. Submit a pull request

## Development Setup

### 1. Clone the Repository
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/JobScryper-.git
cd JobScryper-

# Add upstream remote
git remote add upstream https://github.com/mooncakeSG/JobScryper-.git
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black isort flake8 pre-commit
```

### 4. Set Up Pre-commit Hooks
```bash
pre-commit install
```

### 5. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# GROQ_API_KEY=your_groq_api_key_here
```

### 6. Verify Setup
```bash
# Run the application
streamlit run app.py

# Run tests
pytest

# Check code formatting
black --check .
isort --check .
flake8 .
```

## Contributing Guidelines

### Types of Contributions

#### 🐛 Bug Fixes
- Fix broken functionality
- Improve error handling
- Resolve performance issues

#### ✨ New Features
- Add new job sources
- Enhance AI capabilities
- Improve user interface
- Add analytics and reporting

#### 📚 Documentation
- Improve setup guides
- Add code examples
- Create tutorials
- Update API documentation

#### 🧪 Testing
- Write unit tests
- Add integration tests
- Create test fixtures
- Improve test coverage

#### 🎨 UI/UX Improvements
- Enhance visual design
- Improve user experience
- Add accessibility features
- Optimize mobile responsiveness

### Areas for Contribution

#### High Priority
1. **Error Handling & Reliability**
   - Comprehensive error handling
   - Graceful degradation
   - Retry mechanisms
   - User-friendly error messages

2. **Testing Infrastructure**
   - Unit test coverage
   - Integration testing
   - Mock external APIs
   - Performance testing

3. **Documentation**
   - Code documentation
   - User guides
   - API references
   - Architecture documentation

#### Medium Priority
1. **New Job Sources**
   - Additional job board APIs
   - Regional job sites
   - Niche industry platforms
   - Government job portals

2. **AI Enhancements**
   - Better resume parsing
   - Advanced job matching
   - Interview preparation
   - Salary prediction

3. **User Experience**
   - Mobile optimization
   - Accessibility improvements
   - Performance optimization
   - Offline capabilities

#### Low Priority
1. **Advanced Features**
   - User authentication
   - Database integration
   - Email notifications
   - Social media integration

## Code Standards

### Python Style Guide
We follow PEP 8 with some modifications:

```python
# Good examples
class JobScraper:
    """Base class for all job scrapers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def search_jobs(
        self, 
        job_title: str, 
        location: str, 
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """Search for jobs matching criteria.
        
        Args:
            job_title: The job title to search for
            location: The location for the search
            max_results: Maximum number of results to return
            
        Returns:
            List of job dictionaries
            
        Raises:
            APIError: When API request fails
        """
        try:
            # Implementation here
            pass
        except Exception as e:
            self.logger.error(f"Job search failed: {e}")
            raise
```

### Formatting Tools
```bash
# Format code
black .

# Sort imports
isort .

# Check for style issues
flake8 .

# Type checking (optional but recommended)
mypy .
```

### Documentation Standards

#### Docstrings
Use Google-style docstrings:

```python
def parse_resume(file_path: str) -> Dict[str, Any]:
    """Parse resume from file.
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Dictionary containing parsed resume data with keys:
        - 'text': Raw text content
        - 'sections': Identified sections
        - 'metadata': File metadata
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ParseError: If file cannot be parsed
        
    Example:
        >>> result = parse_resume("resume.pdf")
        >>> print(result['text'][:100])
        'John Doe Software Engineer...'
    """
```

#### Comments
```python
# Good: Explain why, not what
# Use exponential backoff to handle rate limiting
for attempt in range(max_retries):
    try:
        response = make_api_call()
        break
    except RateLimitError:
        sleep_time = 2 ** attempt
        time.sleep(sleep_time)
```

### Error Handling Standards

```python
class JobScraperError(Exception):
    """Base exception for job scraper errors."""
    pass

class APIKeyError(JobScraperError):
    """Raised when API key is missing or invalid."""
    pass

class RateLimitError(JobScraperError):
    """Raised when API rate limit is exceeded."""
    pass

# Usage
try:
    jobs = scraper.search_jobs(title, location)
except APIKeyError:
    logger.error("API key not configured")
    return {"error": "API configuration required"}
except RateLimitError:
    logger.warning("Rate limit exceeded, retrying...")
    time.sleep(60)
    # Retry logic
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal server error"}
```

## Testing

### Test Structure
```
tests/
├── unit/
│   ├── test_job_scraping.py
│   ├── test_resume_parsing.py
│   ├── test_ai_features.py
│   └── test_utilities.py
├── integration/
│   ├── test_full_workflow.py
│   ├── test_api_integration.py
│   └── test_file_operations.py
├── fixtures/
│   ├── sample_resumes/
│   ├── sample_jobs.json
│   └── test_config.py
└── conftest.py
```

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from job_scraper import JobSpyWrapper

class TestJobSpyWrapper:
    def setup_method(self):
        self.scraper = JobSpyWrapper()
    
    def test_search_jobs_success(self):
        """Test successful job search."""
        # Arrange
        expected_jobs = [
            {"title": "Software Engineer", "company": "Tech Corp"}
        ]
        
        # Act
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = expected_jobs
            result = self.scraper.search_jobs("Engineer", "Remote")
        
        # Assert
        assert len(result) == 1
        assert result[0]["title"] == "Software Engineer"
    
    def test_search_jobs_api_error(self):
        """Test handling of API errors."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException()
            
            with pytest.raises(APIError):
                self.scraper.search_jobs("Engineer", "Remote")
```

#### Integration Tests
```python
import pytest
import tempfile
from pathlib import Path

class TestResumeWorkflow:
    def test_full_resume_analysis_workflow(self):
        """Test complete resume analysis workflow."""
        # Create temporary resume file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b"Sample resume content")
            tmp_path = tmp.name
        
        try:
            # Test upload and parsing
            parser = ResumeParser()
            parsed = parser.parse_resume(tmp_path)
            
            assert parsed['text']
            assert 'sections' in parsed
            
            # Test AI analysis
            analyzer = GroqAnalyzer()
            suggestions = analyzer.generate_suggestions(parsed['text'])
            
            assert 'suggestions' in suggestions
            assert len(suggestions['suggestions']) > 0
        finally:
            Path(tmp_path).unlink()
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_job_scraping.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run integration tests only
pytest tests/integration/

# Run tests matching pattern
pytest -k "test_search_jobs"
```

### Test Fixtures
```python
# conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def sample_job():
    return {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Remote",
        "description": "Python developer position",
        "url": "https://example.com/job/123"
    }

@pytest.fixture
def mock_groq_client():
    mock_client = Mock()
    mock_client.chat.completions.create.return_value.choices[0].message.content = "AI response"
    return mock_client
```

## Pull Request Process

### Before Submitting

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Your Changes**
   - Follow code standards
   - Write tests
   - Update documentation

3. **Test Thoroughly**
```bash
pytest
black --check .
isort --check .
flake8 .
```

4. **Commit Changes**
```bash
git add .
git commit -m "feat: add new job source integration

- Add Adzuna API integration
- Implement rate limiting
- Add comprehensive tests
- Update documentation

Closes #123"
```

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(scraping): add LinkedIn job scraper

- Implement LinkedIn API integration
- Add rate limiting for API calls
- Include company logo extraction
- Add comprehensive error handling

Closes #45

fix(resume): handle corrupted PDF files

- Add try-catch for PDF parsing errors
- Provide user-friendly error messages
- Add fallback to text extraction
- Update tests for error scenarios

Fixes #78
```

### Pull Request Template

When you submit a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested the changes manually

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] Any dependent changes have been merged and published
```

### Review Process

1. **Automated Checks**
   - All tests must pass
   - Code style checks must pass
   - No security vulnerabilities

2. **Manual Review**
   - Code quality and maintainability
   - Architecture consistency
   - Documentation completeness
   - Test coverage

3. **Feedback & Iteration**
   - Address review comments
   - Update code as needed
   - Re-request review

4. **Merge**
   - Squash commits if needed
   - Update changelog
   - Deploy to staging (if applicable)

## Issue Reporting

### Bug Reports

Use this template for bug reports:

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10, macOS 12, Ubuntu 20.04]
 - Python Version: [e.g. 3.9.7]
 - Browser: [e.g. chrome, safari]
 - Version: [e.g. 22]

**Additional Context**
Add any other context about the problem here.
```

### Feature Requests

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Development Workflow

### Git Workflow

```bash
# Stay up to date
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/new-job-source

# Make changes and commit
git add .
git commit -m "feat: add new job source"

# Push to your fork
git push origin feature/new-job-source

# Create pull request on GitHub
```

### Release Process

1. **Version Bump**
   - Update version in `setup.py`
   - Update `CHANGELOG.md`
   - Create release notes

2. **Testing**
   - Run full test suite
   - Manual testing
   - Performance testing

3. **Release**
   - Create GitHub release
   - Tag version
   - Deploy to production

### Development Best Practices

1. **Small, Focused Changes**
   - Keep PRs small and focused
   - One feature per PR
   - Easy to review and test

2. **Documentation**
   - Update docs with code changes
   - Include examples
   - Keep README current

3. **Testing**
   - Write tests for new features
   - Maintain test coverage
   - Test edge cases

4. **Communication**
   - Discuss major changes in issues
   - Ask questions early
   - Provide context in PRs

## Architecture Guidelines

### Adding New Job Sources

1. **Create Scraper Class**
```python
from .base_scraper import BaseJobScraper

class NewJobSiteScraper(BaseJobScraper):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://api.newjobsite.com"
    
    def search_jobs(self, criteria):
        # Implementation
        pass
    
    def parse_job_data(self, raw_data):
        # Parse to standard format
        pass
```

2. **Register in Factory**
```python
# In job_scraper_factory.py
def create_scraper(source_type):
    if source_type == "newjobsite":
        return NewJobSiteScraper(config)
```

3. **Add Tests**
```python
class TestNewJobSiteScraper:
    def test_search_jobs(self):
        # Test implementation
        pass
```

4. **Update Documentation**
   - Add to API reference
   - Update user guide
   - Include in setup instructions

### Adding AI Features

1. **Create Service Module**
```python
class NewAIService:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def process_data(self, input_data):
        # AI processing logic
        pass
```

2. **Integration**
```python
# In main app
if st.button("New AI Feature"):
    service = NewAIService(api_key)
    result = service.process_data(user_input)
    st.json(result)
```

3. **Error Handling**
```python
try:
    result = ai_service.process(data)
except APIKeyError:
    st.error("API key required")
except Exception as e:
    st.error(f"Processing failed: {e}")
```

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: [maintainer email] for private communication
- **Documentation**: Check docs/ folder for detailed guides

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes
- Annual contributor highlights

Thank you for contributing to Auto Applyer! 🚀

---

*Last updated: July 8, 2025*
*Version: 1.0* 