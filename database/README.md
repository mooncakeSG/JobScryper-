# Auto Applyer Database System

A comprehensive database system for managing job applications, user profiles, resumes, and search history with support for both SQLite (development) and PostgreSQL (production).

## 🏗️ Architecture Overview

The database system consists of several key components:

- **Models**: SQLAlchemy models defining the database schema
- **Connection Management**: Database connection handling with environment-specific configurations
- **Utilities**: High-level CRUD operations and data management
- **Migrations**: Schema versioning and upgrade system
- **Backup/Restore**: Data backup and recovery functionality

## 📋 Database Schema

### Core Tables

#### Users (`users`)
- **Purpose**: Store user profiles and authentication information
- **Key Fields**: `email`, `first_name`, `last_name`, `location`, `job_title`, `experience_years`, `skills`
- **Relationships**: One-to-many with resumes, job applications, search history

#### User Preferences (`user_preferences`)
- **Purpose**: Store user-specific settings and preferences
- **Key Fields**: `preferred_job_titles`, `preferred_locations`, `salary_min/max`, `remote_work_preference`
- **Relationships**: One-to-one with users

#### Resumes (`resumes`)
- **Purpose**: Store resume files and parsed content
- **Key Fields**: `filename`, `file_path`, `parsed_text`, `skills_extracted`, `experience_level`
- **Relationships**: Many-to-one with users, one-to-many with job applications

#### Job Applications (`job_applications`)
- **Purpose**: Track job applications and their status
- **Key Fields**: `job_title`, `company`, `location`, `status`, `salary_min/max`, `match_score`
- **Relationships**: Many-to-one with users and resumes

#### Search History (`search_history`)
- **Purpose**: Track search queries and results for analytics
- **Key Fields**: `job_title`, `location`, `keywords`, `total_results`, `search_duration`
- **Relationships**: Many-to-one with users

### Support Tables

#### AI Analysis Cache (`ai_analysis_cache`)
- **Purpose**: Cache AI analysis results to avoid reprocessing
- **Key Fields**: `cache_key`, `analysis_type`, `results`, `expires_at`

#### System Settings (`system_settings`)
- **Purpose**: Store system-wide configuration
- **Key Fields**: `setting_key`, `setting_value`, `setting_type`

#### Schema Migrations (`schema_migrations`)
- **Purpose**: Track applied database migrations
- **Key Fields**: `version`, `description`, `applied_at`

## 🚀 Quick Start

### 1. Initialize Database

```bash
# Development environment (SQLite)
python database/init_db.py --environment development

# Production environment (PostgreSQL)
python database/init_db.py --environment production

# Reset database (WARNING: destroys all data)
python database/init_db.py --environment development --reset
```

### 2. Basic Usage

```python
from database.connection import init_database
from database.utilities import DatabaseUtils

# Initialize database
init_database("development")

# Create a user
user = DatabaseUtils.create_user(
    email="user@example.com",
    first_name="John",
    last_name="Doe",
    location="Cape Town",
    job_title="Software Developer",
    skills=["Python", "JavaScript", "SQL"]
)

# Add job application
application = DatabaseUtils.add_job_application(
    user_id=user.id,
    job_title="Senior Python Developer",
    company="TechCorp",
    location="Cape Town",
    status=ApplicationStatus.APPLIED,
    salary_min=80000,
    salary_max=120000,
    match_score=85.5
)

# Get user statistics
stats = DatabaseUtils.get_application_statistics(user.id, days=30)
print(f"Total applications: {stats['total_applications']}")
print(f"Interview rate: {stats['interview_rate']}%")
```

## 🔧 Configuration

### Environment Variables

For **production** (PostgreSQL):
```bash
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=auto_applyer
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600
DATABASE_TIMEOUT=30
```

For **development** (SQLite):
```bash
DATABASE_ECHO=false  # Set to true for SQL debugging
```

### Database Environments

#### Development (SQLite)
- **File**: `data/auto_applyer.db`
- **Features**: Full functionality, file-based storage
- **Use Case**: Local development, testing

#### Testing (In-Memory SQLite)
- **File**: `:memory:`
- **Features**: Fast, temporary, isolated
- **Use Case**: Unit/integration tests

#### Production (PostgreSQL)
- **Connection**: Network-based
- **Features**: Full ACID compliance, scalability, concurrent access
- **Use Case**: Production deployment

