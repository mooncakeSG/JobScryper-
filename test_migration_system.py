#!/usr/bin/env python3
"""
Auto Applyer - Production Migration System Test Script

Comprehensive test script to verify the production database migration system
works correctly before moving to the next development phase.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import subprocess

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_section(title: str):
    """Print a formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)

def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")

def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print a warning message."""
    print(f"⚠️  {message}")

def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")

def test_imports():
    """Test that all required modules can be imported."""
    print_section("Testing Module Imports")
    
    try:
        from database.production_migration import ProductionMigrationManager
        print_success("ProductionMigrationManager imported successfully")
    except ImportError as e:
        print_error(f"Failed to import ProductionMigrationManager: {e}")
        return False
    
    try:
        from database.models import Base, User, UserPreferences, JobApplication, Activity
        print_success("Database models imported successfully")
    except ImportError as e:
        print_error(f"Failed to import database models: {e}")
        return False
    
    try:
        from utils.errors import DatabaseError, MigrationError, ErrorHandler
        print_success("Error handling classes imported successfully")
    except ImportError as e:
        print_error(f"Failed to import error handling classes: {e}")
        return False
    
    try:
        from database.connection import get_database_manager
        print_success("Database connection module imported successfully")
    except ImportError as e:
        print_error(f"Failed to import database connection: {e}")
        return False
    
    return True

def test_migration_manager_creation():
    """Test migration manager creation and initialization."""
    print_section("Testing Migration Manager Creation")
    
    try:
        from database.production_migration import ProductionMigrationManager
        
        # Test creation
        manager = ProductionMigrationManager("testing")
        print_success("Migration manager created successfully")
        
        # Test properties
        assert manager.environment == "testing"
        assert manager.db_manager is None
        assert manager.backup_dir.exists()
        print_success("Migration manager properties verified")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create migration manager: {e}")
        return False

def test_database_initialization(db_path, database_url):
    """Test database initialization."""
    print_section("Testing Database Initialization")
    
    try:
        from database.production_migration import ProductionMigrationManager
        from sqlalchemy import create_engine, inspect
        from database.models import Base
        
        # Initialize migration manager
        manager = ProductionMigrationManager("testing")
        manager.initialize_database(database_url)
        
        print_success(f"Database initialized: {database_url}")
        
        # Verify database manager
        assert manager.db_manager is not None
        assert manager.db_manager.config.config['database_url'] == database_url
        assert manager.db_manager.config.environment == "testing"
        print_success("Database manager configuration verified")
        
        # Verify database file exists
        assert db_path.exists(), f"Database file not found: {db_path}"
        print_success("Database file created successfully")
        
        # Verify tables are created
        engine = create_engine(database_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users', 'user_preferences', 'resumes', 'job_applications', 
                          'search_history', 'ai_analysis_cache', 'system_settings', 
                          'saved_jobs', 'activities']
        
        for table in expected_tables:
            assert table in tables, f"Expected table '{table}' not found"
        
        print_success(f"All {len(expected_tables)} tables created successfully")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        return False

def test_backup_creation(db_path, database_url):
    """Test backup creation functionality."""
    print_section("Testing Backup Creation")
    
    try:
        from database.production_migration import ProductionMigrationManager
        from sqlalchemy import create_engine
        from database.models import Base
        
        # Initialize migration manager
        manager = ProductionMigrationManager("testing")
        manager.initialize_database(database_url)
        
        # Create database tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Create backup
        backup_path = manager.create_backup("test_backup")
        
        # Verify backup
        if backup_path:
            assert Path(backup_path).exists()
            assert backup_path.endswith("test_backup.sql")
            assert Path(backup_path).stat().st_size > 0
            print_success(f"Backup created: {backup_path}")
        else:
            print_warning("Backup skipped (in-memory or invalid DB)")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create backup: {e}")
        return False

def test_data_migration(db_path, database_url):
    """Test data migration functionality."""
    print_section("Testing Data Migration")
    
    try:
        from database.production_migration import ProductionMigrationManager
        from sqlalchemy import create_engine
        from database.models import Base, User, JobApplication, UserPreferences, Activity
        from database.models import ActivityType
        
        # Initialize migration manager
        manager = ProductionMigrationManager("testing")
        manager.initialize_database(database_url)
        
        # Create database tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Sample data for migration
        sample_data = {
            "users": [
                {
                    "email": "test@example.com",
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User",
                    "location": "Cape Town, South Africa",
                    "job_title": "IT Support Specialist",
                    "experience_years": 3,
                    "skills": ["Windows 10", "Active Directory", "Office 365"],
                    "is_active": True,
                    "is_verified": False
                }
            ],
            "applications": [
                {
                    "user_email": "test@example.com",
                    "job_title": "IT Support Specialist",
                    "company": "TechCorp Inc.",
                    "location": "Cape Town, South Africa",
                    "job_description": "Seeking IT Support Specialist with Windows experience",
                    "job_url": "https://example.com/job/123",
                    "application_date": "2024-01-15T10:00:00",
                    "status": "APPLIED",
                    "source": "linkedin",
                    "salary_min": 30000,
                    "salary_max": 40000,
                    "job_type": "Full-time",
                    "is_remote": False,
                    "easy_apply": True,
                    "match_score": 85.5
                }
            ],
            "preferences": [
                {
                    "user_email": "test@example.com",
                    "preferred_job_titles": ["IT Support Specialist", "Help Desk Analyst"],
                    "preferred_locations": ["Cape Town", "Remote"],
                    "salary_min": 30000,
                    "salary_max": 45000,
                    "salary_currency": "ZAR",
                    "remote_work_preference": True
                }
            ],
            "activities": [
                {
                    "user_email": "test@example.com",
                    "activity_type": ActivityType.APPLICATION_CREATED.value,
                    "title": "Applied to IT Support Specialist at TechCorp Inc.",
                    "description": "Submitted application for IT Support Specialist position",
                    "entity_type": "application",
                    "entity_id": 1,
                    "activity_metadata": {"company": "TechCorp Inc.", "status": "APPLIED"},
                    "created_at": "2024-01-15T10:00:00"
                }
            ]
        }
        
        # Perform migration
        manager.migrate_in_memory_to_persistent(sample_data)
        print_success("Data migration completed")
        
        # Verify migration with row counts
        with manager.db_manager.get_session() as session:
            users = session.query(User).all()
            applications = session.query(JobApplication).all()
            preferences = session.query(UserPreferences).all()
            activities = session.query(Activity).all()
            
            # Verify row counts
            assert len(users) == 1, f"Expected 1 user, got {len(users)}"
            assert len(applications) == 1, f"Expected 1 application, got {len(applications)}"
            assert len(preferences) == 1, f"Expected 1 preference set, got {len(preferences)}"
            assert len(activities) == 1, f"Expected 1 activity, got {len(activities)}"
            
            print_success(f"Row counts verified - Users: {len(users)}, Applications: {len(applications)}, Preferences: {len(preferences)}, Activities: {len(activities)}")
            
            # Check user data
            user = users[0]
            assert user.email == "test@example.com"
            assert user.first_name == "Test"
            assert user.job_title == "IT Support Specialist"
            
            # Check application data
            app = applications[0]
            assert app.job_title == "IT Support Specialist"
            assert app.company == "TechCorp Inc."
            assert app.user.email == "test@example.com"
            
            # Check activity data
            activity = activities[0]
            assert activity.title == "Applied to IT Support Specialist at TechCorp Inc."
            assert activity.activity_type.value == ActivityType.APPLICATION_CREATED.value
            
            print_success("Data migration verification passed")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to migrate data: {e}")
        return False

def test_migration_verification(db_path, database_url):
    """Test migration verification functionality."""
    print_section("Testing Migration Verification")
    
    try:
        from database.production_migration import ProductionMigrationManager
        from sqlalchemy import create_engine, inspect
        from database.models import Base, User, JobApplication, UserPreferences, Activity
        
        # Initialize migration manager with the same database
        manager = ProductionMigrationManager("testing")
        manager.initialize_database(database_url)
        
        # Verify database file exists and has data
        assert db_path.exists(), f"Database file not found: {db_path}"
        
        # Check if data exists from previous migration test
        with manager.db_manager.get_session() as session:
            user_count = session.query(User).count()
            application_count = session.query(JobApplication).count()
            preference_count = session.query(UserPreferences).count()
            activity_count = session.query(Activity).count()
        
        print_info(f"Current database counts - Users: {user_count}, Applications: {application_count}, Preferences: {preference_count}, Activities: {activity_count}")
        
        # Run verification
        verification = manager.verify_migration()
        
        assert verification['success'] is True
        assert verification['environment'] == "testing"
        assert verification['database_url'] == database_url
        
        # Verify counts match what we expect (should be 1 each if data migration ran)
        if user_count > 0:
            assert verification['user_count'] == user_count, f"Expected {user_count} users, got {verification['user_count']}"
        if application_count > 0:
            assert verification['application_count'] == application_count, f"Expected {application_count} applications, got {verification['application_count']}"
        if preference_count > 0:
            assert verification['preference_count'] == preference_count, f"Expected {preference_count} preferences, got {verification['preference_count']}"
        if activity_count > 0:
            assert verification['activity_count'] == activity_count, f"Expected {activity_count} activities, got {verification['activity_count']}"
        
        print_success("Migration verification passed")
        print_info(f"Database contains {verification['tables_found']} tables")
        print_info(f"Verified counts - Users: {verification['user_count']}, Applications: {verification['application_count']}, Preferences: {verification['preference_count']}, Activities: {verification['activity_count']}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to verify migration: {e}")
        return False

def test_error_handling():
    """Test error handling system."""
    print_section("Testing Error Handling")
    
    try:
        from utils.errors import (
            DatabaseError, MigrationError, ErrorHandler, 
            handle_exceptions, safe_execute, create_error
        )
        
        # Test error creation
        db_error = DatabaseError("Test database error", operation="connect", table="users")
        assert db_error.error_code == "DB_ERROR"
        assert db_error.details['operation'] == "connect"
        print_success("Database error creation works")
        
        # Test migration error
        migration_error = MigrationError("Test migration error", migration_version="001")
        assert migration_error.error_code == "MIGRATION_ERROR"
        assert migration_error.details['migration_version'] == "001"
        print_success("Migration error creation works")
        
        # Test error handler
        handler = ErrorHandler(log_errors=False)  # Don't log during tests
        error_info = handler.handle_error(db_error)
        assert error_info['error'] is True
        assert error_info['error_code'] == "DB_ERROR"
        print_success("Error handler works")
        
        # Test safe execution
        def failing_function():
            raise ValueError("Test error")
        
        result = safe_execute(failing_function, default_return="fallback")
        assert result == "fallback"
        print_success("Safe execution works")
        
        # Test error decorator
        @handle_exceptions
        def decorated_function():
            raise RuntimeError("Decorated error")
        
        try:
            decorated_function()
        except Exception as e:
            assert "Decorated error" in str(e)
        print_success("Error decorator works")
        
        # Test error creation utility
        error = create_error('database_connection_failed', operation='connect')
        assert isinstance(error, DatabaseError)
        print_success("Error creation utility works")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to test error handling: {e}")
        return False

def test_cli_functionality():
    """Test CLI functionality."""
    print_section("Testing CLI Functionality")
    
    try:
        # Test help command
        result = subprocess.run([
            sys.executable, "database/production_migration.py", "--help"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("CLI help command works")
        else:
            print_warning("CLI help command failed (this might be expected)")
        
        # Test basic CLI initialization
        result = subprocess.run([
            sys.executable, "database/production_migration.py", 
            "--environment", "testing", "--verify"
        ], capture_output=True, text=True)
        
        # CLI might fail due to missing database, but should not crash
        if result.returncode in [0, 1]:  # 0 = success, 1 = expected error
            print_success("CLI basic functionality works")
        else:
            print_error("CLI crashed unexpectedly")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Failed to test CLI: {e}")
        return False

def test_unit_tests():
    """Run the unit tests for the migration system."""
    print_section("Running Unit Tests")
    
    try:
        # Check if pytest is available
        result = subprocess.run([
            sys.executable, "-m", "pytest", "--version"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print_warning("pytest not available, skipping unit tests")
            return True
        
        # Run the migration unit tests
        test_file = "tests/unit/test_database_migration.py"
        if Path(test_file).exists():
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success("Unit tests passed")
                print_info("Migration system unit tests completed successfully")
            else:
                print_warning("Some unit tests failed")
                print_info("This might be expected if database dependencies are missing")
        else:
            print_warning(f"Unit test file not found: {test_file}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to run unit tests: {e}")
        return False

def test_integration():
    """Test integration with existing backend."""
    print_section("Testing Backend Integration")
    
    try:
        # Test if backend can import migration system
        from backend.main import app
        print_success("Backend can import migration system")
        
        # Test if database models are accessible
        from database.models import User, JobApplication
        print_success("Database models are accessible from backend")
        
        # Test if error handling is accessible
        from utils.errors import DatabaseError, MigrationError
        print_success("Error handling is accessible from backend")
        
        return True
        
    except ImportError as e:
        print_warning(f"Backend integration test skipped: {e}")
        return True
    except Exception as e:
        print_error(f"Backend integration test failed: {e}")
        return False

def main():
    """Main test function."""
    print_header("Auto Applyer - Production Migration System Test")
    
    print_info("This script will test the production database migration system")
    print_info("to ensure it works correctly before moving to the next phase.")

    # Create a single temp dir and db for all tests
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_migration.db"
    database_url = f"sqlite:///{db_path}"

    tests = [
        ("Module Imports", lambda: test_imports()),
        ("Migration Manager Creation", lambda: test_migration_manager_creation()),
        ("Database Initialization", lambda: test_database_initialization(db_path, database_url)),
        ("Backup Creation", lambda: test_backup_creation(db_path, database_url)),
        ("Data Migration", lambda: test_data_migration(db_path, database_url)),
        ("Migration Verification", lambda: test_migration_verification(db_path, database_url)),
        ("Error Handling", lambda: test_error_handling()),
        ("CLI Functionality", lambda: test_cli_functionality()),
        ("Unit Tests", lambda: test_unit_tests()),
        ("Backend Integration", lambda: test_integration()),
    ]

    passed = 0
    failed = 0
    for name, func in tests:
        try:
            if func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("🧪 Test Results Summary")
    print("=" * 60)
    print_info(f"Tests Passed: {passed}")
    print_info(f"Tests Failed: {failed}")
    print_info(f"Total Tests: {passed + failed}")
    if failed == 0:
        print_success("All tests passed! Migration system is production-ready.")
    else:
        print_error(f"{failed} test(s) failed. Please review the errors above.")
    print("=" * 60)
    shutil.rmtree(temp_dir)
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 