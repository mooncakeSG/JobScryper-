"""
Auto Applyer - Database Utilities

Provides high-level database operations, CRUD utilities, data management,
and backup/restore functionality.
"""

import os
import json
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from sqlalchemy.exc import IntegrityError, NoResultFound

from .models import (
    User, UserPreferences, Resume, JobApplication, SearchHistory,
    AIAnalysisCache, SystemSettings, SavedJob, ApplicationStatus, ResumeStatus
)
from .connection import get_database_manager, db_session_scope
from utils.errors import DatabaseError, ValidationError
from utils.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseUtils:
    """High-level database utilities and operations."""
    
    @staticmethod
    def create_user(email: str, **kwargs) -> User:
        """
        Create a new user with default preferences.
        
        Args:
            email: User email address
            **kwargs: Additional user fields
            
        Returns:
            Created User object
            
        Raises:
            DatabaseError: If user creation fails
        """
        try:
            with db_session_scope() as session:
                # Check if user already exists
                existing_user = session.query(User).filter_by(email=email).first()
                if existing_user:
                    raise ValidationError(f"User with email {email} already exists")
                
                # Create user
                user = User(email=email, **kwargs)
                session.add(user)
                session.flush()  # Get the user ID
                
                # Create default preferences
                preferences = UserPreferences(
                    user_id=user.id,
                    max_results_per_search=50,
                    auto_apply_enabled=False,
                    email_notifications=True,
                    ai_suggestions_enabled=True,
                    ats_analysis_enabled=True
                )
                session.add(preferences)
                
                session.commit()
                logger.info(f"Created user: {email} (ID: {user.id})")
                return user
                
        except IntegrityError as e:
            raise DatabaseError(f"User creation failed: {e}")
        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}")
            raise DatabaseError(f"User creation failed: {e}")
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User object or None if not found
        """
        try:
            with db_session_scope() as session:
                return session.query(User).filter_by(email=email, is_active=True).first()
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        try:
            with db_session_scope() as session:
                return session.query(User).filter_by(id=user_id, is_active=True).first()
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated User object or None if not found
        """
        try:
            with db_session_scope() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if not user:
                    return None
                
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                
                user.updated_at = datetime.now(timezone.utc)
                session.commit()
                
                logger.info(f"Updated user {user_id}")
                return user
                
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise DatabaseError(f"User update failed: {e}")
    
    @staticmethod
    def add_resume(user_id: int, filename: str, file_path: str, file_size: int, 
                   file_type: str, **kwargs) -> Resume:
        """
        Add a resume for a user.
        
        Args:
            user_id: User ID
            filename: Original filename
            file_path: Path to stored file
            file_size: File size in bytes
            file_type: File type (pdf, docx, txt)
            **kwargs: Additional resume fields
            
        Returns:
            Created Resume object
        """
        try:
            with db_session_scope() as session:
                # Deactivate previous resumes if this is set as active
                if kwargs.get('is_active', True):
                    session.query(Resume).filter_by(user_id=user_id, is_active=True).update(
                        {Resume.is_active: False}
                    )
                
                resume = Resume(
                    user_id=user_id,
                    filename=filename,
                    file_path=file_path,
                    file_size=file_size,
                    file_type=file_type,
                    **kwargs
                )
                session.add(resume)
                session.commit()
                
                logger.info(f"Added resume for user {user_id}: {filename}")
                return resume
                
        except Exception as e:
            logger.error(f"Failed to add resume for user {user_id}: {e}")
            raise DatabaseError(f"Resume creation failed: {e}")
    
    @staticmethod
    def get_user_resumes(user_id: int, active_only: bool = True) -> List[Resume]:
        """
        Get resumes for a user.
        
        Args:
            user_id: User ID
            active_only: Whether to return only active resumes
            
        Returns:
            List of Resume objects
        """
        try:
            with db_session_scope() as session:
                query = session.query(Resume).filter_by(user_id=user_id)
                
                if active_only:
                    query = query.filter_by(is_active=True)
                
                return query.order_by(desc(Resume.upload_date)).all()
                
        except Exception as e:
            logger.error(f"Failed to get resumes for user {user_id}: {e}")
            return []
    
    @staticmethod
    def add_job_application(user_id: int, job_title: str, company: str, 
                           **kwargs) -> JobApplication:
        """
        Add a job application.
        
        Args:
            user_id: User ID
            job_title: Job title
            company: Company name
            **kwargs: Additional application fields
            
        Returns:
            Created JobApplication object
        """
        try:
            with db_session_scope() as session:
                application = JobApplication(
                    user_id=user_id,
                    job_title=job_title,
                    company=company,
                    **kwargs
                )
                session.add(application)
                session.commit()
                
                logger.info(f"Added job application for user {user_id}: {job_title} at {company}")
                return application
                
        except Exception as e:
            logger.error(f"Failed to add job application for user {user_id}: {e}")
            raise DatabaseError(f"Job application creation failed: {e}")
    
    @staticmethod
    def get_user_applications(user_id: int, status: ApplicationStatus = None, 
                             limit: int = None) -> List[JobApplication]:
        """
        Get job applications for a user.
        
        Args:
            user_id: User ID
            status: Filter by application status
            limit: Maximum number of results
            
        Returns:
            List of JobApplication objects
        """
        try:
            with db_session_scope() as session:
                query = session.query(JobApplication).filter_by(user_id=user_id)
                
                if status:
                    query = query.filter_by(status=status)
                
                query = query.order_by(desc(JobApplication.application_date))
                
                if limit:
                    query = query.limit(limit)
                
                return query.all()
                
        except Exception as e:
            logger.error(f"Failed to get applications for user {user_id}: {e}")
            return []
    
    @staticmethod
    def update_application_status(application_id: int, status: ApplicationStatus, 
                                 notes: str = None, **kwargs) -> Optional[JobApplication]:
        """
        Update job application status.
        
        Args:
            application_id: Application ID
            status: New status
            notes: Optional notes
            **kwargs: Additional fields to update
            
        Returns:
            Updated JobApplication object or None if not found
        """
        try:
            with db_session_scope() as session:
                application = session.query(JobApplication).filter_by(id=application_id).first()
                if not application:
                    return None
                
                application.status = status
                application.updated_at = datetime.now(timezone.utc)
                
                if notes:
                    if status in [ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.INTERVIEWED]:
                        application.interview_notes = notes
                    else:
                        application.follow_up_notes = notes
                
                # Update additional fields
                for key, value in kwargs.items():
                    if hasattr(application, key):
                        setattr(application, key, value)
                
                session.commit()
                
                logger.info(f"Updated application {application_id} status to {status.value}")
                return application
                
        except Exception as e:
            logger.error(f"Failed to update application {application_id}: {e}")
            raise DatabaseError(f"Application update failed: {e}")
    
    @staticmethod
    def add_search_history(user_id: int, job_title: str, **kwargs) -> SearchHistory:
        """
        Add search history entry.
        
        Args:
            user_id: User ID
            job_title: Job title searched
            **kwargs: Additional search fields
            
        Returns:
            Created SearchHistory object
        """
        try:
            with db_session_scope() as session:
                search = SearchHistory(
                    user_id=user_id,
                    job_title=job_title,
                    **kwargs
                )
                session.add(search)
                session.commit()
                
                return search
                
        except Exception as e:
            logger.error(f"Failed to add search history for user {user_id}: {e}")
            raise DatabaseError(f"Search history creation failed: {e}")
    
    @staticmethod
    def get_user_preferences(user_id: int) -> Optional[UserPreferences]:
        """
        Get user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            UserPreferences object or None if not found
        """
        try:
            with db_session_scope() as session:
                return session.query(UserPreferences).filter_by(user_id=user_id).first()
                
        except Exception as e:
            logger.error(f"Failed to get preferences for user {user_id}: {e}")
            return None
    
    @staticmethod
    def update_user_preferences(user_id: int, **kwargs) -> Optional[UserPreferences]:
        """
        Update user preferences.
        
        Args:
            user_id: User ID
            **kwargs: Preference fields to update
            
        Returns:
            Updated UserPreferences object or None if not found
        """
        try:
            with db_session_scope() as session:
                preferences = session.query(UserPreferences).filter_by(user_id=user_id).first()
                if not preferences:
                    return None
                
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(preferences, key):
                        setattr(preferences, key, value)
                
                preferences.updated_at = datetime.now(timezone.utc)
                session.commit()
                
                return preferences
                
        except Exception as e:
            logger.error(f"Failed to update preferences for user {user_id}: {e}")
            raise DatabaseError(f"Preferences update failed: {e}")
    
    @staticmethod
    def get_application_statistics(user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get application statistics for a user.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Dictionary with statistics
        """
        try:
            with db_session_scope() as session:
                since_date = datetime.now(timezone.utc) - timedelta(days=days)
                
                # Total applications
                total_apps = session.query(JobApplication).filter_by(user_id=user_id).count()
                
                # Applications in time period
                recent_apps = session.query(JobApplication).filter(
                    and_(
                        JobApplication.user_id == user_id,
                        JobApplication.application_date >= since_date
                    )
                ).count()
                
                # Status breakdown
                status_counts = {}
                for status in ApplicationStatus:
                    count = session.query(JobApplication).filter(
                        and_(
                            JobApplication.user_id == user_id,
                            JobApplication.status == status,
                            JobApplication.application_date >= since_date
                        )
                    ).count()
                    status_counts[status.value] = count
                
                # Interview rate
                interviews = session.query(JobApplication).filter(
                    and_(
                        JobApplication.user_id == user_id,
                        JobApplication.status.in_([
                            ApplicationStatus.INTERVIEW_SCHEDULED,
                            ApplicationStatus.INTERVIEWED
                        ]),
                        JobApplication.application_date >= since_date
                    )
                ).count()
                
                interview_rate = (interviews / recent_apps * 100) if recent_apps > 0 else 0
                
                # Average match score
                avg_match = session.query(func.avg(JobApplication.match_score)).filter(
                    and_(
                        JobApplication.user_id == user_id,
                        JobApplication.match_score.isnot(None),
                        JobApplication.application_date >= since_date
                    )
                ).scalar() or 0
                
                return {
                    'total_applications': total_apps,
                    'recent_applications': recent_apps,
                    'status_breakdown': status_counts,
                    'interview_count': interviews,
                    'interview_rate': round(interview_rate, 1),
                    'average_match_score': round(float(avg_match), 1) if avg_match else 0,
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics for user {user_id}: {e}")
            return {}
    
    @staticmethod
    def cache_ai_analysis(cache_key: str, analysis_type: str, results: Dict[str, Any],
                         expiry_hours: int = 24) -> AIAnalysisCache:
        """
        Cache AI analysis results.
        
        Args:
            cache_key: Unique cache key
            analysis_type: Type of analysis
            results: Analysis results
            expiry_hours: Hours until expiry
            
        Returns:
            Created AIAnalysisCache object
        """
        try:
            with db_session_scope() as session:
                # Remove existing cache entry if it exists
                session.query(AIAnalysisCache).filter_by(cache_key=cache_key).delete()
                
                expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
                
                cache_entry = AIAnalysisCache(
                    cache_key=cache_key,
                    analysis_type=analysis_type,
                    results=results,
                    expires_at=expires_at
                )
                session.add(cache_entry)
                session.commit()
                
                return cache_entry
                
        except Exception as e:
            logger.error(f"Failed to cache AI analysis: {e}")
            raise DatabaseError(f"AI cache creation failed: {e}")
    
    @staticmethod
    def get_cached_analysis(cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached AI analysis results.
        
        Args:
            cache_key: Cache key to look up
            
        Returns:
            Cached results or None if not found/expired
        """
        try:
            with db_session_scope() as session:
                cache_entry = session.query(AIAnalysisCache).filter_by(cache_key=cache_key).first()
                
                if not cache_entry:
                    return None
                
                if cache_entry.is_expired():
                    # Delete expired entry
                    session.delete(cache_entry)
                    session.commit()
                    return None
                
                return cache_entry.results
                
        except Exception as e:
            logger.error(f"Failed to get cached analysis: {e}")
            return None


class BackupManager:
    """Handles database backup and restore operations."""
    
    def __init__(self, backup_dir: str = "backups"):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, backup_name: str = None) -> str:
        """
        Create a database backup.
        
        Args:
            backup_name: Name for the backup file
            
        Returns:
            Path to the backup file
        """
        try:
            db_manager = get_database_manager()
            
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"auto_applyer_backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.json"
            
            logger.info(f"Creating database backup: {backup_path}")
            
            # Export all data
            backup_data = {
                'metadata': {
                    'backup_date': datetime.now(timezone.utc).isoformat(),
                    'version': '1.0',
                    'environment': db_manager.config.environment
                },
                'data': {}
            }
            
            with db_session_scope() as session:
                # Backup users
                users = session.query(User).all()
                backup_data['data']['users'] = [user.to_dict() for user in users]
                
                # Backup user preferences
                preferences = session.query(UserPreferences).all()
                backup_data['data']['user_preferences'] = [
                    {
                        'id': pref.id,
                        'user_id': pref.user_id,
                        'preferred_job_titles': pref.preferred_job_titles,
                        'preferred_locations': pref.preferred_locations,
                        'preferred_job_types': pref.preferred_job_types,
                        'salary_min': pref.salary_min,
                        'salary_max': pref.salary_max,
                        'remote_work_preference': pref.remote_work_preference,
                        'max_results_per_search': pref.max_results_per_search,
                        'auto_apply_enabled': pref.auto_apply_enabled,
                        'job_sources': pref.job_sources,
                        'email_notifications': pref.email_notifications,
                        'application_reminders': pref.application_reminders,
                        'daily_job_alerts': pref.daily_job_alerts,
                        'ai_suggestions_enabled': pref.ai_suggestions_enabled,
                        'ats_analysis_enabled': pref.ats_analysis_enabled,
                        'auto_resume_optimization': pref.auto_resume_optimization,
                        'created_at': pref.created_at.isoformat() if pref.created_at else None,
                        'updated_at': pref.updated_at.isoformat() if pref.updated_at else None
                    }
                    for pref in preferences
                ]
                
                # Backup resumes (metadata only, not file content)
                resumes = session.query(Resume).all()
                backup_data['data']['resumes'] = [resume.to_dict() for resume in resumes]
                
                # Backup job applications
                applications = session.query(JobApplication).all()
                backup_data['data']['job_applications'] = [app.to_dict() for app in applications]
                
                # Backup search history
                searches = session.query(SearchHistory).all()
                backup_data['data']['search_history'] = [search.to_dict() for search in searches]
            
            # Write backup file
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Database backup created successfully: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            raise DatabaseError(f"Backup creation failed: {e}")
    
    def restore_backup(self, backup_path: str, confirm: bool = False) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            confirm: Confirmation flag (required for safety)
            
        Returns:
            True if successful
        """
        if not confirm:
            raise DatabaseError("Restore operation requires explicit confirmation")
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise DatabaseError(f"Backup file not found: {backup_path}")
        
        try:
            logger.warning(f"Starting database restore from: {backup_path}")
            
            # Load backup data
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validate backup format
            if 'metadata' not in backup_data or 'data' not in backup_data:
                raise DatabaseError("Invalid backup file format")
            
            db_manager = get_database_manager()
            
            # Clear existing data (this is destructive!)
            logger.warning("Clearing existing database data")
            with db_session_scope() as session:
                session.query(SearchHistory).delete()
                session.query(JobApplication).delete()
                session.query(Resume).delete()
                session.query(UserPreferences).delete()
                session.query(User).delete()
                session.commit()
            
            # Restore data
            data = backup_data['data']
            
            with db_session_scope() as session:
                # Restore users first
                for user_data in data.get('users', []):
                    user = User(**{k: v for k, v in user_data.items() 
                                 if k not in ['created_at', 'updated_at', 'last_login']})
                    session.add(user)
                
                session.flush()  # Get user IDs
                
                # Restore user preferences
                for pref_data in data.get('user_preferences', []):
                    pref = UserPreferences(**{k: v for k, v in pref_data.items() 
                                            if k not in ['id', 'created_at', 'updated_at']})
                    session.add(pref)
                
                # Restore resumes (metadata only)
                for resume_data in data.get('resumes', []):
                    resume = Resume(**{k: v for k, v in resume_data.items() 
                                     if k not in ['id', 'created_at', 'updated_at', 'upload_date', 'last_analyzed']})
                    session.add(resume)
                
                session.flush()  # Get resume IDs
                
                # Restore job applications
                for app_data in data.get('job_applications', []):
                    # Convert status string back to enum
                    if 'status' in app_data:
                        app_data['status'] = ApplicationStatus(app_data['status'])
                    
                    app = JobApplication(**{k: v for k, v in app_data.items() 
                                          if k not in ['id', 'created_at', 'updated_at', 'application_date', 
                                                     'interview_date', 'follow_up_date']})
                    session.add(app)
                
                # Restore search history
                for search_data in data.get('search_history', []):
                    search = SearchHistory(**{k: v for k, v in search_data.items() 
                                            if k not in ['id', 'search_date']})
                    session.add(search)
                
                session.commit()
            
            logger.info("Database restore completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            raise DatabaseError(f"Restore operation failed: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Returns:
            List of backup information
        """
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.json"):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    metadata = backup_data.get('metadata', {})
                    
                    backups.append({
                        'filename': backup_file.name,
                        'path': str(backup_file),
                        'size': backup_file.stat().st_size,
                        'created': metadata.get('backup_date'),
                        'environment': metadata.get('environment'),
                        'version': metadata.get('version')
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not read backup file {backup_file}: {e}")
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created'] or '', reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return [] 