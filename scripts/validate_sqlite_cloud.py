#!/usr/bin/env python3
"""
Auto Applyer - SQLite Cloud Connection Validator

This script validates the SQLite Cloud connection and configuration
for production deployment.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseConfig, DatabaseManager
from utils.logging_config import get_logger

logger = get_logger(__name__)


def validate_environment_variables():
    """Validate required environment variables are set."""
    required_vars = [
        'SQLITE_CLOUD_HOST',
        'SQLITE_CLOUD_API_KEY',
        'SQLITE_CLOUD_DATABASE'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True


def validate_database_config():
    """Validate database configuration."""
    try:
        config = DatabaseConfig('production')
        print(f"✅ Database configuration loaded successfully")
        print(f"   Environment: {config.environment}")
        print(f"   Database URL: {config.config['database_url'].replace(config.config.get('password', ''), '***')}")
        return True
    except Exception as e:
        print(f"❌ Database configuration error: {e}")
        return False


def test_database_connection():
    """Test database connection."""
    try:
        print("🔌 Testing database connection...")
        db_manager = DatabaseManager(DatabaseConfig('production'))
        db_manager.initialize()
        
        # Test basic connection
        with db_manager.session_scope() as session:
            result = session.execute("SELECT 1 as test")
            test_value = result.scalar()
            if test_value == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection test failed")
                return False
        
        # Get database info
        info = db_manager.get_database_info()
        print(f"✅ Database info retrieved:")
        print(f"   Status: {info['status']}")
        print(f"   Type: {info['database_type']}")
        print(f"   Tables: {info['table_count']}")
        
        db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_database_operations():
    """Test basic database operations."""
    try:
        print("🔧 Testing database operations...")
        db_manager = DatabaseManager(DatabaseConfig('production'))
        db_manager.initialize()
        
        # Test table creation
        db_manager.create_tables(drop_existing=False)
        print("✅ Table creation/verification successful")
        
        # Test session operations
        with db_manager.session_scope() as session:
            # Test a simple query
            result = session.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = result.scalar()
            print(f"✅ Session operations successful (found {table_count} tables)")
        
        db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False


def validate_ssl_configuration():
    """Validate SSL configuration."""
    ssl_mode = os.getenv('SQLITE_CLOUD_SSL_MODE', 'require')
    
    if ssl_mode not in ['require', 'verify-full', 'verify-ca', 'prefer', 'allow', 'disable']:
        print(f"❌ Invalid SSL mode: {ssl_mode}")
        return False
    
    print(f"✅ SSL configuration valid: {ssl_mode}")
    return True


def check_connection_pool():
    """Check connection pool configuration."""
    pool_size = int(os.getenv('DATABASE_POOL_SIZE', '10'))
    max_overflow = int(os.getenv('DATABASE_MAX_OVERFLOW', '20'))
    
    if pool_size < 1 or pool_size > 50:
        print(f"❌ Invalid pool size: {pool_size} (should be 1-50)")
        return False
    
    if max_overflow < 0 or max_overflow > 100:
        print(f"❌ Invalid max overflow: {max_overflow} (should be 0-100)")
        return False
    
    print(f"✅ Connection pool configuration valid:")
    print(f"   Pool size: {pool_size}")
    print(f"   Max overflow: {max_overflow}")
    return True


def run_performance_test():
    """Run basic performance test."""
    try:
        print("⚡ Running performance test...")
        db_manager = DatabaseManager(DatabaseConfig('production'))
        db_manager.initialize()
        
        import time
        start_time = time.time()
        
        # Test multiple connections
        for i in range(5):
            with db_manager.session_scope() as session:
                session.execute("SELECT 1")
        
        end_time = time.time()
        duration = end_time - start_time
        
        if duration < 5.0:  # Should complete in under 5 seconds
            print(f"✅ Performance test passed ({duration:.2f}s)")
        else:
            print(f"⚠️  Performance test slow ({duration:.2f}s)")
        
        db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def generate_report(results):
    """Generate validation report."""
    print("\n" + "="*60)
    print("📊 SQLITE CLOUD VALIDATION REPORT")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print()
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SQLite Cloud is ready for production.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description='Validate SQLite Cloud configuration')
    parser.add_argument('--skip-performance', action='store_true', 
                       help='Skip performance tests')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Load environment variables from .env.production
    env_file = Path(".env.production")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ Loaded environment from .env.production")
    else:
        print("⚠️  .env.production file not found")
    
    if args.verbose:
        # Set debug level for logging
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🔍 SQLite Cloud Configuration Validator")
    print("="*50)
    
    # Run all validation tests
    results = {
        "Environment Variables": validate_environment_variables(),
        "Database Configuration": validate_database_config(),
        "SSL Configuration": validate_ssl_configuration(),
        "Connection Pool": check_connection_pool(),
        "Database Connection": test_database_connection(),
        "Database Operations": test_database_operations(),
    }
    
    if not args.skip_performance:
        results["Performance Test"] = run_performance_test()
    
    # Generate report
    success = generate_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 