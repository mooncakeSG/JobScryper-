#!/usr/bin/env python3
"""
Auto Applyer - Database Initialization Script

Script to initialize the database, run migrations, and set up initial data.
"""

import sys
import os
from pathlib import Path
import argparse
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import init_database, DatabaseConfig
from database.migrations import MigrationManager
from database.utilities import DatabaseUtils, BackupManager
from database.models import User, UserPreferences, ApplicationStatus
from utils.logging_config import get_logger

logger = get_logger(__name__)


def setup_development_data(create_sample_user: bool = True) -> None:
    """Set up development/demo data."""
    try:
        logger.info("Setting up development data")
        
        if create_sample_user:
            # Create a sample user for development
            try:
                sample_user = DatabaseUtils.create_user(
                    email="demo@autoapplyer.com",
                    first_name="Demo",
                    last_name="User",
                    location="Cape Town, South Africa",
                    job_title="IT Support Specialist",
                    experience_years=3,
                    skills=["Windows 10", "Active Directory", "Office 365", "Help Desk"]
                )
                
                logger.info(f"Created sample user: {sample_user.email} (ID: {sample_user.id})")
                
                # Update user preferences
                DatabaseUtils.update_user_preferences(
                    sample_user.id,
                    preferred_job_titles=["IT Support Specialist", "Help Desk Analyst", "Desktop Support"],
                    preferred_locations=["Cape Town", "Johannesburg", "Remote"],
                    preferred_job_types=["Full-time", "Contract"],
                    salary_min=25000,
                    salary_max=45000,
                    remote_work_preference=True,
                    daily_job_alerts=True
                )
                
                logger.info("Updated sample user preferences")
                
                # Add sample job application
                sample_app = DatabaseUtils.add_job_application(
                    user_id=sample_user.id,
                    job_title="IT Support Specialist",
                    company="TechCorp Inc.",
                    location="Cape Town, South Africa",
                    job_description="Seeking IT Support Specialist with Windows and Office 365 experience",
                    job_url="https://example.com/job/123",
                    status=ApplicationStatus.APPLIED,
                    source="linkedin",
                    salary_min=30000,
                    salary_max=40000,
                    job_type="Full-time",
                    is_remote=False,
                    easy_apply=True,
                    match_score=85.5
                )
                
                logger.info(f"Created sample job application: {sample_app.job_title}")
                
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("Sample user already exists, skipping creation")
                else:
                    logger.error(f"Failed to create sample user: {e}")
        
        logger.info("Development data setup completed")
        
    except Exception as e:
        logger.error(f"Failed to set up development data: {e}")
        raise


