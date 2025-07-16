"""
Auto Applyer - Database Models

SQLAlchemy models for all application data including users, job applications,
resumes, search history, and preferences.
"""

from sqlalchemy import (
    Column, String, Integer, DateTime, Text, Boolean, Float, 
    ForeignKey, Enum, JSON, LargeBinary, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from datetime import datetime, timezone
import enum
import uuid
from typing import Dict, Any, Optional, List

# Create the base class for all models
Base = declarative_base()


class ApplicationStatus(enum.Enum):
    """Enumeration for job application statuses."""
    PENDING = "pending"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    TECHNICAL_TEST = "technical_test"
    OFFER_RECEIVED = "offer_received"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_REJECTED = "offer_rejected"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ResumeStatus(enum.Enum):
    """Enumeration for resume processing statuses."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PARSED = "parsed"
    ANALYZED = "analyzed"
    ERROR = "error"


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = 'users'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)  # For future authentication
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Professional information
    job_title = Column(String(200), nullable=True)
    experience_years = Column(Integer, nullable=True)
    skills = Column(JSON, nullable=True)  # Store as JSON array
    
    # Account settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    linkedin_username = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email.split('@')[0]  # Use email prefix as fallback
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for API responses."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'location': self.location,
            'job_title': self.job_title,
            'experience_years': self.experience_years,
            'skills': self.skills,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'linkedin_username': self.linkedin_username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class UserPreferences(Base):
    """User preferences and settings."""
    
    __tablename__ = 'user_preferences'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Job search preferences
    preferred_job_titles = Column(JSON, nullable=True)  # Array of job titles
    preferred_locations = Column(JSON, nullable=True)   # Array of locations
    preferred_job_types = Column(JSON, nullable=True)   # Array of job types
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(20), nullable=True, default='USD')  # Currency code (USD, EUR, GBP, etc.)
    remote_work_preference = Column(Boolean, default=False)
    
    # Search settings
    max_results_per_search = Column(Integer, default=50)
    auto_apply_enabled = Column(Boolean, default=False)
    job_sources = Column(JSON, nullable=True)  # Array of enabled job sources
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    application_reminders = Column(Boolean, default=True)
    daily_job_alerts = Column(Boolean, default=False)
    
    # AI and analysis preferences
    ai_suggestions_enabled = Column(Boolean, default=True)
    ats_analysis_enabled = Column(Boolean, default=True)
    auto_resume_optimization = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, auto_apply={self.auto_apply_enabled})>"


class Resume(Base):
    """Resume storage and tracking."""
    
    __tablename__ = 'resumes'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    
    # Processing information
    status = Column(Enum(ResumeStatus), default=ResumeStatus.UPLOADED, nullable=False)
    parsed_text = Column(Text, nullable=True)
    parsed_sections = Column(JSON, nullable=True)  # Structured resume data
    
    # Analysis results
    skills_extracted = Column(JSON, nullable=True)
    experience_level = Column(String(50), nullable=True)
    education_info = Column(JSON, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_analyzed = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    job_applications = relationship("JobApplication", back_populates="resume")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, filename='{self.filename}', status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resume to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'status': self.status.value if self.status else None,
            'skills_extracted': self.skills_extracted,
            'experience_level': self.experience_level,
            'is_active': self.is_active,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'last_analyzed': self.last_analyzed.isoformat() if self.last_analyzed else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class JobApplication(Base):
    """Job application tracking and management."""
    
    __tablename__ = 'job_applications'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    resume_id = Column(Integer, ForeignKey('resumes.id'), nullable=True)
    
    # Job information
    job_title = Column(String(300), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    job_description = Column(Text, nullable=True)
    job_url = Column(String(1000), nullable=True)
    
    # Application details
    application_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    source = Column(String(100), nullable=True)  # linkedin, indeed, etc.
    
    # Job details
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    job_type = Column(String(50), nullable=True)  # Full-time, Part-time, etc.
    is_remote = Column(Boolean, default=False)
    easy_apply = Column(Boolean, default=False)
    
    # Application tracking
    applied_via = Column(String(100), nullable=True)  # Auto-applied, Manual, etc.
    cover_letter_used = Column(Boolean, default=False)
    
    # Interview and follow-up
    interview_date = Column(DateTime(timezone=True), nullable=True)
    interview_type = Column(String(50), nullable=True)  # Phone, Video, In-person
    interview_notes = Column(Text, nullable=True)
    
    # Follow-up tracking
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    
    # Analysis results
    match_score = Column(Float, nullable=True)  # 0-100 match percentage
    ats_score = Column(Float, nullable=True)    # ATS compatibility score
    ai_analysis = Column(JSON, nullable=True)   # AI-generated insights
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="job_applications")
    resume = relationship("Resume", back_populates="job_applications")
    
    # Database constraints
    __table_args__ = (
        Index('ix_job_applications_user_date', 'user_id', 'application_date'),
        Index('ix_job_applications_company_title', 'company', 'job_title'),
        Index('ix_job_applications_status', 'status'),
    )
    
    def __repr__(self):
        return f"<JobApplication(id={self.id}, user_id={self.user_id}, title='{self.job_title}', company='{self.company}', status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job application to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'job_title': self.job_title,
            'company': self.company,
            'location': self.location,
            'job_description': self.job_description,
            'job_url': self.job_url,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'status': self.status.value if self.status else None,
            'source': self.source,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'job_type': self.job_type,
            'is_remote': self.is_remote,
            'easy_apply': self.easy_apply,
            'applied_via': self.applied_via,
            'cover_letter_used': self.cover_letter_used,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_type': self.interview_type,
            'interview_notes': self.interview_notes,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'follow_up_notes': self.follow_up_notes,
            'match_score': self.match_score,
            'ats_score': self.ats_score,
            'ai_analysis': self.ai_analysis,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def salary_range(self) -> str:
        """Get formatted salary range."""
        if self.salary_min and self.salary_max:
            return f"R{self.salary_min:,} - R{self.salary_max:,}"
        elif self.salary_min:
            return f"R{self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to R{self.salary_max:,}"
        else:
            return "Not specified"


class SearchHistory(Base):
    """Search history tracking for analytics and preferences."""
    
    __tablename__ = 'search_history'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Search parameters
    job_title = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    job_type = Column(String(50), nullable=True)
    keywords = Column(String(500), nullable=True)
    
    # Search settings
    sources_searched = Column(JSON, nullable=True)  # Array of sources
    max_results = Column(Integer, default=50)
    
    # Search results
    total_results = Column(Integer, default=0)
    filtered_results = Column(Integer, default=0)
    applications_made = Column(Integer, default=0)
    
    # Performance metrics
    search_duration = Column(Float, nullable=True)  # Duration in seconds
    
    # Timestamps
    search_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="search_history")
    
    # Database constraints
    __table_args__ = (
        Index('ix_search_history_user_date', 'user_id', 'search_date'),
        Index('ix_search_history_job_title', 'job_title'),
    )
    
    def __repr__(self):
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, job_title='{self.job_title}', results={self.total_results})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert search history to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_title': self.job_title,
            'location': self.location,
            'job_type': self.job_type,
            'keywords': self.keywords,
            'sources_searched': self.sources_searched,
            'max_results': self.max_results,
            'total_results': self.total_results,
            'filtered_results': self.filtered_results,
            'applications_made': self.applications_made,
            'search_duration': self.search_duration,
            'search_date': self.search_date.isoformat() if self.search_date else None
        }


class AIAnalysisCache(Base):
    """Cache for AI analysis results to avoid reprocessing."""
    
    __tablename__ = 'ai_analysis_cache'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Cache key (hash of inputs)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    
    # Analysis type
    analysis_type = Column(String(100), nullable=False)  # resume_suggestions, ats_analysis, etc.
    
    # Input data (for validation)
    input_hash = Column(String(255), nullable=False)
    
    # Results
    results = Column(JSON, nullable=False)
    
    # Metadata
    tokens_used = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Database constraints
    __table_args__ = (
        Index('ix_ai_cache_type_key', 'analysis_type', 'cache_key'),
        Index('ix_ai_cache_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<AIAnalysisCache(id={self.id}, type='{self.analysis_type}', key='{self.cache_key[:20]}...')>"
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc)


class SystemSettings(Base):
    """System-wide settings and configuration."""
    
    __tablename__ = 'system_settings'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Setting identification
    setting_key = Column(String(255), unique=True, nullable=False, index=True)
    setting_value = Column(JSON, nullable=False)
    setting_type = Column(String(50), nullable=False)  # string, integer, boolean, json
    
    # Metadata
    description = Column(Text, nullable=True)
    is_user_configurable = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self):
        return f"<SystemSettings(key='{self.setting_key}', type='{self.setting_type}')>"


class SavedJob(Base):
    """Saved jobs for users to review later."""
    
    __tablename__ = 'saved_jobs'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Job identification
    job_id = Column(String(255), nullable=True)  # External job ID from source
    job_url = Column(String(1000), nullable=True)  # Job posting URL
    
    # Job data (stored as JSON for flexibility)
    job_data = Column(JSON, nullable=False)  # Complete job data from source
    
    # Metadata
    source = Column(String(100), nullable=True)  # indeed, linkedin, etc.
    saved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Database constraints
    __table_args__ = (
        Index('idx_saved_jobs_user_id', 'user_id'),
        Index('idx_saved_jobs_job_id', 'job_id'),
        Index('idx_saved_jobs_saved_at', 'saved_at'),
        UniqueConstraint('user_id', 'job_id', name='uq_user_job_id'),
        UniqueConstraint('user_id', 'job_url', name='uq_user_job_url'),
    )
    
    def __repr__(self):
        return f"<SavedJob(id={self.id}, user_id={self.user_id}, job_id='{self.job_id}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert saved job to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'job_url': self.job_url,
            'job_data': self.job_data,
            'source': self.source,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ActivityType(enum.Enum):
    """Enumeration for activity types."""
    APPLICATION_CREATED = "application_created"
    APPLICATION_UPDATED = "application_updated"
    APPLICATION_DELETED = "application_deleted"
    JOB_SAVED = "job_saved"
    JOB_APPLIED = "job_applied"
    RESUME_UPLOADED = "resume_uploaded"
    STATUS_CHANGED = "status_changed"
    SEARCH_PERFORMED = "search_performed"
    PROFILE_UPDATED = "profile_updated"


class Activity(Base):
    """User activity tracking for recent activity feed."""
    
    __tablename__ = 'activities'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Activity information
    activity_type = Column(Enum(ActivityType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Related entity information
    entity_type = Column(String(50), nullable=True)  # application, job, resume, etc.
    entity_id = Column(Integer, nullable=True)  # ID of related entity
    
    # Additional data
    activity_metadata = Column(JSON, nullable=True)  # Additional context data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    # Database constraints
    __table_args__ = (
        Index('ix_activities_user_created', 'user_id', 'created_at'),
        Index('ix_activities_type', 'activity_type'),
        Index('ix_activities_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f"<Activity(id={self.id}, user_id={self.user_id}, type='{self.activity_type.value}', title='{self.title}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type.value,
            'title': self.title,
            'description': self.description,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'metadata': self.activity_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Model registry for migrations and utilities
ALL_MODELS = [
    User,
    UserPreferences,
    Resume,
    JobApplication,
    SearchHistory,
    AIAnalysisCache,
    SystemSettings,
    SavedJob,
    Activity
] 