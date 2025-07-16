#!/usr/bin/env python3
"""
Auto Applyer - Database Migration Unit Tests

Comprehensive test suite for the production database migration system.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.production_migration import ProductionMigrationManager
from database.models import Base, User, UserPreferences, JobApplication, Activity, ApplicationStatus, ActivityType
from database.connection import DatabaseConfig
from utils.errors import DatabaseError, MigrationError


class TestProductionMigrationManager:
    """Test suite for ProductionMigrationManager."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_migration.db"
        yield str(db_path)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def migration_manager(self):
        """Create a migration manager instance."""
        return ProductionMigrationManager("testing")
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for migration testing."""
        return {
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
                },
                {
                    "email": "demo@autoapplyer.com",
                    "username": "demo",
                    "first_name": "Demo",
                    "last_name": "User",
                    "location": "Johannesburg, South Africa",
                    "job_title": "Help Desk Analyst",
                    "experience_years": 2,
                    "skills": ["Customer Service", "Technical Support", "Troubleshooting"],
                    "is_active": True,
                    "is_verified": True
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
                    "status": ApplicationStatus.APPLIED,
                    "source": "linkedin",
                    "salary_min": 30000,
                    "salary_max": 40000,
                    "job_type": "Full-time",
                    "is_remote": False,
                    "easy_apply": True,
                    "match_score": 85.5
                },
                {
                    "user_email": "demo@autoapplyer.com",
                    "job_title": "Help Desk Analyst",
                    "company": "SupportPro Ltd.",
                    "location": "Johannesburg, South Africa",
                    "job_description": "Customer service focused help desk role",
                    "job_url": "https://example.com/job/456",
                    "application_date": "2024-01-16T14:30:00",
                    "status": ApplicationStatus.INTERVIEW_SCHEDULED,
                    "source": "indeed",
                    "salary_min": 25000,
                    "salary_max": 35000,
                    "job_type": "Full-time",
                    "is_remote": True,
                    "easy_apply": False,
                    "match_score": 92.0
                }
            ],
            "preferences": [
                {
                    "user_email": "test@example.com",
                    "preferred_job_titles": ["IT Support Specialist", "Help Desk Analyst"],
                    "preferred_locations": ["Cape Town", "Remote"],
                    "preferred_job_types": ["Full-time", "Contract"],
                    "salary_min": 30000,
                    "salary_max": 45000,
                    "salary_currency": "ZAR",
                    "remote_work_preference": True,
                    "max_results_per_search": 50,
                    "auto_apply_enabled": False,
                    "email_notifications": True,
                    "application_reminders": True,
                    "daily_job_alerts": False,
                    "ai_suggestions_enabled": True,
                    "ats_analysis_enabled": True
                }
            ],
            "activities": [
                {
                    "user_email": "test@example.com",
                    "activity_type": ActivityType.APPLICATION_CREATED,
                    "title": "Applied to IT Support Specialist at TechCorp Inc.",
                    "description": "Submitted application for IT Support Specialist position",
                    "entity_type": "application",
                    "entity_id": 1,
                    "activity_metadata": {"company": "TechCorp Inc.", "status": "applied"},
                    "created_at": "2024-01-15T10:00:00"
                },
                {
                    "user_email": "demo@autoapplyer.com",
                    "activity_type": ActivityType.RESUME_UPLOADED,
                    "title": "Uploaded resume",
                    "description": "Successfully uploaded resume for job applications",
                    "entity_type": "resume",
                    "entity_id": 1,
                    "activity_metadata": {"filename": "demo_resume.pdf", "file_size": 1024000},
                    "created_at": "2024-01-16T09:15:00"
                }
            ]
        }
    
    def test_initialization(self, migration_manager):
        """Test migration manager initialization."""
        assert migration_manager.environment == "testing"
        assert migration_manager.db_manager is None
        assert migration_manager.backup_dir.exists()
    
    def test_initialize_database_sqlite(self, migration_manager, temp_db_path):
        """Test database initialization with SQLite."""
        database_url = f"sqlite:///{temp_db_path}"
        
        migration_manager.initialize_database(database_url)
        
        assert migration_manager.db_manager is not None
        assert migration_manager.db_manager.config.database_url == database_url
        assert migration_manager.db_manager.config.environment == "testing"
    
    @patch('database.production_migration.get_database_manager')
    def test_initialize_database_error(self, mock_get_manager, migration_manager):
        """Test database initialization error handling."""
        mock_get_manager.side_effect = Exception("Database connection failed")
        
        with pytest.raises(DatabaseError, match="Database initialization failed"):
            migration_manager.initialize_database("sqlite:///test.db")
    
    def test_create_backup_sqlite(self, migration_manager, temp_db_path):
        """Test SQLite backup creation."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create the database file
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Create backup
        backup_path = migration_manager.create_backup("test_backup")
        
        assert Path(backup_path).exists()
        assert backup_path.endswith("test_backup.sql")
        
        # Verify backup file size
        assert Path(backup_path).stat().st_size > 0
    
    @patch('subprocess.run')
    def test_create_backup_postgresql(self, mock_run, migration_manager):
        """Test PostgreSQL backup creation."""
        # Mock successful pg_dump
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Initialize with PostgreSQL URL
        database_url = "postgresql://user:pass@localhost:5432/testdb"
        migration_manager.initialize_database(database_url)
        
        # Create backup
        backup_path = migration_manager.create_backup("pg_backup")
        
        assert mock_run.called
        assert backup_path.endswith("pg_backup.sql")
    
    @patch('subprocess.run')
    def test_create_backup_postgresql_error(self, mock_run, migration_manager):
        """Test PostgreSQL backup error handling."""
        # Mock failed pg_dump
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Connection failed"
        
        database_url = "postgresql://user:pass@localhost:5432/testdb"
        migration_manager.initialize_database(database_url)
        
        with pytest.raises(DatabaseError, match="pg_dump failed"):
            migration_manager.create_backup()
    
    def test_migrate_users(self, migration_manager, temp_db_path, sample_data):
        """Test user migration functionality."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Migrate users
        with migration_manager.db_manager.get_session() as session:
            migration_manager._migrate_users(session, sample_data["users"])
            session.commit()
            
            # Verify users were created
            users = session.query(User).all()
            assert len(users) == 2
            
            # Check first user
            user1 = session.query(User).filter_by(email="test@example.com").first()
            assert user1 is not None
            assert user1.first_name == "Test"
            assert user1.last_name == "User"
            assert user1.job_title == "IT Support Specialist"
            assert user1.experience_years == 3
            assert user1.skills == ["Windows 10", "Active Directory", "Office 365"]
            
            # Check second user
            user2 = session.query(User).filter_by(email="demo@autoapplyer.com").first()
            assert user2 is not None
            assert user2.first_name == "Demo"
            assert user2.is_verified is True
    
    def test_migrate_users_duplicate_handling(self, migration_manager, temp_db_path, sample_data):
        """Test user migration with duplicate handling."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Migrate users twice
        with migration_manager.db_manager.get_session() as session:
            migration_manager._migrate_users(session, sample_data["users"])
            session.commit()
            
            # Try to migrate again (should skip duplicates)
            migration_manager._migrate_users(session, sample_data["users"])
            session.commit()
            
            # Should still have only 2 users
            users = session.query(User).all()
            assert len(users) == 2
    
    def test_migrate_applications(self, migration_manager, temp_db_path, sample_data):
        """Test application migration functionality."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Create users first
        with migration_manager.db_manager.get_session() as session:
            migration_manager._migrate_users(session, sample_data["users"])
            session.commit()
            
            # Migrate applications
            migration_manager._migrate_applications(session, sample_data["applications"])
            session.commit()
            
            # Verify applications were created
            applications = session.query(JobApplication).all()
            assert len(applications) == 2
            
            # Check first application
            app1 = session.query(JobApplication).filter_by(job_title="IT Support Specialist").first()
            assert app1 is not None
            assert app1.company == "TechCorp Inc."
            assert app1.location == "Cape Town, South Africa"
            assert app1.status.value == "applied"
            assert app1.source == "linkedin"
            assert app1.salary_min == 30000
            assert app1.salary_max == 40000
            assert app1.match_score == 85.5
            
            # Check user relationship
            assert app1.user.email == "test@example.com"
    
    def test_migrate_preferences(self, migration_manager, temp_db_path, sample_data):
        """Test preferences migration functionality."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Create users first
        with migration_manager.db_manager.get_session() as session:
            migration_manager._migrate_users(session, sample_data["users"])
            session.commit()
            
            # Migrate preferences
            migration_manager._migrate_preferences(session, sample_data["preferences"])
            session.commit()
            
            # Verify preferences were created
            preferences = session.query(UserPreferences).all()
            assert len(preferences) == 1
            
            # Check preferences
            prefs = preferences[0]
            assert prefs.user.email == "test@example.com"
            assert prefs.preferred_job_titles == ["IT Support Specialist", "Help Desk Analyst"]
            assert prefs.preferred_locations == ["Cape Town", "Remote"]
            assert prefs.salary_min == 30000
            assert prefs.salary_max == 45000
            assert prefs.salary_currency == "ZAR"
            assert prefs.remote_work_preference is True
            assert prefs.auto_apply_enabled is False
    
    def test_migrate_activities(self, migration_manager, temp_db_path, sample_data):
        """Test activities migration functionality."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Create users first
        with migration_manager.db_manager.get_session() as session:
            migration_manager._migrate_users(session, sample_data["users"])
            session.commit()
            
            # Migrate activities
            migration_manager._migrate_activities(session, sample_data["activities"])
            session.commit()
            
            # Verify activities were created
            activities = session.query(Activity).all()
            assert len(activities) == 2
            
            # Check first activity
            activity1 = activities[0]
            assert activity1.activity_type.value == "application_created"
            assert activity1.title == "Applied to IT Support Specialist at TechCorp Inc."
            assert activity1.entity_type == "application"
            assert activity1.entity_id == 1
            assert activity1.activity_metadata["company"] == "TechCorp Inc."
            
            # Check user relationship
            assert activity1.user.email == "test@example.com"
    
    def test_migrate_in_memory_to_persistent(self, migration_manager, temp_db_path, sample_data):
        """Test complete in-memory to persistent migration."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Perform complete migration
        migration_manager.migrate_in_memory_to_persistent(sample_data)
        
        # Verify all data was migrated
        with migration_manager.db_manager.get_session() as session:
            users = session.query(User).all()
            applications = session.query(JobApplication).all()
            preferences = session.query(UserPreferences).all()
            activities = session.query(Activity).all()
            
            assert len(users) == 2
            assert len(applications) == 2
            assert len(preferences) == 1
            assert len(activities) == 2
    
    def test_verify_migration(self, migration_manager, temp_db_path, sample_data):
        """Test migration verification."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Migrate data
        migration_manager.migrate_in_memory_to_persistent(sample_data)
        
        # Verify migration
        verification = migration_manager.verify_migration()
        
        assert verification['success'] is True
        assert verification['user_count'] == 2
        assert verification['application_count'] == 2
        assert verification['preference_count'] == 1
        assert verification['activity_count'] == 2
        assert verification['environment'] == "testing"
        assert verification['database_url'] == database_url
    
    def test_verify_migration_missing_tables(self, migration_manager, temp_db_path):
        """Test migration verification with missing tables."""
        # Initialize database without creating tables
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Verify migration (should fail)
        verification = migration_manager.verify_migration()
        
        assert verification['success'] is False
        assert len(verification['missing_tables']) > 0
        assert 'users' in verification['missing_tables']
        assert 'job_applications' in verification['missing_tables']
    
    @patch('database.production_migration.shutil.copy2')
    def test_rollback_sqlite(self, mock_copy, migration_manager, temp_db_path):
        """Test SQLite rollback functionality."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create backup file
        backup_path = temp_db_path + ".backup"
        with open(backup_path, 'w') as f:
            f.write("backup data")
        
        # Rollback
        migration_manager.rollback_migration(backup_path)
        
        # Verify copy was called
        mock_copy.assert_called_once()
    
    @patch('subprocess.run')
    def test_rollback_postgresql(self, mock_run, migration_manager):
        """Test PostgreSQL rollback functionality."""
        # Mock successful commands
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Initialize with PostgreSQL URL
        database_url = "postgresql://user:pass@localhost:5432/testdb"
        migration_manager.initialize_database(database_url)
        
        # Create backup file
        backup_path = "/tmp/test_backup.sql"
        with open(backup_path, 'w') as f:
            f.write("backup data")
        
        # Rollback
        migration_manager.rollback_migration(backup_path)
        
        # Verify commands were called
        assert mock_run.call_count >= 3  # drop, create, restore
    
    def test_error_handling_missing_user(self, migration_manager, temp_db_path):
        """Test error handling when migrating data for non-existent user."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Try to migrate application for non-existent user
        applications_data = [{
            "user_email": "nonexistent@example.com",
            "job_title": "Test Job",
            "company": "Test Company",
            "application_date": "2024-01-15T10:00:00",
            "status": "applied"
        }]
        
        with migration_manager.db_manager.get_session() as session:
            # Should log warning but not fail
            migration_manager._migrate_applications(session, applications_data)
            session.commit()
            
            # No applications should be created
            applications = session.query(JobApplication).all()
            assert len(applications) == 0
    
    def test_data_integrity(self, migration_manager, temp_db_path, sample_data):
        """Test data integrity after migration."""
        # Initialize database
        database_url = f"sqlite:///{temp_db_path}"
        migration_manager.initialize_database(database_url)
        
        # Create tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Migrate data
        migration_manager.migrate_in_memory_to_persistent(sample_data)
        
        # Verify data integrity
        with migration_manager.db_manager.get_session() as session:
            # Check user-application relationships
            user = session.query(User).filter_by(email="test@example.com").first()
            assert user is not None
            
            applications = session.query(JobApplication).filter_by(user_id=user.id).all()
            assert len(applications) == 1
            assert applications[0].job_title == "IT Support Specialist"
            
            # Check user-preferences relationships
            preferences = session.query(UserPreferences).filter_by(user_id=user.id).first()
            assert preferences is not None
            assert preferences.salary_currency == "ZAR"
            
            # Check user-activities relationships
            activities = session.query(Activity).filter_by(user_id=user.id).all()
            assert len(activities) == 1
            assert activities[0].activity_type.value == "application_created"


class TestMigrationCLI:
    """Test suite for migration CLI functionality."""
    
    @patch('database.production_migration.ProductionMigrationManager')
    def test_cli_initialization(self, mock_manager_class):
        """Test CLI initialization."""
        from database.production_migration import main
        
        # Mock the manager
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        # Mock sys.argv
        with patch('sys.argv', ['production_migration.py', '--environment', 'testing']):
            with patch('sys.exit') as mock_exit:
                main()
                mock_exit.assert_called_with(0)
    
    @patch('database.production_migration.ProductionMigrationManager')
    def test_cli_backup_option(self, mock_manager_class):
        """Test CLI backup option."""
        from database.production_migration import main
        
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        with patch('sys.argv', ['production_migration.py', '--backup']):
            with patch('sys.exit') as mock_exit:
                main()
                
                # Verify backup was called
                mock_manager.create_backup.assert_called_once()
                mock_exit.assert_called_with(0)
    
    @patch('database.production_migration.ProductionMigrationManager')
    def test_cli_verify_option(self, mock_manager_class):
        """Test CLI verify option."""
        from database.production_migration import main
        
        mock_manager = Mock()
        mock_manager.verify_migration.return_value = {'success': True}
        mock_manager_class.return_value = mock_manager
        
        with patch('sys.argv', ['production_migration.py', '--verify']):
            with patch('sys.exit') as mock_exit:
                main()
                
                # Verify verification was called
                mock_manager.verify_migration.assert_called_once()
                mock_exit.assert_called_with(0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 