## 📊 Database Operations

### User Management

```python
from database.utilities import DatabaseUtils

# Create user with preferences
user = DatabaseUtils.create_user(
    email="user@example.com",
    first_name="John",
    last_name="Doe",
    location="Cape Town",
    job_title="Developer",
    experience_years=5,
    skills=["Python", "Django", "React"]
)

# Update user information
DatabaseUtils.update_user(
    user.id,
    job_title="Senior Developer",
    experience_years=7,
    skills=["Python", "Django", "React", "AWS"]
)

# Get user by email or ID
user = DatabaseUtils.get_user_by_email("user@example.com")
user = DatabaseUtils.get_user_by_id(1)

# Update user preferences
DatabaseUtils.update_user_preferences(
    user.id,
    preferred_job_titles=["Senior Developer", "Lead Developer"],
    preferred_locations=["Cape Town", "Remote"],
    salary_min=100000,
    salary_max=150000,
    remote_work_preference=True
)
```

### Resume Management

```python
# Add resume
resume = DatabaseUtils.add_resume(
    user_id=user.id,
    filename="john_doe_resume.pdf",
    file_path="/uploads/resumes/john_doe_resume.pdf",
    file_size=1024000,
    file_type="pdf",
    parsed_text="Experienced Python developer...",
    skills_extracted=["Python", "Django", "PostgreSQL"],
    experience_level="Senior"
)

# Get user resumes
resumes = DatabaseUtils.get_user_resumes(user.id)
active_resumes = DatabaseUtils.get_user_resumes(user.id, active_only=True)
```

### Job Application Tracking

```python
# Add job application
application = DatabaseUtils.add_job_application(
    user_id=user.id,
    job_title="Senior Python Developer",
    company="TechCorp",
    location="Cape Town",
    job_description="Looking for senior Python developer...",
    job_url="https://example.com/jobs/123",
    status=ApplicationStatus.APPLIED,
    source="linkedin",
    salary_min=100000,
    salary_max=130000,
    job_type="Full-time",
    is_remote=False,
    match_score=92.5
)

# Get applications
applications = DatabaseUtils.get_user_applications(user.id)
recent_apps = DatabaseUtils.get_user_applications(user.id, limit=10)
applied_apps = DatabaseUtils.get_user_applications(user.id, status=ApplicationStatus.APPLIED)

# Update application status
DatabaseUtils.update_application_status(
    application.id,
    ApplicationStatus.INTERVIEW_SCHEDULED,
    notes="Phone interview scheduled for tomorrow at 10 AM",
    interview_date=datetime(2024, 1, 15, 10, 0),
    interview_type="Phone"
)
```

### Analytics and Statistics

```python
# Get user application statistics
stats = DatabaseUtils.get_application_statistics(user.id, days=30)

print(f"Total applications: {stats['total_applications']}")
print(f"Recent applications: {stats['recent_applications']}")
print(f"Interview rate: {stats['interview_rate']}%")
print(f"Average match score: {stats['average_match_score']}")
print(f"Status breakdown: {stats['status_breakdown']}")
```

### Search History

```python
# Add search history
DatabaseUtils.add_search_history(
    user_id=user.id,
    job_title="Python Developer",
    location="Cape Town",
    keywords="Python Django PostgreSQL",
    sources_searched=["linkedin", "indeed", "glassdoor"],
    max_results=100,
    total_results=85,
    filtered_results=25,
    applications_made=3,
    search_duration=5.2
)
```

## 🔄 Migrations

### Migration System

The database uses a custom migration system for schema versioning:

```python
from database.migrations import MigrationManager

migration_manager = MigrationManager()

# Check migration status
status = migration_manager.get_migration_status()
print(f"Applied: {status['applied_count']}")
print(f"Pending: {status['pending_count']}")

# Apply all pending migrations
migration_manager.migrate_to_latest()

# Migrate to specific version
migration_manager.migrate_to_version("002")

# Rollback migration
migration_manager.rollback_migration("003")
```

### Available Migrations

1. **Migration 001**: Initial database schema
2. **Migration 002**: Performance indexes
3. **Migration 003**: Full-text search support

### Creating Custom Migrations

