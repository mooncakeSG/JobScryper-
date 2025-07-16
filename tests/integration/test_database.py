"""
Integration tests for the database system.

Tests database connections, models, utilities, migrations, and backup functionality.
"""

import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from database.connection import init_database, get_database_manager, cleanup_database
from database.models import User, UserPreferences, Resume, JobApplication, SearchHistory, ApplicationStatus
from database.utilities import DatabaseUtils, BackupManager
from database.migrations import MigrationManager
from utils.errors import DatabaseError, ValidationError


class TestDatabaseConnection:
    """Test database connection management."""
    
    def test_init_database_development(self):
        """Test database initialization in development mode."""
        # Clean up any existing database
        cleanup_database()
        
        # Initialize database
        db_manager = init_database("development", drop_existing=True)
        
        assert db_manager is not None
        assert db_manager.config.environment == "development"
        assert db_manager._initialized is True
        
        # Test database info
        db_info = db_manager.get_database_info()
        assert db_info["status"] == "connected"
        assert db_info["database_type"] == "sqlite"
        assert db_info["table_count"] > 0
        
        # Cleanup
        cleanup_database()
    
    def test_init_database_testing(self):
        """Test database initialization in testing mode."""
        cleanup_database()
        
        db_manager = init_database("testing", drop_existing=True)
        
        assert db_manager.config.environment == "testing"
        assert "memory" in db_manager.config.config["database_url"]
        
        cleanup_database()
    
    def test_session_management(self):
        """Test database session management."""
        cleanup_database()
        db_manager = init_database("testing", drop_existing=True)
        
        # Test regular session
        session = db_manager.get_session()
        assert session is not None
        session.close()
        
        # Test scoped session
        scoped_session = db_manager.get_scoped_session()
        assert scoped_session is not None
        
        # Test session scope context manager
        with db_manager.session_scope() as session:
            assert session is not None
            user = User(email="test@example.com", first_name="Test")
            session.add(user)
            # Session should auto-commit on success
        
        # Verify user was saved
        with db_manager.session_scope() as session:
            saved_user = session.query(User).filter_by(email="test@example.com").first()
            assert saved_user is not None
            assert saved_user.first_name == "Test"
        
        cleanup_database()


