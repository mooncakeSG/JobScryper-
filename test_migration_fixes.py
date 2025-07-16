#!/usr/bin/env python3
"""
Auto Applyer - Migration System Fixes Test

Simple test script to verify that the migration system fixes work correctly.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing Module Imports...")
    
    try:
        from database.production_migration import ProductionMigrationManager
        print("✅ ProductionMigrationManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ProductionMigrationManager: {e}")
        return False
    
    try:
        from utils.errors import DatabaseError, MigrationError, APIKeyError, RateLimitError
        print("✅ Error handling classes imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import error handling classes: {e}")
        return False
    
    try:
        from database.models import User, JobApplication, UserPreferences, Activity
        print("✅ Database models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database models: {e}")
        return False
    
    return True

def test_migration_manager():
    """Test migration manager creation and initialization."""
    print("\n🧪 Testing Migration Manager...")
    
    try:
        from database.production_migration import ProductionMigrationManager
        
        # Create migration manager
        manager = ProductionMigrationManager("testing")
        print("✅ Migration manager created successfully")
        
        # Test properties
        assert manager.environment == "testing"
        assert manager.db_manager is None
        assert manager.backup_dir.exists()
        print("✅ Migration manager properties verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create migration manager: {e}")
        return False

def test_database_initialization():
    """Test database initialization."""
    print("\n🧪 Testing Database Initialization...")
    
    try:
        from database.production_migration import ProductionMigrationManager
        
        # Initialize migration manager with testing environment
        manager = ProductionMigrationManager("testing")
        manager.initialize_database()
        
        print(f"✅ Database initialized: {manager.db_manager.config.config.get('database_url')}")
        
        # Verify database manager
        assert manager.db_manager is not None
        assert manager.db_manager.config.environment == "testing"
        print("✅ Database manager configuration verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def test_error_handling():
    """Test error handling system."""
    print("\n🧪 Testing Error Handling...")
    
    try:
        from utils.errors import (
            DatabaseError, MigrationError, APIKeyError, RateLimitError,
            ErrorHandler, create_error
        )
        
        # Test error creation
        db_error = DatabaseError("Test database error", operation="connect", table="users")
        assert db_error.error_code == "DB_ERROR"
        print("✅ Database error creation works")
        
        # Test API key error
        api_error = APIKeyError("Test API key error", api_name="groq", is_missing=True)
        assert api_error.error_code == "API_KEY_ERROR"
        print("✅ API key error creation works")
        
        # Test rate limit error
        rate_error = RateLimitError("Test rate limit error", service_name="jobspy", retry_after=60)
        assert rate_error.error_code == "RATE_LIMIT_ERROR"
        print("✅ Rate limit error creation works")
        
        # Test error handler
        handler = ErrorHandler(log_errors=False)  # Don't log during tests
        error_info = handler.handle_error(db_error)
        assert error_info['error'] is True
        print("✅ Error handler works")
        
        # Test error creation utility
        error = create_error('database_connection_failed', operation='connect')
        assert isinstance(error, DatabaseError)
        print("✅ Error creation utility works")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test error handling: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 Auto Applyer - Migration System Fixes Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Migration Manager", test_migration_manager),
        ("Database Initialization", test_database_initialization),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📋 Total Tests: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Migration system fixes are working correctly.")
        print("✅ You can now run the full migration system test.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
    
    print("\n" + "=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 