```python
def migration_004_upgrade(session: Session) -> None:
    """Add new column example."""
    session.execute(text("""
        ALTER TABLE users ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE
    """))

def migration_004_downgrade(session: Session) -> None:
    """Remove new column example."""
    session.execute(text("""
        ALTER TABLE users DROP COLUMN phone_verified
    """))

# Register migration
migration_manager.migrations.append(Migration(
    "004",
    "Add phone verification field",
    migration_004_upgrade,
    migration_004_downgrade
))
```

## 💾 Backup and Restore

### Create Backup

```python
from database.utilities import BackupManager

backup_manager = BackupManager()

# Create backup
backup_path = backup_manager.create_backup("my_backup")
print(f"Backup created: {backup_path}")

# Create backup with automatic naming
backup_path = backup_manager.create_backup()  # Uses timestamp
```

### Restore Backup

```python
# Restore from backup (requires confirmation)
backup_manager.restore_backup(
    "/path/to/backup.json",
    confirm=True  # Required for safety
)

# List available backups
backups = backup_manager.list_backups()
for backup in backups:
    print(f"File: {backup['filename']}")
    print(f"Created: {backup['created']}")
    print(f"Size: {backup['size']} bytes")
    print(f"Environment: {backup['environment']}")
```

### Backup Format

Backups are stored in JSON format with the following structure:

```json
{
  "metadata": {
    "backup_date": "2024-01-15T10:30:00Z",
    "version": "1.0",
    "environment": "development"
  },
  "data": {
    "users": [...],
    "user_preferences": [...],
    "resumes": [...],
    "job_applications": [...],
    "search_history": [...]
  }
}
```

## 🧪 Testing

### Running Database Tests

```bash
# Run all database tests
pytest tests/integration/test_database.py -v

# Run specific test class
pytest tests/integration/test_database.py::TestDatabaseUtils -v

# Run with coverage
pytest tests/integration/test_database.py --cov=database --cov-report=html
```

### Test Database Setup

Tests use an in-memory SQLite database for speed and isolation:

```python
def setup_method(self):
    """Set up test database."""
    cleanup_database()
    self.db_manager = init_database("testing", drop_existing=True)

def teardown_method(self):
    """Clean up after tests."""
    cleanup_database()
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Problem**: `DatabaseError: Database not initialized`
**Solution**: Initialize the database first
```python
from database.connection import init_database
init_database("development")
```

#### 2. Migration Errors

**Problem**: `MigrationError: Migration 002 failed`
**Solution**: Check migration status and manually fix
```python
migration_manager = MigrationManager()
status = migration_manager.get_migration_status()
print(status)
```

#### 3. SQLite Lock Errors

**Problem**: `database is locked`
**Solution**: Ensure proper session management
```python
# Always use session scope
with db_session_scope() as session:
    # Your database operations
    pass
```

#### 4. PostgreSQL Connection Issues

**Problem**: `connection refused`
**Solution**: Check environment variables and PostgreSQL service
```bash
# Check PostgreSQL status
systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d auto_applyer
```

### Performance Optimization

#### 1. Database Indexes

The system automatically creates performance indexes during migration:

```sql
-- Application lookups
CREATE INDEX ix_job_applications_user_date ON job_applications(user_id, application_date);
CREATE INDEX ix_job_applications_status ON job_applications(status);

-- Resume lookups
CREATE INDEX ix_resumes_user_active ON resumes(user_id, is_active);

-- Search history
CREATE INDEX ix_search_history_user_date ON search_history(user_id, search_date);
```

#### 2. Connection Pooling

For production PostgreSQL:

```python
# Connection pool configuration
{
    'pool_size': 5,           # Number of connections to maintain
    'max_overflow': 10,       # Maximum overflow connections
    'pool_recycle': 3600,     # Recycle connections after 1 hour
    'pool_pre_ping': True     # Validate connections before use
}
```

#### 3. Query Optimization

```python
# Use specific queries instead of loading all data
applications = DatabaseUtils.get_user_applications(user_id, limit=20)