class TestDatabaseModels:
    """Test database models and relationships."""
    
    def setup_method(self):
        """Set up test database."""
        cleanup_database()
        self.db_manager = init_database("testing", drop_existing=True)
    
    def teardown_method(self):
        """Clean up after tests."""
        cleanup_database()
    
    def test_user_model_creation(self):
        """Test User model creation and basic operations."""
        with self.db_manager.session_scope() as session:
            user = User(
                email="test@example.com",
                first_name="Test",
                last_name="User",
                location="Cape Town",
                job_title="Developer",
                experience_years=5,
                skills=["Python", "SQL", "Git"]
            )
            session.add(user)
            session.commit()
            
            # Test user was created
            assert user.id is not None
            assert user.full_name == "Test User"
            assert user.skills == ["Python", "SQL", "Git"]
            
            # Test to_dict method
            user_dict = user.to_dict()
            assert user_dict["email"] == "test@example.com"
            assert user_dict["first_name"] == "Test"
            assert user_dict["skills"] == ["Python", "SQL", "Git"]
    
    def test_user_preferences_relationship(self):
        """Test User and UserPreferences relationship."""
        with self.db_manager.session_scope() as session:
            # Create user
            user = User(email="test@example.com", first_name="Test")
            session.add(user)
            session.flush()
            
            # Create preferences
            preferences = UserPreferences(
                user_id=user.id,
                preferred_job_titles=["Developer", "Engineer"],
                preferred_locations=["Cape Town", "Remote"],
                salary_min=50000,
                salary_max=100000,
                remote_work_preference=True
            )
            session.add(preferences)
            session.commit()
            
            # Test relationship
            assert user.preferences is not None
            assert user.preferences.preferred_job_titles == ["Developer", "Engineer"]
            assert user.preferences.remote_work_preference is True
            
            # Test reverse relationship
            assert preferences.user.email == "test@example.com"
    
    def test_resume_model(self):
        """Test Resume model."""
        with self.db_manager.session_scope() as session:
            # Create user
            user = User(email="test@example.com", first_name="Test")
            session.add(user)
            session.flush()
            
            # Create resume
            resume = Resume(
                user_id=user.id,
                filename="test_resume.pdf",
                file_path="/tmp/test_resume.pdf",
                file_size=1024,
                file_type="pdf",
                parsed_text="Test resume content",
                skills_extracted=["Python", "SQL"],
                experience_level="Mid-level"
            )
            session.add(resume)
            session.commit()
            
            # Test resume creation
            assert resume.id is not None
            assert resume.user.email == "test@example.com"
            assert resume.skills_extracted == ["Python", "SQL"]
            
            # Test to_dict method
            resume_dict = resume.to_dict()
            assert resume_dict["filename"] == "test_resume.pdf"
            assert resume_dict["file_type"] == "pdf"
            assert resume_dict["skills_extracted"] == ["Python", "SQL"]
    
    def test_job_application_model(self):
        """Test JobApplication model."""
        with self.db_manager.session_scope() as session:
            # Create user
            user = User(email="test@example.com", first_name="Test")
            session.add(user)
            session.flush()
            
            # Create job application
            application = JobApplication(
                user_id=user.id,
                job_title="Software Developer",
                company="TechCorp",
                location="Cape Town",
                job_description="Develop software solutions",
                status=ApplicationStatus.APPLIED,
                salary_min=60000,
                salary_max=80000,
                is_remote=True,
                match_score=85.5
            )
            session.add(application)
            session.commit()
            
            # Test application creation
            assert application.id is not None
            assert application.user.email == "test@example.com"
            assert application.status == ApplicationStatus.APPLIED
            assert application.salary_range == "R60,000 - R80,000"
            
            # Test to_dict method
            app_dict = application.to_dict()
            assert app_dict["job_title"] == "Software Developer"
            assert app_dict["company"] == "TechCorp"
            assert app_dict["status"] == "applied"
            assert app_dict["match_score"] == 85.5
    
    def test_search_history_model(self):
        """Test SearchHistory model."""
        with self.db_manager.session_scope() as session:
            # Create user
            user = User(email="test@example.com", first_name="Test")
            session.add(user)
            session.flush()
            
            # Create search history
            search = SearchHistory(
                user_id=user.id,
                job_title="Developer",
                location="Cape Town",
                keywords="Python Django",
                sources_searched=["linkedin", "indeed"],
                total_results=50,
                filtered_results=25,
                search_duration=2.5
            )
            session.add(search)
            session.commit()
            
            # Test search history creation
            assert search.id is not None
            assert search.user.email == "test@example.com"
            assert search.sources_searched == ["linkedin", "indeed"]
            
            # Test to_dict method
            search_dict = search.to_dict()
            assert search_dict["job_title"] == "Developer"
            assert search_dict["total_results"] == 50
            assert search_dict["search_duration"] == 2.5


