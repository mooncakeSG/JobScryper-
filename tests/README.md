# Auto Applyer Testing Framework

This directory contains comprehensive tests for the Auto Applyer application, including unit tests, integration tests, and performance tests.

## 📁 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures and configuration
├── README.md                   # This documentation
├── unit/                       # Unit tests for individual components
│   ├── __init__.py
│   ├── test_error_handling.py  # Error handling system tests
│   ├── test_job_scraping.py    # Job scraping functionality tests
│   ├── test_ai_features.py     # AI and ML feature tests
│   └── test_resume_parsing.py  # Resume parsing tests
├── integration/                # End-to-end workflow tests
│   ├── __init__.py
│   └── test_complete_workflow.py # Complete application workflow tests
└── performance/                # Performance and load tests
    └── __init__.py
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
Test individual functions and classes in isolation with mocked dependencies.

**Coverage:**
- Error handling system
- Job scraping and filtering
- AI features (Groq integration, matching)
- Resume parsing and analysis
- Validation and retry mechanisms

### Integration Tests (`tests/integration/`)
Test complete workflows and cross-module functionality.

**Coverage:**
- End-to-end job search workflow
- Resume analysis pipeline
- Application tracking lifecycle
- Multiple job source integration
- Error handling across modules

### Performance Tests (`tests/performance/`)
Test performance characteristics and load handling.

**Coverage:**
- Response time benchmarks
- Memory usage monitoring
- Concurrent user simulation
- API rate limiting validation

## 🚀 Running Tests

### Quick Start
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
python run_tests.py

# Run quick smoke test
python run_tests.py smoke
```

### Using the Test Runner
The `run_tests.py` script provides convenient options:

```bash
# Basic usage
python run_tests.py                 # Run all tests
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --performance   # Performance tests only

# With coverage
python run_tests.py --coverage      # Terminal coverage report
python run_tests.py --html-report   # HTML coverage report

# Advanced options
python run_tests.py --verbose       # Verbose output
python run_tests.py --fast          # Skip slow tests
python run_tests.py --parallel      # Run tests in parallel

# Specific tests
python run_tests.py --file tests/unit/test_error_handling.py
python run_tests.py --function test_api_error
```

### Using pytest Directly
```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest -m "not slow"  # Skip slow tests

# Run specific test file
pytest tests/unit/test_error_handling.py -v

# Run specific test function
pytest tests/unit/test_error_handling.py::TestCustomExceptions::test_api_error_creation -v
```

## 📊 Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Tests that take longer than 10 seconds
- `@pytest.mark.api` - Tests requiring external API calls
- `@pytest.mark.mocked` - Tests using mocked dependencies

### Using Markers
```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run only API tests (use sparingly)
pytest -m api

# Combine markers
pytest -m "unit and not slow"
```

## 🔧 Test Configuration

### pytest.ini
The `pytest.ini` file contains test configuration:
- Test discovery settings
- Coverage configuration
- Marker definitions
- Output formatting

### conftest.py
Shared test fixtures and utilities:
- Sample data fixtures
- Mock configurations
- Test utilities
- Environment setup

## 🏗️ Writing Tests

### Test File Naming
- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<workflow_name>.py`
- Performance tests: `test_<feature>_performance.py`

### Test Function Naming
```python
def test_<function_being_tested>_<scenario>():
    """Test description explaining what is being tested."""
    pass

# Examples:
def test_api_error_creation():
def test_job_search_with_valid_params():
def test_resume_parsing_with_pdf_file():
```

### Test Structure (AAA Pattern)
```python
def test_example():
    """Test description."""
    # Arrange - Set up test data and conditions
    input_data = {"key": "value"}
    expected_result = "expected"
    
    # Act - Execute the function being tested
    result = function_under_test(input_data)
    
    # Assert - Verify the results
    assert result == expected_result
```

### Using Fixtures
```python
def test_with_fixtures(sample_job, sample_resume_file):
    """Test using shared fixtures."""
    # Fixtures are automatically injected
    assert sample_job['title'] is not None
    assert os.path.exists(sample_resume_file)
```

### Mocking External Dependencies
```python
@patch('external_module.api_call')
def test_with_mock(mock_api_call):
    """Test with mocked external dependency."""
    mock_api_call.return_value = {"status": "success"}
    
    result = function_that_calls_api()
    
    assert result is not None
    mock_api_call.assert_called_once()
```

