"""
Auto Applyer - Database Migration System

Handles database schema migrations, version management, and upgrades.
"""

import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import Session

from .connection import get_database_manager, db_session_scope
from .models import Base
from utils.errors import DatabaseError, MigrationError
from utils.logging_config import get_logger

logger = get_logger(__name__)


class Migration:
    """Individual migration definition."""
    
    def __init__(self, version: str, description: str, 
                 upgrade_func: Callable[[Session], None] = None,
                 downgrade_func: Callable[[Session], None] = None):
        """
        Initialize migration.
        
        Args:
            version: Migration version (e.g., "001", "002")
            description: Human-readable description
            upgrade_func: Function to apply migration
            downgrade_func: Function to rollback migration
        """
        self.version = version
        self.description = description
        self.upgrade_func = upgrade_func
        self.downgrade_func = downgrade_func
        self.applied_at: Optional[datetime] = None
    
    def apply(self, session: Session) -> None:
        """Apply the migration."""
        if self.upgrade_func:
            logger.info(f"Applying migration {self.version}: {self.description}")
            self.upgrade_func(session)
            self.applied_at = datetime.now(timezone.utc)
        else:
            logger.warning(f"No upgrade function defined for migration {self.version}")
    
    def rollback(self, session: Session) -> None:
        """Rollback the migration."""
        if self.downgrade_func:
            logger.info(f"Rolling back migration {self.version}: {self.description}")
            self.downgrade_func(session)
        else:
            logger.warning(f"No downgrade function defined for migration {self.version}")


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self):
        """Initialize migration manager."""
        self.migrations: List[Migration] = []
        self.migration_table_name = 'schema_migrations'
        self._register_migrations()
    
    def _register_migrations(self) -> None:
        """Register all available migrations."""
        
        # Migration 001: Initial schema
        def migration_001_upgrade(session: Session) -> None:
            """Create all initial tables."""
            db_manager = get_database_manager()
            Base.metadata.create_all(db_manager.engine)
        
        def migration_001_downgrade(session: Session) -> None:
            """Drop all tables."""
            db_manager = get_database_manager()
            Base.metadata.drop_all(db_manager.engine)
        
        self.migrations.append(Migration(
            "001",
            "Initial database schema",
            migration_001_upgrade,
            migration_001_downgrade
        ))
        
        # Migration 002: Add indexes for performance
        def migration_002_upgrade(session: Session) -> None:
            """Add performance indexes."""
            db_manager = get_database_manager()
            
            if db_manager.config.config['database_url'].startswith('sqlite'):
                # SQLite indexes
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_job_applications_user_company 
                    ON job_applications(user_id, company)
                """))
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_job_applications_status_date 
                    ON job_applications(status, application_date)
                """))
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_resumes_user_active 
                    ON resumes(user_id, is_active)
                """))
            else:
                # PostgreSQL indexes
                session.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_job_applications_user_company 
                    ON job_applications(user_id, company)
                """))
                session.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_job_applications_status_date 
                    ON job_applications(status, application_date)
                """))
                session.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_resumes_user_active 
                    ON resumes(user_id, is_active)
                """))
        
        def migration_002_downgrade(session: Session) -> None:
            """Remove performance indexes."""
            session.execute(text("DROP INDEX IF EXISTS ix_job_applications_user_company"))
            session.execute(text("DROP INDEX IF EXISTS ix_job_applications_status_date"))
            session.execute(text("DROP INDEX IF EXISTS ix_resumes_user_active"))
        
        self.migrations.append(Migration(
            "002",
            "Add performance indexes",
            migration_002_upgrade,
            migration_002_downgrade
        ))
        
        # Migration 003: Add full-text search support
        def migration_003_upgrade(session: Session) -> None:
            """Add full-text search capabilities."""
            db_manager = get_database_manager()
            
            if db_manager.config.config['database_url'].startswith('sqlite'):
                # SQLite FTS (if supported)
                try:
                    session.execute(text("""
                        CREATE VIRTUAL TABLE IF NOT EXISTS job_applications_fts 
                        USING fts5(job_title, company, job_description, content=job_applications, content_rowid=id)
                    """))
                    
                    # Populate FTS table
                    session.execute(text("""
                        INSERT INTO job_applications_fts(job_applications_fts) VALUES('rebuild')
                    """))
                except Exception as e:
                    logger.warning(f"Could not create FTS table: {e}")
            else:
                # PostgreSQL full-text search
                session.execute(text("""
                    ALTER TABLE job_applications 
                    ADD COLUMN IF NOT EXISTS search_vector tsvector
                """))
                
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_job_applications_search 
                    ON job_applications USING gin(search_vector)
                """))
                
                # Create trigger to update search vector
                session.execute(text("""
                    CREATE OR REPLACE FUNCTION update_job_application_search_vector()
                    RETURNS trigger AS $$
                    BEGIN
                        NEW.search_vector := to_tsvector('english', 
                            COALESCE(NEW.job_title, '') || ' ' ||
                            COALESCE(NEW.company, '') || ' ' ||
                            COALESCE(NEW.job_description, '')
                        );
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """))
                
                session.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS job_applications_search_vector_update
                    BEFORE INSERT OR UPDATE ON job_applications
                    FOR EACH ROW EXECUTE FUNCTION update_job_application_search_vector()
                """))
        
        def migration_003_downgrade(session: Session) -> None:
            """Remove full-text search."""
            db_manager = get_database_manager()
            
            if db_manager.config.config['database_url'].startswith('sqlite'):
                session.execute(text("DROP TABLE IF EXISTS job_applications_fts"))
            else:
                session.execute(text("DROP TRIGGER IF EXISTS job_applications_search_vector_update ON job_applications"))
                session.execute(text("DROP FUNCTION IF EXISTS update_job_application_search_vector()"))
                session.execute(text("DROP INDEX IF EXISTS ix_job_applications_search"))
                session.execute(text("ALTER TABLE job_applications DROP COLUMN IF EXISTS search_vector"))
        
        self.migrations.append(Migration(
            "003",
            "Add full-text search support",
            migration_003_upgrade,
            migration_003_downgrade
        ))
        
        # Migration 004: Add activities table
        def migration_004_upgrade(session: Session) -> None:
            """Create activities table for user activity tracking."""
            db_manager = get_database_manager()
            
            if db_manager.config.config['database_url'].startswith('sqlite'):
                # SQLite activities table
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        activity_type VARCHAR(50) NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        entity_type VARCHAR(50),
                        entity_id INTEGER,
                        activity_metadata TEXT,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """))
                
                # Create indexes
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_activities_user_created 
                    ON activities(user_id, created_at)
                """))
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_activities_type 
                    ON activities(activity_type)
                """))
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_activities_entity 
                    ON activities(entity_type, entity_id)
                """))
            else:
                # PostgreSQL activities table
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS activities (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        activity_type VARCHAR(50) NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        entity_type VARCHAR(50),
                        entity_id INTEGER,
                        activity_metadata JSONB,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """))
                
                # Create indexes
                session.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_activities_user_created 
                    ON activities(user_id, created_at)
                """))
                session.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_activities_type 
                    ON activities(activity_type)
                """))
                session.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_activities_entity 
                    ON activities(entity_type, entity_id)
                """))
        
        def migration_004_downgrade(session: Session) -> None:
            """Remove activities table."""
            session.execute(text("DROP TABLE IF EXISTS activities"))
        
        self.migrations.append(Migration(
            "004",
            "Add activities table for user activity tracking",
            migration_004_upgrade,
            migration_004_downgrade
        ))
        
        # Migration 005: Add salary currency to user preferences
        def migration_005_upgrade(session: Session) -> None:
            """Add salary_currency column to user_preferences table."""
            db_manager = get_database_manager()
            
            if db_manager.config.config['database_url'].startswith('sqlite'):
                # SQLite doesn't support ADD COLUMN with DEFAULT in ALTER TABLE
                # We'll need to recreate the table or use a workaround
                try:
                    # Check if column already exists
                    result = session.execute(text("PRAGMA table_info(user_preferences)"))
                    columns = [row[1] for row in result.fetchall()]
                    
                    if 'salary_currency' not in columns:
                        # Add the column
                        session.execute(text("""
                            ALTER TABLE user_preferences 
                            ADD COLUMN salary_currency VARCHAR(20)
                        """))
                        
                        # Update existing records with default value
                        session.execute(text("""
                            UPDATE user_preferences 
                            SET salary_currency = 'USD' 
                            WHERE salary_currency IS NULL
                        """))
                        
                        logger.info("Added salary_currency column to user_preferences table")
                    else:
                        logger.info("salary_currency column already exists")
                        
                except Exception as e:
                    logger.error(f"Error adding salary_currency column: {e}")
                    raise
            else:
                # PostgreSQL supports ADD COLUMN with DEFAULT
                session.execute(text("""
                    ALTER TABLE user_preferences 
                    ADD COLUMN IF NOT EXISTS salary_currency VARCHAR(20) DEFAULT 'USD'
                """))
        
        def migration_005_downgrade(session: Session) -> None:
            """Remove salary_currency column from user_preferences table."""
            db_manager = get_database_manager()
            
            if db_manager.config.config['database_url'].startswith('sqlite'):
                # SQLite doesn't support DROP COLUMN directly
                # This would require recreating the table
                logger.warning("SQLite DROP COLUMN not supported - manual intervention required")
            else:
                session.execute(text("""
                    ALTER TABLE user_preferences 
                    DROP COLUMN IF EXISTS salary_currency
                """))
        
        self.migrations.append(Migration(
            "005",
            "Add salary currency to user preferences",
            migration_005_upgrade,
            migration_005_downgrade
        ))
        
        # Sort migrations by version
        self.migrations.sort(key=lambda m: m.version)
    
    def _ensure_migration_table(self) -> None:
        """Ensure the migration tracking table exists."""
        try:
            db_manager = get_database_manager()
            
            # Create migration table if it doesn't exist
            with db_session_scope() as session:
                if db_manager.config.config['database_url'].startswith('sqlite'):
                    session.execute(text(f"""
                        CREATE TABLE IF NOT EXISTS {self.migration_table_name} (
                            version VARCHAR(50) PRIMARY KEY,
                            description TEXT,
                            applied_at DATETIME NOT NULL,
                            checksum VARCHAR(255)
                        )
                    """))
                else:
                    session.execute(text(f"""
                        CREATE TABLE IF NOT EXISTS {self.migration_table_name} (
                            version VARCHAR(50) PRIMARY KEY,
                            description TEXT,
                            applied_at TIMESTAMP WITH TIME ZONE NOT NULL,
                            checksum VARCHAR(255)
                        )
                    """))
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to create migration table: {e}")
            raise MigrationError(f"Migration table creation failed: {e}")
    
    def _get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            with db_session_scope() as session:
                result = session.execute(text(f"""
                    SELECT version FROM {self.migration_table_name} ORDER BY version
                """))
                return [row[0] for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def _record_migration(self, migration: Migration) -> None:
        """Record a migration as applied."""
        try:
            with db_session_scope() as session:
                session.execute(text(f"""
                    INSERT INTO {self.migration_table_name} (version, description, applied_at)
                    VALUES (:version, :description, :applied_at)
                """), {
                    'version': migration.version,
                    'description': migration.description,
                    'applied_at': migration.applied_at
                })
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to record migration {migration.version}: {e}")
            raise MigrationError(f"Migration recording failed: {e}")
    
    def _remove_migration_record(self, version: str) -> None:
        """Remove migration record."""
        try:
            with db_session_scope() as session:
                session.execute(text(f"""
                    DELETE FROM {self.migration_table_name} WHERE version = :version
                """), {'version': version})
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to remove migration record {version}: {e}")
            raise MigrationError(f"Migration record removal failed: {e}")
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        try:
            self._ensure_migration_table()
            applied_versions = self._get_applied_migrations()
            
            pending_migrations = []
            applied_migrations = []
            
            for migration in self.migrations:
                if migration.version in applied_versions:
                    applied_migrations.append({
                        'version': migration.version,
                        'description': migration.description,
                        'status': 'applied'
                    })
                else:
                    pending_migrations.append({
                        'version': migration.version,
                        'description': migration.description,
                        'status': 'pending'
                    })
            
            return {
                'total_migrations': len(self.migrations),
                'applied_count': len(applied_migrations),
                'pending_count': len(pending_migrations),
                'applied_migrations': applied_migrations,
                'pending_migrations': pending_migrations,
                'current_version': applied_versions[-1] if applied_versions else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {'error': str(e)}
    
    def migrate_to_latest(self) -> bool:
        """Apply all pending migrations."""
        try:
            logger.info("Starting database migration to latest version")
            
            self._ensure_migration_table()
            applied_versions = set(self._get_applied_migrations())
            
            migrations_applied = 0
            
            for migration in self.migrations:
                if migration.version not in applied_versions:
                    try:
                        with db_session_scope() as session:
                            migration.apply(session)
                            session.commit()
                        
                        self._record_migration(migration)
                        migrations_applied += 1
                        
                        logger.info(f"Successfully applied migration {migration.version}")
                        
                    except Exception as e:
                        logger.error(f"Failed to apply migration {migration.version}: {e}")
                        raise MigrationError(f"Migration {migration.version} failed: {e}")
            
            if migrations_applied > 0:
                logger.info(f"Applied {migrations_applied} migrations successfully")
            else:
                logger.info("Database is already up to date")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration to latest failed: {e}")
            raise MigrationError(f"Migration failed: {e}")
    
    def migrate_to_version(self, target_version: str) -> bool:
        """
        Migrate to a specific version.
        
        Args:
            target_version: Target migration version
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Migrating database to version {target_version}")
            
            self._ensure_migration_table()
            applied_versions = set(self._get_applied_migrations())
            
            # Find target migration
            target_migration = None
            for migration in self.migrations:
                if migration.version == target_version:
                    target_migration = migration
                    break
            
            if not target_migration:
                raise MigrationError(f"Migration version {target_version} not found")
            
            # Apply migrations up to target version
            for migration in self.migrations:
                if migration.version <= target_version and migration.version not in applied_versions:
                    try:
                        with db_session_scope() as session:
                            migration.apply(session)
                            session.commit()
                        
                        self._record_migration(migration)
                        logger.info(f"Applied migration {migration.version}")
                        
                    except Exception as e:
                        logger.error(f"Failed to apply migration {migration.version}: {e}")
                        raise MigrationError(f"Migration {migration.version} failed: {e}")
                
                elif migration.version > target_version and migration.version in applied_versions:
                    # Need to rollback this migration
                    try:
                        with db_session_scope() as session:
                            migration.rollback(session)
                            session.commit()
                        
                        self._remove_migration_record(migration.version)
                        logger.info(f"Rolled back migration {migration.version}")
                        
                    except Exception as e:
                        logger.error(f"Failed to rollback migration {migration.version}: {e}")
                        raise MigrationError(f"Rollback of {migration.version} failed: {e}")
            
            logger.info(f"Successfully migrated to version {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Migration to version {target_version} failed: {e}")
            raise MigrationError(f"Migration failed: {e}")
    
    def rollback_migration(self, version: str) -> bool:
        """
        Rollback a specific migration.
        
        Args:
            version: Migration version to rollback
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Rolling back migration {version}")
            
            applied_versions = self._get_applied_migrations()
            
            if version not in applied_versions:
                raise MigrationError(f"Migration {version} is not currently applied")
            
            # Find migration
            migration_to_rollback = None
            for migration in self.migrations:
                if migration.version == version:
                    migration_to_rollback = migration
                    break
            
            if not migration_to_rollback:
                raise MigrationError(f"Migration {version} not found")
            
            # Rollback migration
            with db_session_scope() as session:
                migration_to_rollback.rollback(session)
                session.commit()
            
            self._remove_migration_record(version)
            
            logger.info(f"Successfully rolled back migration {version}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback of migration {version} failed: {e}")
            raise MigrationError(f"Rollback failed: {e}")
    
    def reset_database(self, confirm: bool = False) -> bool:
        """
        Reset database to clean state.
        
        Args:
            confirm: Confirmation flag (required for safety)
            
        Returns:
            True if successful
        """
        if not confirm:
            raise MigrationError("Database reset requires explicit confirmation")
        
        try:
            logger.warning("Resetting database to clean state")
            
            db_manager = get_database_manager()
            
            # Drop all tables
            Base.metadata.drop_all(db_manager.engine)
            
            # Remove migration table
            try:
                with db_session_scope() as session:
                    session.execute(text(f"DROP TABLE IF EXISTS {self.migration_table_name}"))
                    session.commit()
            except Exception:
                pass  # Table might not exist
            
            logger.warning("Database reset completed")
            return True
            
        except Exception as e:
            logger.error(f"Database reset failed: {e}")
            raise MigrationError(f"Reset failed: {e}")


 