class TestDatabaseUtils:
    """Test database utilities and high-level operations."""
    
    def setup_method(self):
        """Set up test database."""
        cleanup_database()
        self.db_manager = init_database("testing", drop_existing=True)
    
    def teardown_method(self):
        """Clean up after tests."""
        cleanup_database()
    
    def test_create_user_with_preferences(self):
        """Test creating user with default preferences."""
        # Create user
        user = DatabaseUtils.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            location="Cape Town",
            skills=["Python", "SQL"]
        )
        
        assert user is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.skills == ["Python", "SQL"]
        
        # Check preferences were created
        preferences = DatabaseUtils.get_user_preferences(user.id)
        assert preferences is not None
        assert preferences.user_id == user.id
        assert preferences.max_results_per_search == 50
        assert preferences.ai_suggestions_enabled is True
        
        # Test duplicate user creation
        with pytest.raises(ValidationError):
            DatabaseUtils.create_user(email="test@example.com")
    
    def test_user_crud_operations(self):
        """Test user CRUD operations."""
        # Create user
        user = DatabaseUtils.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Test get by email
        retrieved_user = DatabaseUtils.get_user_by_email("test@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        
        # Test get by ID
        retrieved_user = DatabaseUtils.get_user_by_id(user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        
        # Test update user
        updated_user = DatabaseUtils.update_user(
            user.id,
            job_title="Senior Developer",
            experience_years=5
        )
        assert updated_user.job_title == "Senior Developer"
        assert updated_user.experience_years == 5
        
        # Test non-existent user
        assert DatabaseUtils.get_user_by_email("nonexistent@example.com") is None
        assert DatabaseUtils.get_user_by_id(99999) is None
    
    def test_resume_operations(self):
        """Test resume operations."""
        # Create user
        user = DatabaseUtils.create_user(email="test@example.com", first_name="Test")
        
        # Add resume
        resume = DatabaseUtils.add_resume(
            user_id=user.id,
            filename="test_resume.pdf",
            file_path="/tmp/test_resume.pdf",
            file_size=1024,
            file_type="pdf",
            parsed_text="Test resume content",
            skills_extracted=["Python", "SQL"]
        )
        
        assert resume is not None
        assert resume.user_id == user.id
        assert resume.filename == "test_resume.pdf"
        assert resume.is_active is True
        
        # Test get user resumes
        resumes = DatabaseUtils.get_user_resumes(user.id)
        assert len(resumes) == 1
        assert resumes[0].filename == "test_resume.pdf"
        
        # Add another resume (should deactivate first)
        resume2 = DatabaseUtils.add_resume(
            user_id=user.id,
            filename="new_resume.pdf",
            file_path="/tmp/new_resume.pdf",
            file_size=2048,
            file_type="pdf"
        )
        
        # Check only active resume
        active_resumes = DatabaseUtils.get_user_resumes(user.id, active_only=True)
        assert len(active_resumes) == 1
        assert active_resumes[0].filename == "new_resume.pdf"
        
        # Check all resumes
        all_resumes = DatabaseUtils.get_user_resumes(user.id, active_only=False)
        assert len(all_resumes) == 2
    
    def test_job_application_operations(self):
        """Test job application operations."""
        # Create user
        user = DatabaseUtils.create_user(email="test@example.com", first_name="Test")
        
        # Add job application
        application = DatabaseUtils.add_job_application(
            user_id=user.id,
            job_title="Software Developer",
            company="TechCorp",
            location="Cape Town",
            job_description="Develop software",
            status=ApplicationStatus.APPLIED,
            salary_min=60000,
            salary_max=80000,
            match_score=85.5
        )
        
        assert application is not None
        assert application.user_id == user.id
        assert application.job_title == "Software Developer"
        assert application.status == ApplicationStatus.APPLIED
        
        # Test get user applications
        applications = DatabaseUtils.get_user_applications(user.id)
        assert len(applications) == 1
        assert applications[0].company == "TechCorp"
        
        # Test filter by status
        applied_apps = DatabaseUtils.get_user_applications(user.id, status=ApplicationStatus.APPLIED)
        assert len(applied_apps) == 1
        
        pending_apps = DatabaseUtils.get_user_applications(user.id, status=ApplicationStatus.PENDING)
        assert len(pending_apps) == 0
        
        # Test update application status
        updated_app = DatabaseUtils.update_application_status(
            application.id,
            ApplicationStatus.INTERVIEW_SCHEDULED,
            notes="Phone interview scheduled for tomorrow",
            interview_date=datetime.now(timezone.utc)
        )
        
        assert updated_app.status == ApplicationStatus.INTERVIEW_SCHEDULED
        assert updated_app.interview_notes == "Phone interview scheduled for tomorrow"
        assert updated_app.interview_date is not None
    
    def test_user_preferences_operations(self):
        """Test user preferences operations."""
        # Create user
        user = DatabaseUtils.create_user(email="test@example.com", first_name="Test")
        
        # Get default preferences
        preferences = DatabaseUtils.get_user_preferences(user.id)
        assert preferences is not None
        assert preferences.max_results_per_search == 50
        assert preferences.ai_suggestions_enabled is True
        
        # Update preferences
        updated_prefs = DatabaseUtils.update_user_preferences(
            user.id,
            preferred_job_titles=["Developer", "Engineer"],
            preferred_locations=["Cape Town", "Remote"],
            salary_min=70000,
            salary_max=120000,
            remote_work_preference=True,
            daily_job_alerts=True
        )
        
        assert updated_prefs.preferred_job_titles == ["Developer", "Engineer"]
        assert updated_prefs.preferred_locations == ["Cape Town", "Remote"]
        assert updated_prefs.salary_min == 70000
        assert updated_prefs.remote_work_preference is True
        assert updated_prefs.daily_job_alerts is True
    
    def test_application_statistics(self):
        """Test application statistics generation."""
        # Create user
        user = DatabaseUtils.create_user(email="test@example.com", first_name="Test")
        
        # Add multiple applications with different statuses
        DatabaseUtils.add_job_application(
            user_id=user.id, job_title="Job 1", company="Company 1",
            status=ApplicationStatus.APPLIED, match_score=80.0
        )
        DatabaseUtils.add_job_application(
            user_id=user.id, job_title="Job 2", company="Company 2",
            status=ApplicationStatus.INTERVIEW_SCHEDULED, match_score=90.0
        )
        DatabaseUtils.add_job_application(
            user_id=user.id, job_title="Job 3", company="Company 3",
            status=ApplicationStatus.REJECTED, match_score=70.0
        )
        
        # Get statistics
        stats = DatabaseUtils.get_application_statistics(user.id, days=30)
        
        assert stats["total_applications"] == 3
        assert stats["recent_applications"] == 3
        assert stats["status_breakdown"]["applied"] == 1
        assert stats["status_breakdown"]["interview_scheduled"] == 1
        assert stats["status_breakdown"]["rejected"] == 1
        assert stats["interview_count"] == 1
        assert stats["interview_rate"] == 33.3  # 1/3 * 100
        assert stats["average_match_score"] == 80.0  # (80 + 90 + 70) / 3
    
    def test_search_history_operations(self):
        """Test search history operations."""
        # Create user
        user = DatabaseUtils.create_user(email="test@example.com", first_name="Test")
        
        # Add search history
        search = DatabaseUtils.add_search_history(
            user_id=user.id,
            job_title="Developer",
            location="Cape Town",
            keywords="Python Django",
            sources_searched=["linkedin", "indeed"],
            total_results=50,
            filtered_results=25,
            search_duration=2.5
        )
        
        assert search is not None
        assert search.user_id == user.id
        assert search.job_title == "Developer"
        assert search.total_results == 50
        assert search.search_duration == 2.5


class TestMigrationManager:
    """Test database migration system."""
    
    def setup_method(self):
        """Set up test database."""
        cleanup_database()
        self.db_manager = init_database("testing", drop_existing=True)
        self.migration_manager = MigrationManager()
    
    def teardown_method(self):
        """Clean up after tests."""
        cleanup_database()
    
    def test_migration_status(self):
        """Test getting migration status."""
        status = self.migration_manager.get_migration_status()
        
        assert "total_migrations" in status
        assert "applied_count" in status
        assert "pending_count" in status
        assert "applied_migrations" in status
        assert "pending_migrations" in status
        
        # Initially no migrations should be applied
        assert status["applied_count"] == 0
        assert status["pending_count"] > 0
    
    def test_migrate_to_latest(self):
        """Test migrating to latest version."""
        # Check initial status
        initial_status = self.migration_manager.get_migration_status()
        assert initial_status["applied_count"] == 0
        
        # Migrate to latest
        result = self.migration_manager.migrate_to_latest()
        assert result is True
        
        # Check final status
        final_status = self.migration_manager.get_migration_status()
        assert final_status["applied_count"] > 0
        assert final_status["pending_count"] == 0
    
    def test_migrate_to_specific_version(self):
        """Test migrating to specific version."""
        # Migrate to version 001
        result = self.migration_manager.migrate_to_version("001")
        assert result is True
        
        # Check status
        status = self.migration_manager.get_migration_status()
        assert status["current_version"] == "001"
        assert status["applied_count"] == 1
    
    def test_rollback_migration(self):
        """Test rolling back migration."""
        # First apply migrations
        self.migration_manager.migrate_to_latest()
        
        # Get current status
        status = self.migration_manager.get_migration_status()
        applied_count = status["applied_count"]
        
        # Rollback latest migration
        latest_version = status["current_version"]
        if latest_version:
            result = self.migration_manager.rollback_migration(latest_version)
            assert result is True
            
            # Check status after rollback
            new_status = self.migration_manager.get_migration_status()
            assert new_status["applied_count"] == applied_count - 1


class TestBackupManager:
    """Test database backup and restore functionality."""
    
    def setup_method(self):
        """Set up test database."""
        cleanup_database()
        self.db_manager = init_database("testing", drop_existing=True)
        
        # Create test data
        self.test_user = DatabaseUtils.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            location="Cape Town"
        )
        
        DatabaseUtils.add_job_application(
            user_id=self.test_user.id,
            job_title="Software Developer",
            company="TechCorp",
            location="Cape Town",
            status=ApplicationStatus.APPLIED
        )
        
        # Use temporary directory for backups
        self.temp_dir = tempfile.mkdtemp()
        self.backup_manager = BackupManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up after tests."""
        cleanup_database()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_backup(self):
        """Test creating database backup."""
        backup_path = self.backup_manager.create_backup("test_backup")
        
        assert backup_path is not None
        assert Path(backup_path).exists()
        assert Path(backup_path).suffix == ".json"
        
        # Verify backup content
        import json
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert "metadata" in backup_data
        assert "data" in backup_data
        assert "users" in backup_data["data"]
        assert "job_applications" in backup_data["data"]
        
        # Check user data
        users = backup_data["data"]["users"]
        assert len(users) == 1
        assert users[0]["email"] == "test@example.com"
        assert users[0]["first_name"] == "Test"
        
        # Check application data
        applications = backup_data["data"]["job_applications"]
        assert len(applications) == 1
        assert applications[0]["job_title"] == "Software Developer"
        assert applications[0]["company"] == "TechCorp"
    
    def test_list_backups(self):
        """Test listing available backups."""
        # Create a few backups
        self.backup_manager.create_backup("backup1")
        self.backup_manager.create_backup("backup2")
        
        backups = self.backup_manager.list_backups()
        
        assert len(backups) >= 2
        assert all("filename" in backup for backup in backups)
        assert all("path" in backup for backup in backups)
        assert all("size" in backup for backup in backups)
        assert all("created" in backup for backup in backups)
    
    def test_restore_backup(self):
        """Test restoring from backup."""
        # Create backup
        backup_path = self.backup_manager.create_backup("restore_test")
        
        # Modify database (add another user)
        DatabaseUtils.create_user(email="another@example.com", first_name="Another")
        
        # Verify we have 2 users
        with self.db_manager.session_scope() as session:
            user_count = session.query(User).count()
            assert user_count == 2
        
        # Restore from backup
        result = self.backup_manager.restore_backup(backup_path, confirm=True)
        assert result is True
        
        # Verify restore worked (should have original 1 user)
        with self.db_manager.session_scope() as session:
            user_count = session.query(User).count()
            assert user_count == 1
            
            restored_user = session.query(User).first()
            assert restored_user.email == "test@example.com"
            assert restored_user.first_name == "Test"
    
    def test_restore_without_confirmation(self):
        """Test restore fails without confirmation."""
        backup_path = self.backup_manager.create_backup("no_confirm_test")
        
        with pytest.raises(DatabaseError, match="requires explicit confirmation"):
            self.backup_manager.restore_backup(backup_path, confirm=False)


class TestDatabaseIntegration:
    """Integration tests for complete database workflows."""
    
    def setup_method(self):
        """Set up test database."""
        cleanup_database()
        self.db_manager = init_database("testing", drop_existing=True)
        
        # Apply migrations
        migration_manager = MigrationManager()
        migration_manager.migrate_to_latest()
    
    def teardown_method(self):
        """Clean up after tests."""
        cleanup_database()
    
    def test_complete_user_workflow(self):
        """Test complete user workflow from creation to job tracking."""
        # 1. Create user
        user = DatabaseUtils.create_user(
            email="workflow@example.com",
            first_name="Workflow",
            last_name="User",
            location="Cape Town",
            job_title="IT Support",
            experience_years=2,
            skills=["Windows", "Office 365", "Help Desk"]
        )
        
        # 2. Update preferences
        DatabaseUtils.update_user_preferences(
            user.id,
            preferred_job_titles=["IT Support", "Help Desk"],
            preferred_locations=["Cape Town", "Remote"],
            salary_min=30000,
            salary_max=50000,
            remote_work_preference=True
        )
        
        # 3. Add resume
        resume = DatabaseUtils.add_resume(
            user_id=user.id,
            filename="workflow_resume.pdf",
            file_path="/tmp/workflow_resume.pdf",
            file_size=1024,
            file_type="pdf",
            parsed_text="IT Support experience with Windows and Office 365",
            skills_extracted=["Windows", "Office 365", "Help Desk"]
        )
        
        # 4. Add job applications
        app1 = DatabaseUtils.add_job_application(
            user_id=user.id,
            resume_id=resume.id,
            job_title="IT Support Specialist",
            company="TechCorp",
            location="Cape Town",
            status=ApplicationStatus.APPLIED,
            salary_min=35000,
            salary_max=45000,
            match_score=90.0
        )
        
        app2 = DatabaseUtils.add_job_application(
            user_id=user.id,
            resume_id=resume.id,
            job_title="Help Desk Analyst",
            company="BusinessCorp",
            location="Remote",
            status=ApplicationStatus.INTERVIEW_SCHEDULED,
            salary_min=30000,
            salary_max=40000,
            match_score=85.0
        )
        
        # 5. Update application status
        DatabaseUtils.update_application_status(
            app2.id,
            ApplicationStatus.INTERVIEWED,
            notes="Great interview, waiting for feedback"
        )
        
        # 6. Add search history
        DatabaseUtils.add_search_history(
            user_id=user.id,
            job_title="IT Support",
            location="Cape Town",
            keywords="Windows Office 365",
            sources_searched=["linkedin", "indeed"],
            total_results=25,
            filtered_results=15,
            applications_made=2
        )
        
        # 7. Verify complete workflow
        # Check user and preferences
        retrieved_user = DatabaseUtils.get_user_by_email("workflow@example.com")
        assert retrieved_user.full_name == "Workflow User"
        
        preferences = DatabaseUtils.get_user_preferences(user.id)
        assert preferences.preferred_job_titles == ["IT Support", "Help Desk"]
        assert preferences.remote_work_preference is True
        
        # Check resume
        resumes = DatabaseUtils.get_user_resumes(user.id)
        assert len(resumes) == 1
        assert resumes[0].skills_extracted == ["Windows", "Office 365", "Help Desk"]
        
        # Check applications
        applications = DatabaseUtils.get_user_applications(user.id)
        assert len(applications) == 2
        
        # Check statistics
        stats = DatabaseUtils.get_application_statistics(user.id)
        assert stats["total_applications"] == 2
        assert stats["interview_count"] == 1
        assert stats["interview_rate"] == 50.0  # 1/2 * 100
        assert stats["average_match_score"] == 87.5  # (90 + 85) / 2
    
    def test_database_backup_restore_integration(self):
        """Test complete backup and restore workflow."""
        # Create test data
        user = DatabaseUtils.create_user(
            email="backup@example.com",
            first_name="Backup",
            last_name="User"
        )
        
        DatabaseUtils.add_job_application(
            user_id=user.id,
            job_title="Test Job",
            company="Test Company",
            status=ApplicationStatus.APPLIED
        )
        
        # Create backup
        backup_manager = BackupManager()
        backup_path = backup_manager.create_backup("integration_test")
        
        # Verify backup exists
        assert Path(backup_path).exists()
        
        # Add more data after backup
        DatabaseUtils.create_user(
            email="after_backup@example.com",
            first_name="After",
            last_name="Backup"
        )
        
        # Verify we have 2 users
        with self.db_manager.session_scope() as session:
            user_count = session.query(User).count()
            assert user_count == 2
        
        # Restore from backup
        backup_manager.restore_backup(backup_path, confirm=True)
        
        # Verify restore (should have original 1 user)
        with self.db_manager.session_scope() as session:
            user_count = session.query(User).count()
            assert user_count == 1
            
            restored_user = session.query(User).first()
            assert restored_user.email == "backup@example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 