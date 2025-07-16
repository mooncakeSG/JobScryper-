#!/usr/bin/env python3
"""
Auto Applyer - Production Database Migration System

Handles the transition from in-memory storage to persistent database storage
with proper versioning, rollback capabilities, and data migration utilities.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import argparse
import sqlite3
import psycopg2
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import get_database_manager, DatabaseConfig
from database.models import Base, User, UserPreferences, JobApplication, Resume, Activity, ActivityType
from database.migrations import MigrationManager
from utils.logging_config import get_logger
from utils.errors import DatabaseError, MigrationError

logger = get_logger(__name__)


class ProductionMigrationManager:
    """Manages production database migrations and data transitions."""
    
    def __init__(self, environment: str = "production"):
        """Initialize the production migration manager."""
        self.environment = environment
        self.db_manager = None
        self.migration_manager = MigrationManager()
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def initialize_database(self, database_url: Optional[str] = None) -> None:
        """Initialize the production database."""
        try:
            logger.info(f"Initializing production database for environment: {self.environment}")
            
            # Set environment variable
            os.environ['ENVIRONMENT'] = self.environment
            
            # Initialize database manager
            if database_url:
                os.environ['DATABASE_URL'] = database_url
            
            # Always reload config to pick up the new DATABASE_URL
            from database.connection import DatabaseManager, DatabaseConfig
            config = DatabaseConfig(environment=self.environment)
            self.db_manager = DatabaseManager(config)
            self.db_manager.initialize()
            
            # Create tables if they don't exist
            self.db_manager.create_tables(drop_existing=False)
            
            logger.info(f"Database initialized: {self.db_manager.config.config.get('database_url')}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
    
    def create_backup(self, backup_name: Optional[str] = None) -> Optional[str]:
        """Create a backup of the current database. Returns path or None if skipped."""
        try:
            db_url = self.db_manager.config.config['database_url']
            if db_url == 'sqlite:///:memory:':
                logger.warning("Skipping backup: in-memory SQLite database cannot be backed up as a file.")
                return None
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{self.environment}_{timestamp}"
            backup_path = self.backup_dir / f"{backup_name}.sql"
            logger.info(f"Creating backup: {backup_path}")
            if db_url.startswith('sqlite'):
                self._backup_sqlite(backup_path)
            else:
                self._backup_postgresql(backup_path)
            logger.info(f"Backup created successfully: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise DatabaseError(f"Backup creation failed: {e}")
    
    def _backup_sqlite(self, backup_path: Path) -> None:
        """Create SQLite backup."""
        source_db = self.db_manager.config.config['database_url'].replace('sqlite:///', '')
        shutil.copy2(source_db, backup_path)
    
    def _backup_postgresql(self, backup_path: Path) -> None:
        """Create PostgreSQL backup."""
        # Extract connection details from URL
        url = self.db_manager.config.config['database_url']
        # Format: postgresql://user:pass@host:port/dbname
        
        # Use pg_dump for PostgreSQL backup
        import subprocess
        
        # Extract components from URL
        if url.startswith('postgresql://'):
            url = url.replace('postgresql://', '')
        
        # Parse URL components
        auth_part, rest = url.split('@', 1)
        user, password = auth_part.split(':', 1)
        host_port, dbname = rest.split('/', 1)
        
        if ':' in host_port:
            host, port = host_port.split(':', 1)
        else:
            host, port = host_port, '5432'
        
        # Set environment variables for pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Run pg_dump
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', dbname,
            '-f', str(backup_path),
            '--no-password'
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise DatabaseError(f"pg_dump failed: {result.stderr}")
    
    def migrate_in_memory_to_persistent(self, source_data: Dict[str, Any]) -> None:
        """Migrate data from in-memory storage to persistent database."""
        try:
            logger.info("Starting migration from in-memory to persistent storage")
            
            with self.db_manager.get_session() as session:
                # Migrate users
                if 'users' in source_data:
                    self._migrate_users(session, source_data['users'])
                
                # Migrate applications
                if 'applications' in source_data:
                    self._migrate_applications(session, source_data['applications'])
                
                # Migrate preferences
                if 'preferences' in source_data:
                    self._migrate_preferences(session, source_data['preferences'])
                
                # Migrate activities
                if 'activities' in source_data:
                    self._migrate_activities(session, source_data['activities'])
                
                session.commit()
                logger.info("Data migration completed successfully")
                
        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            raise MigrationError(f"Data migration failed: {e}")
    
    def _migrate_users(self, session: Session, users_data: List[Dict[str, Any]]) -> None:
        """Migrate users from in-memory to database."""
        logger.info(f"Migrating {len(users_data)} users")
        
        for user_data in users_data:
            try:
                # Check if user already exists
                existing_user = session.query(User).filter_by(email=user_data['email']).first()
                if existing_user:
                    logger.info(f"User {user_data['email']} already exists, skipping")
                    continue
                
                # Create new user
                user = User(
                    email=user_data['email'],
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    phone=user_data.get('phone'),
                    location=user_data.get('location'),
                    job_title=user_data.get('job_title'),
                    experience_years=user_data.get('experience_years'),
                    skills=user_data.get('skills'),
                    is_active=user_data.get('is_active', True),
                    is_verified=user_data.get('is_verified', False),
                    linkedin_username=user_data.get('linkedin_username')
                )
                
                session.add(user)
                session.flush()  # Get the user ID
                
                logger.info(f"Migrated user: {user.email} (ID: {user.id})")
                
            except Exception as e:
                logger.error(f"Failed to migrate user {user_data.get('email', 'unknown')}: {e}")
                session.rollback()
                raise
    
    def _migrate_applications(self, session: Session, applications_data: List[Dict[str, Any]]) -> None:
        """Migrate job applications from in-memory to database."""
        logger.info(f"Migrating {len(applications_data)} applications")
        
        for app_data in applications_data:
            try:
                # Find user by email
                user = session.query(User).filter_by(email=app_data['user_email']).first()
                if not user:
                    logger.warning(f"User {app_data['user_email']} not found, skipping application")
                    continue
                
                # Create application
                application = JobApplication(
                    user_id=user.id,
                    job_title=app_data['job_title'],
                    company=app_data['company'],
                    location=app_data.get('location'),
                    job_description=app_data.get('job_description'),
                    job_url=app_data.get('job_url'),
                    application_date=datetime.fromisoformat(app_data['application_date']),
                    status=app_data['status'],
                    source=app_data.get('source'),
                    salary_min=app_data.get('salary_min'),
                    salary_max=app_data.get('salary_max'),
                    job_type=app_data.get('job_type'),
                    is_remote=app_data.get('is_remote', False),
                    easy_apply=app_data.get('easy_apply', False),
                    applied_via=app_data.get('applied_via'),
                    cover_letter_used=app_data.get('cover_letter_used', False),
                    match_score=app_data.get('match_score'),
                    ats_score=app_data.get('ats_score'),
                    ai_analysis=app_data.get('ai_analysis')
                )
                
                session.add(application)
                logger.info(f"Migrated application: {application.job_title} at {application.company}")
                
            except Exception as e:
                logger.error(f"Failed to migrate application {app_data.get('job_title', 'unknown')}: {e}")
                session.rollback()
                raise
    
    def _migrate_preferences(self, session: Session, preferences_data: List[Dict[str, Any]]) -> None:
        """Migrate user preferences from in-memory to database."""
        logger.info(f"Migrating {len(preferences_data)} preference sets")
        
        for pref_data in preferences_data:
            try:
                # Find user by email
                user = session.query(User).filter_by(email=pref_data['user_email']).first()
                if not user:
                    logger.warning(f"User {pref_data['user_email']} not found, skipping preferences")
                    continue
                
                # Check if preferences already exist
                existing_prefs = session.query(UserPreferences).filter_by(user_id=user.id).first()
                if existing_prefs:
                    logger.info(f"Preferences for user {user.email} already exist, updating")
                    # Update existing preferences
                    for key, value in pref_data.items():
                        if key != 'user_email' and hasattr(existing_prefs, key):
                            setattr(existing_prefs, key, value)
                else:
                    # Create new preferences
                    preferences = UserPreferences(
                        user_id=user.id,
                        preferred_job_titles=pref_data.get('preferred_job_titles'),
                        preferred_locations=pref_data.get('preferred_locations'),
                        preferred_job_types=pref_data.get('preferred_job_types'),
                        salary_min=pref_data.get('salary_min'),
                        salary_max=pref_data.get('salary_max'),
                        salary_currency=pref_data.get('salary_currency', 'USD'),
                        remote_work_preference=pref_data.get('remote_work_preference', False),
                        max_results_per_search=pref_data.get('max_results_per_search', 50),
                        auto_apply_enabled=pref_data.get('auto_apply_enabled', False),
                        job_sources=pref_data.get('job_sources'),
                        email_notifications=pref_data.get('email_notifications', True),
                        application_reminders=pref_data.get('application_reminders', True),
                        daily_job_alerts=pref_data.get('daily_job_alerts', False),
                        ai_suggestions_enabled=pref_data.get('ai_suggestions_enabled', True),
                        ats_analysis_enabled=pref_data.get('ats_analysis_enabled', True),
                        auto_resume_optimization=pref_data.get('auto_resume_optimization', False)
                    )
                    session.add(preferences)
                
                logger.info(f"Migrated preferences for user: {user.email}")
                
            except Exception as e:
                logger.error(f"Failed to migrate preferences for {pref_data.get('user_email', 'unknown')}: {e}")
                session.rollback()
                raise
    
    def _migrate_activities(self, session: Session, activities_data: List[Dict[str, Any]]) -> None:
        """Migrate activities from in-memory to database."""
        logger.info(f"Migrating {len(activities_data)} activities")
        for act_data in activities_data:
            try:
                user = session.query(User).filter_by(email=act_data['user_email']).first()
                if not user:
                    logger.warning(f"User {act_data['user_email']} not found, skipping activity")
                    continue
                # Map string to ActivityType enum if needed
                activity_type = act_data['activity_type']
                if isinstance(activity_type, str):
                    try:
                        activity_type = ActivityType(activity_type)
                    except ValueError:
                        logger.error(f"Invalid activity_type: {activity_type}, skipping activity")
                        continue
                activity = Activity(
                    user_id=user.id,
                    activity_type=activity_type,
                    title=act_data['title'],
                    description=act_data.get('description'),
                    entity_type=act_data.get('entity_type'),
                    entity_id=act_data.get('entity_id'),
                    activity_metadata=act_data.get('activity_metadata'),
                    created_at=datetime.fromisoformat(act_data['created_at']) if 'created_at' in act_data else None
                )
                session.add(activity)
                logger.info(f"Migrated activity: {activity.title}")
            except Exception as e:
                logger.error(f"Failed to migrate activity {act_data.get('title', 'unknown')}: {e}")
                session.rollback()
                raise
        session.commit()
    
    def run_migrations(self) -> None:
        """Run all pending database migrations."""
        try:
            logger.info("Running database migrations")
            
            # Check migration status
            status = self.migration_manager.get_migration_status()
            logger.info(f"Migration status: {status}")
            
            if status.get('pending_count', 0) > 0:
                logger.info(f"Found {status['pending_count']} pending migrations")
                self.migration_manager.migrate_to_latest()
                logger.info("All migrations completed successfully")
            else:
                logger.info("Database is up to date")
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise MigrationError(f"Migration failed: {e}")
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify that the migration was successful."""
        try:
            logger.info("Verifying migration")
            
            with self.db_manager.get_session() as session:
                # Check table existence
                inspector = inspect(self.db_manager.engine)
                tables = inspector.get_table_names()
                
                expected_tables = [
                    'users', 'user_preferences', 'job_applications', 
                    'resumes', 'search_history', 'ai_analysis_cache',
                    'system_settings', 'saved_jobs', 'activities'
                ]
                
                missing_tables = [table for table in expected_tables if table not in tables]
                
                # Count records in key tables
                user_count = session.query(User).count()
                application_count = session.query(JobApplication).count()
                preference_count = session.query(UserPreferences).count()
                activity_count = session.query(Activity).count()
                
                verification_result = {
                    'success': len(missing_tables) == 0,
                    'tables_found': len(tables),
                    'expected_tables': len(expected_tables),
                    'missing_tables': missing_tables,
                    'user_count': user_count,
                    'application_count': application_count,
                    'preference_count': preference_count,
                    'activity_count': activity_count,
                    'database_url': self.db_manager.config.config['database_url'],
                    'environment': self.environment
                }
                
                logger.info(f"Migration verification completed: {verification_result}")
                return verification_result
                
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            raise MigrationError(f"Verification failed: {e}")
    
    def rollback_migration(self, backup_path: str) -> None:
        """Rollback migration using a backup."""
        try:
            logger.info(f"Rolling back migration using backup: {backup_path}")
            
            if not Path(backup_path).exists():
                raise MigrationError(f"Backup file not found: {backup_path}")
            
            # Restore from backup
            if self.db_manager.config.config['database_url'].startswith('sqlite'):
                self._restore_sqlite_backup(backup_path)
            else:
                self._restore_postgresql_backup(backup_path)
            
            logger.info("Migration rollback completed successfully")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise MigrationError(f"Rollback failed: {e}")
    
    def _restore_sqlite_backup(self, backup_path: str) -> None:
        """Restore SQLite database from backup."""
        current_db = self.db_manager.config.config['database_url'].replace('sqlite:///', '')
        shutil.copy2(backup_path, current_db)
    
    def _restore_postgresql_backup(self, backup_path: str) -> None:
        """Restore PostgreSQL database from backup."""
        # Extract connection details from URL
        url = self.db_manager.config.config['database_url']
        
        if url.startswith('postgresql://'):
            url = url.replace('postgresql://', '')
        
        auth_part, rest = url.split('@', 1)
        user, password = auth_part.split(':', 1)
        host_port, dbname = rest.split('/', 1)
        
        if ':' in host_port:
            host, port = host_port.split(':', 1)
        else:
            host, port = host_port, '5432'
        
        # Set environment variables for psql
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Drop and recreate database
        import subprocess
        
        # Drop database
        drop_cmd = [
            'psql', '-h', host, '-p', port, '-U', user,
            '-d', 'postgres', '-c', f'DROP DATABASE IF EXISTS {dbname}'
        ]
        
        result = subprocess.run(drop_cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"Failed to drop database: {result.stderr}")
        
        # Create database
        create_cmd = [
            'psql', '-h', host, '-p', port, '-U', user,
            '-d', 'postgres', '-c', f'CREATE DATABASE {dbname}'
        ]
        
        result = subprocess.run(create_cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            raise MigrationError(f"Failed to create database: {result.stderr}")
        
        # Restore from backup
        restore_cmd = [
            'psql', '-h', host, '-p', port, '-U', user,
            '-d', dbname, '-f', backup_path
        ]
        
        result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            raise MigrationError(f"Failed to restore database: {result.stderr}")


def main():
    """Main migration script."""
    parser = argparse.ArgumentParser(description="Auto Applyer Production Database Migration")
    
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "testing", "production"],
        default="production",
        help="Target environment"
    )
    
    parser.add_argument(
        "--database-url", "-d",
        help="Database URL (overrides environment variable)"
    )
    
    parser.add_argument(
        "--backup", "-b",
        action="store_true",
        help="Create backup before migration"
    )
    
    parser.add_argument(
        "--migrate-data",
        action="store_true",
        help="Migrate data from in-memory to persistent storage"
    )
    
    parser.add_argument(
        "--source-data",
        help="Path to JSON file containing in-memory data to migrate"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify migration after completion"
    )
    
    parser.add_argument(
        "--rollback",
        help="Rollback migration using specified backup file"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force operations without confirmation"
    )
    
    args = parser.parse_args()
    
    print("🗄️  Auto Applyer Production Database Migration")
    print("=" * 60)
    
    try:
        # Initialize migration manager
        migration_manager = ProductionMigrationManager(args.environment)
        
        # Handle rollback
        if args.rollback:
            print(f"🔄 Rolling back migration using: {args.rollback}")
            migration_manager.initialize_database(args.database_url)
            migration_manager.rollback_migration(args.rollback)
            print("✅ Rollback completed successfully")
            return 0
        
        # Initialize database
        print(f"🔄 Initializing database for environment: {args.environment}")
        migration_manager.initialize_database(args.database_url)
        print("✅ Database initialized")
        
        # Create backup if requested
        backup_path = None
        if args.backup:
            print("📦 Creating backup...")
            backup_path = migration_manager.create_backup()
            if backup_path:
                print(f"✅ Backup created: {backup_path}")
            else:
                print("⚠️ Skipped backup: in-memory SQLite database cannot be backed up as a file.")
        
        # Run migrations
        print("🔄 Running database migrations...")
        migration_manager.run_migrations()
        print("✅ Migrations completed")
        
        # Migrate data if requested
        if args.migrate_data:
            if not args.source_data:
                print("❌ Error: --source-data required for data migration")
                return 1
            
            print(f"🔄 Migrating data from: {args.source_data}")
            
            # Load source data
            with open(args.source_data, 'r') as f:
                source_data = json.load(f)
            
            migration_manager.migrate_in_memory_to_persistent(source_data)
            print("✅ Data migration completed")
        
        # Verify migration
        if args.verify:
            print("🔍 Verifying migration...")
            verification = migration_manager.verify_migration()
            
            if verification['success']:
                print("✅ Migration verification passed")
                print(f"📊 Database contains:")
                print(f"   • {verification['user_count']} users")
                print(f"   • {verification['application_count']} applications")
                print(f"   • {verification['preference_count']} preference sets")
                print(f"   • {verification['activity_count']} activities")
            else:
                print("❌ Migration verification failed")
                print(f"Missing tables: {verification['missing_tables']}")
                return 1
        
        print("\n🎉 Production database migration completed successfully!")
        
        if backup_path:
            print(f"💾 Backup available at: {backup_path}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Migration cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 