# Use filters to reduce data transfer
recent_apps = DatabaseUtils.get_user_applications(
    user_id, 
    status=ApplicationStatus.APPLIED,
    limit=10
)
```

## 📚 API Reference

### Connection Management

- `init_database(environment, drop_existing=False)`: Initialize database
- `get_database_manager()`: Get global database manager
- `get_db_session()`: Get new database session
- `db_session_scope()`: Context manager for transactions
- `cleanup_database()`: Clean up connections

### Database Utils

- `DatabaseUtils.create_user(email, **kwargs)`: Create user with preferences
- `DatabaseUtils.get_user_by_email(email)`: Get user by email
- `DatabaseUtils.get_user_by_id(user_id)`: Get user by ID
- `DatabaseUtils.update_user(user_id, **kwargs)`: Update user
- `DatabaseUtils.add_resume(user_id, filename, ...)`: Add resume
- `DatabaseUtils.get_user_resumes(user_id, active_only=True)`: Get resumes
- `DatabaseUtils.add_job_application(user_id, job_title, company, ...)`: Add application
- `DatabaseUtils.get_user_applications(user_id, status=None, limit=None)`: Get applications
- `DatabaseUtils.update_application_status(app_id, status, notes=None, ...)`: Update status
- `DatabaseUtils.get_application_statistics(user_id, days=30)`: Get stats
- `DatabaseUtils.get_user_preferences(user_id)`: Get preferences
- `DatabaseUtils.update_user_preferences(user_id, **kwargs)`: Update preferences

### Migration Manager

- `MigrationManager.get_migration_status()`: Get migration status
- `MigrationManager.migrate_to_latest()`: Apply all pending migrations
- `MigrationManager.migrate_to_version(version)`: Migrate to specific version
- `MigrationManager.rollback_migration(version)`: Rollback migration
- `MigrationManager.reset_database(confirm=False)`: Reset database

### Backup Manager

- `BackupManager.create_backup(backup_name=None)`: Create backup
- `BackupManager.restore_backup(backup_path, confirm=False)`: Restore backup
- `BackupManager.list_backups()`: List available backups

## 🔗 Integration with Main Application

### Streamlit Integration

```python
# In your Streamlit app
import streamlit as st
from database.connection import init_database, get_database_manager
from database.utilities import DatabaseUtils

# Initialize database on app startup
if 'db_initialized' not in st.session_state:
    init_database("development")
    st.session_state.db_initialized = True

# Use in your app
if 'user_id' in st.session_state:
    user_id = st.session_state.user_id
    
    # Get user applications
    applications = DatabaseUtils.get_user_applications(user_id, limit=10)
    
    # Display applications
    for app in applications:
        st.write(f"{app.job_title} at {app.company}")
        st.write(f"Status: {app.status.value}")
        st.write(f"Applied: {app.application_date}")
```

### Error Handling

```python
from utils.errors import DatabaseError, ValidationError

try:
    user = DatabaseUtils.create_user(email="test@example.com")
except ValidationError as e:
    st.error(f"Invalid input: {e}")
except DatabaseError as e:
    st.error(f"Database error: {e}")
    logger.error(f"Database error: {e}")
```

## 🎯 Best Practices

### 1. Session Management
- Always use `db_session_scope()` for database operations
- Don't keep sessions open longer than necessary
- Handle exceptions properly to ensure session cleanup

### 2. Data Validation
- Use the utilities module for complex operations
- Validate input data before database operations
- Handle unique constraint violations gracefully

### 3. Performance
- Use indexes for frequently queried columns
- Limit result sets with `limit` parameter
- Use specific queries instead of loading all data

### 4. Security
- Never expose database credentials in code
- Use environment variables for configuration
- Validate all user inputs before database operations

### 5. Backup Strategy
- Create regular backups in production
- Test backup restoration procedures
- Store backups in secure, separate location

## 🚀 Future Enhancements

### Planned Features

1. **Advanced Search**: Full-text search across job descriptions
2. **Analytics Dashboard**: Advanced reporting and analytics
3. **Data Export**: Export data in various formats (CSV, Excel, PDF)
4. **API Integration**: REST API for external applications
5. **Real-time Updates**: WebSocket support for real-time notifications
6. **Multi-tenant Support**: Support for multiple organizations
7. **Data Archiving**: Automated data archiving and cleanup
8. **Performance Monitoring**: Database performance tracking and alerts

### Contributing

When adding new features:

1. Create database models in `models.py`
2. Add utility functions in `utilities.py`
3. Create migrations in `migrations.py`
4. Add comprehensive tests in `tests/integration/test_database.py`
5. Update this documentation

---

This database system provides a robust foundation for the Auto Applyer application with comprehensive features for user management, job tracking, and data persistence. The modular design allows for easy extension and customization as the application grows. 