## 📈 Coverage Reports

### Generating Coverage Reports
```bash
# Terminal report
pytest --cov=. --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=. --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=. --cov-report=xml
```

### Coverage Targets
- **Overall coverage target:** 80%+
- **Critical modules:** 90%+ (error handling, core functionality)
- **UI modules:** 60%+ (harder to test, more manual verification needed)

### Excluded from Coverage
- Test files themselves
- Setup scripts
- Configuration files
- External dependencies

## 🔍 Debugging Tests

### Running Tests in Debug Mode
```bash
# Verbose output with full tracebacks
pytest -v --tb=long

# Drop into debugger on failure
pytest --pdb

# Print statements (normally captured)
pytest -s

# Specific test with debugging
pytest tests/unit/test_error_handling.py::test_api_error -v -s
```

### Common Debugging Tips
1. **Use print statements**: Add `print()` statements and run with `-s`
2. **Check fixtures**: Verify fixture data is as expected
3. **Mock verification**: Use `mock.assert_called_with()` to verify mock calls
4. **Temporary files**: Check that temporary files are created/cleaned up properly

## 🚀 Continuous Integration

### CI Test Commands
```bash
# Fast test suite for CI
pytest tests/ -m "not slow" --cov=. --cov-report=xml --junit-xml=test-results.xml

# Full test suite (nightly builds)
pytest tests/ --cov=. --cov-report=xml --junit-xml=test-results.xml
```

### Test Environment Variables
Set these in CI/testing environments:
```bash
export TESTING=true
export LOG_LEVEL=DEBUG
export GROQ_API_KEY=test_key_for_mocking
```

## 🐛 Common Issues and Solutions

### Import Errors
**Problem:** `ModuleNotFoundError` when running tests
**Solution:** Ensure the project root is in Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Fixture Not Found
**Problem:** `fixture 'fixture_name' not found`
**Solution:** Check that fixtures are defined in `conftest.py` or imported properly

### Mock Not Working
**Problem:** Mock not intercepting calls
**Solution:** Ensure you're patching the right module and function path:
```python
# Patch where it's used, not where it's defined
@patch('module_under_test.external_function')  # Correct
@patch('external_module.external_function')   # Often wrong
```

### Temporary Files
**Problem:** Tests leaving temporary files behind
**Solution:** Use fixtures with proper cleanup or `tempfile.TemporaryDirectory()`

### Async/Await Issues
**Problem:** Tests hanging or not running async code
**Solution:** Use `pytest-asyncio` and mark tests with `@pytest.mark.asyncio`

## 📝 Test Data and Fixtures

### Sample Data Location
- Resume samples: `tests/fixtures/resumes/`
- Job posting samples: Defined in `conftest.py`
- Configuration samples: `tests/fixtures/config/`

### Creating New Fixtures
```python
# In conftest.py or test file
@pytest.fixture
def my_fixture():
    """Description of what this fixture provides."""
    # Setup
    data = create_test_data()
    
    yield data  # Provide to test
    
    # Cleanup (optional)
    cleanup_test_data()
```

## 🎯 Best Practices

### Test Organization
1. **One test file per module** being tested
2. **Group related tests** in test classes
3. **Use descriptive test names** that explain the scenario
4. **Keep tests independent** - no test should depend on another

### Test Quality
1. **Test one thing at a time** - focused, single-purpose tests
2. **Use meaningful assertions** - check the right things
3. **Mock external dependencies** - tests should be reliable and fast
4. **Test edge cases** - empty inputs, large inputs, error conditions

### Performance
1. **Keep tests fast** - under 1 second each for unit tests
2. **Mark slow tests** - use `@pytest.mark.slow` for tests > 10 seconds
3. **Use fixtures efficiently** - share setup across related tests
4. **Mock expensive operations** - database calls, API calls, file I/O

## 📚 Additional Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov coverage plugin](https://pytest-cov.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)

### Contributing Tests
When adding new features:
1. **Write tests first** (TDD approach recommended)
2. **Include both positive and negative test cases**
3. **Update this documentation** if adding new test categories
4. **Ensure tests pass in CI** before merging

### Getting Help
- Check existing tests for examples
- Review `conftest.py` for available fixtures
- Run `python run_tests.py help` for test runner options
- Check the main project documentation for testing guidelines

---

**Happy Testing! 🧪** 