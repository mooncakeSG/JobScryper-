#!/usr/bin/env python3
"""
Auto Applyer Test Runner

Convenient script to run tests with various options and configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description=""):
    """Run a command and return the result."""
    print(f"🔄 {description}")
    print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"✅ {description} - Passed")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False, e.stderr


def main():
    parser = argparse.ArgumentParser(description="Auto Applyer Test Runner")
    
    # Test type options
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Test options
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    
    # Specific test options
    parser.add_argument("--file", type=str, help="Run specific test file")
    parser.add_argument("--function", type=str, help="Run specific test function")
    
    # Output options
    parser.add_argument("--html-report", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--xml-report", action="store_true", help="Generate XML test report")
    
    args = parser.parse_args()
    
    # Default to all tests if no specific type is selected
    if not any([args.unit, args.integration, args.performance, args.file]):
        args.all = True
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Add test directories/files
    if args.file:
        pytest_cmd.append(args.file)
    elif args.unit:
        pytest_cmd.append("tests/unit/")
    elif args.integration:
        pytest_cmd.append("tests/integration/")
    elif args.performance:
        pytest_cmd.append("tests/performance/")
    elif args.all:
        pytest_cmd.append("tests/")
    
    # Add specific function if specified
    if args.function:
        pytest_cmd.extend(["-k", args.function])
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-v")
    else:
        pytest_cmd.append("-q")
    
    # Add coverage options
    if args.coverage or args.html_report:
        pytest_cmd.extend([
            "--cov=.",
            "--cov-report=term-missing"
        ])
        
        if args.html_report:
            pytest_cmd.append("--cov-report=html:htmlcov")
        
        # Remove --cov-exclude arguments, handled by pytest.ini
    
    # Add XML report for CI
    if args.xml_report:
        pytest_cmd.append("--junit-xml=test-results.xml")
    
    # Skip slow tests if requested
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])
    
    # Parallel execution
    if args.parallel:
        pytest_cmd.extend(["-n", "auto"])
    
    # Additional pytest options
    pytest_cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print("🧪 Auto Applyer Test Runner")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ pytest not found. Please install test dependencies:")
        print("   pip install pytest pytest-cov pytest-mock")
        return 1
    
    # Run the tests
    success, output = run_command(pytest_cmd, "Running tests")
    
    if success:
        print("\n📊 Test Summary:")
        print(output)
        
        if args.coverage or args.html_report:
            print("\n📈 Coverage Information:")
            if args.html_report:
                print("HTML coverage report generated: htmlcov/index.html")
        
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Tests failed!")
        print(output)
        return 1


def quick_test():
    """Run a quick smoke test to verify basic functionality."""
    print("🚀 Running Quick Smoke Test")
    print("=" * 30)
    
    # Test basic imports
    try:
        print("📦 Testing imports...")
        
        # Test utils imports
        from utils.errors import AutoApplyerError
        from utils.validation import InputValidator
        from utils.retry import RetryHandler
        print("✅ Utils imports - OK")
        
        # Test basic functionality
        validator = InputValidator()
        validator.validate_user_text_input("test", "test_field")
        print("✅ Basic validation - OK")
        
        retry_handler = RetryHandler()
        print("✅ Retry handler - OK")
        
        print("\n🎯 Smoke test passed! Core functionality working.")
        return True
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False


def install_test_dependencies():
    """Install test dependencies."""
    print("📦 Installing test dependencies...")
    
    dependencies = [
        "pytest>=8.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.14.0",
        "pytest-xdist>=3.0.0",  # For parallel testing
        "pytest-html>=4.0.0",   # For HTML reports
        "coverage>=7.0.0"
    ]
    
    for dep in dependencies:
        cmd = ["pip", "install", dep]
        success, _ = run_command(cmd, f"Installing {dep}")
        if not success:
            print(f"⚠️  Failed to install {dep}")
            return False
    
    print("✅ Test dependencies installed successfully!")
    return True


if __name__ == "__main__":
    # Special commands
    if len(sys.argv) > 1:
        if sys.argv[1] == "smoke":
            sys.exit(0 if quick_test() else 1)
        elif sys.argv[1] == "install-deps":
            sys.exit(0 if install_test_dependencies() else 1)
        elif sys.argv[1] == "help":
            print("""
Auto Applyer Test Runner Commands:

Basic Usage:
  python run_tests.py                 # Run all tests
  python run_tests.py --unit          # Run unit tests only
  python run_tests.py --integration   # Run integration tests only
  python run_tests.py --coverage      # Run with coverage report
  
Special Commands:
  python run_tests.py smoke           # Quick smoke test
  python run_tests.py install-deps    # Install test dependencies
  python run_tests.py help            # Show this help
  
Advanced Options:
  --verbose / -v                      # Verbose output
  --fast                              # Skip slow tests
  --parallel                          # Run tests in parallel
  --html-report                       # Generate HTML coverage report
  --file <path>                       # Run specific test file
  --function <name>                   # Run specific test function
  
Examples:
  python run_tests.py --unit --coverage --verbose
  python run_tests.py --file tests/unit/test_errors.py
  python run_tests.py --function test_api_error --verbose
            """)
            sys.exit(0)
    
    # Run main test command
    sys.exit(main()) 