def main():
    """Main initialization function."""
    parser = argparse.ArgumentParser(description="Auto Applyer Database Initialization")
    
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "testing", "production"],
        default="development",
        help="Environment to initialize"
    )
    
    parser.add_argument(
        "--reset", "-r",
        action="store_true",
        help="Reset database (WARNING: destroys all data)"
    )
    
    parser.add_argument(
        "--no-migrate",
        action="store_true",
        help="Skip running migrations"
    )
    
    parser.add_argument(
        "--no-sample-data",
        action="store_true",
        help="Skip creating sample data for development"
    )
    
    parser.add_argument(
        "--backup-before-reset",
        action="store_true",
        help="Create backup before reset"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force operations without confirmation"
    )
    
    args = parser.parse_args()
    
    print("🗄️  Auto Applyer Database Initialization")
    print("=" * 50)
    
    try:
        # Set environment variable
        os.environ['ENVIRONMENT'] = args.environment
        
        print(f"Environment: {args.environment}")
        print(f"Reset database: {args.reset}")
        print(f"Run migrations: {not args.no_migrate}")
        print(f"Create sample data: {not args.no_sample_data and args.environment == 'development'}")
        print("-" * 50)
        
        # Confirmation for destructive operations
        if args.reset and not args.force:
            if args.environment == "production":
                print("⚠️  WARNING: You are about to reset the PRODUCTION database!")
                print("This will permanently delete ALL data.")
                confirmation = input("Type 'DELETE ALL DATA' to confirm: ")
                if confirmation != "DELETE ALL DATA":
                    print("❌ Operation cancelled")
                    return 1
            else:
                confirmation = input(f"Reset {args.environment} database? [y/N]: ")
                if confirmation.lower() != 'y':
                    print("❌ Operation cancelled")
                    return 1
        
        # Create backup before reset if requested
        if args.reset and args.backup_before_reset:
            try:
                print("📦 Creating backup before reset...")
                backup_manager = BackupManager()
                backup_path = backup_manager.create_backup()
                print(f"✅ Backup created: {backup_path}")
            except Exception as e:
                print(f"⚠️  Backup failed: {e}")
                if not args.force:
                    confirmation = input("Continue without backup? [y/N]: ")
                    if confirmation.lower() != 'y':
                        return 1
        
        # Initialize database
        print("🔄 Initializing database connection...")
        db_manager = init_database(args.environment, drop_existing=args.reset)
        print(f"✅ Database initialized ({db_manager.config.environment})")
        
        # Run migrations
        if not args.no_migrate:
            print("🔄 Running database migrations...")
            migration_manager = MigrationManager()
            
            if args.reset:
                # For reset, apply all migrations
                migration_manager.migrate_to_latest()
                print("✅ All migrations applied")
            else:
                # Check migration status
                status = migration_manager.get_migration_status()
                if status.get('pending_count', 0) > 0:
                    print(f"Found {status['pending_count']} pending migrations")
                    migration_manager.migrate_to_latest()
                    print("✅ Migrations completed")
                else:
                    print("✅ Database is up to date")
        
        # Set up sample data for development
        if not args.no_sample_data and args.environment == "development":
            print("🔄 Setting up development data...")
            setup_development_data(create_sample_user=True)
            print("✅ Development data created")
        
        # Display database info
        print("\n📊 Database Information:")
        db_info = db_manager.get_database_info()
        print(f"Status: {db_info.get('status', 'unknown')}")
        print(f"Type: {db_info.get('database_type', 'unknown')}")
        print(f"Tables: {db_info.get('table_count', 0)}")
        
        if args.environment == "development":
            print(f"Sample user: demo@autoapplyer.com")
        
        print("\n🎉 Database initialization completed successfully!")
        
        # Usage instructions
        print("\n💡 Next steps:")
        if args.environment == "development":
            print("  • Run: streamlit run app.py")
            print("  • Login with: demo@autoapplyer.com")
        
        print("  • Check database status: python database/init_db.py --environment", args.environment)
        print("  • Create backup: python -c \"from database.utilities import BackupManager; BackupManager().create_backup()\"")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        print(f"\n❌ Error: {e}")
        return 1


def check_status():
    """Check database status without making changes."""
    try:
        print("📊 Database Status Check")
        print("=" * 30)
        
        # Try to get database manager
        try:
            from database.connection import get_database_manager
            db_manager = get_database_manager()
            
            db_info = db_manager.get_database_info()
            print(f"Status: {db_info.get('status', 'unknown')}")
            print(f"Environment: {db_manager.config.environment}")
            print(f"Type: {db_info.get('database_type', 'unknown')}")
            print(f"Tables: {db_info.get('table_count', 0)}")
            
            if db_info.get('tables'):
                print(f"Table list: {', '.join(db_info['tables'])}")
            
        except Exception as e:
            print(f"Database not initialized: {e}")
            print("Run: python database/init_db.py --environment development")
            return
        
        # Check migration status
        try:
            migration_manager = MigrationManager()
            status = migration_manager.get_migration_status()
            
            print(f"\nMigrations:")
            print(f"  Applied: {status.get('applied_count', 0)}")
            print(f"  Pending: {status.get('pending_count', 0)}")
            print(f"  Current version: {status.get('current_version', 'none')}")
            
        except Exception as e:
            print(f"Migration check failed: {e}")
        
        # Check for sample data
        try:
            sample_user = DatabaseUtils.get_user_by_email("demo@autoapplyer.com")
            if sample_user:
                print(f"\nSample user: {sample_user.full_name} ({sample_user.email})")
                apps = DatabaseUtils.get_user_applications(sample_user.id, limit=1)
                print(f"Sample applications: {len(apps)}")
            else:
                print("\nNo sample user found")
                
        except Exception as e:
            print(f"Sample data check failed: {e}")
            
    except Exception as e:
        print(f"Status check failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_status()
    else:
        exit_code = main()
        sys.exit(exit_code) 