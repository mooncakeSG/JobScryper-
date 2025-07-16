"""
Pytest configuration and fixtures for Auto Applyer tests
"""
import sqlite3
import os
import pytest
from pathlib import Path
import sys

# Add the parent directory to the Python path to import modules
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create required tables for testing"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./auto_applyer.db")
    db_path = db_url.replace("sqlite:///", "")
    
    # Ensure we have an absolute path
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.getcwd(), db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            resume_text TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_verified BOOLEAN DEFAULT FALSE,
            two_fa_enabled BOOLEAN DEFAULT FALSE
        )
    """)

    # Create job_applications table (matching backend expectations)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'pending',
            application_date TEXT,
            salary_min INTEGER,
            salary_max INTEGER,
            job_url TEXT,
            interview_date TEXT,
            notes TEXT,
            match_score INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Insert a test user for foreign key constraints
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, email, password_hash, is_verified)
        VALUES (1, 'test_user', 'test@example.com', 'test_hash', TRUE)
    """)

    conn.commit()
    conn.close()
    
    print("✅ Test database setup complete")
    
    yield
    
    # Cleanup (optional - uncomment if you want to clean up after tests)
    # print("Cleaning up test database...")
    # os.remove(db_path)

@pytest.fixture(scope="function")
def clean_database():
    """Clean database tables before each test function"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///auto_applyer.db")
    
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear data but keep tables
        cursor.execute("DELETE FROM job_applications")
        cursor.execute("DELETE FROM users WHERE id > 1")  # Keep the test user
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='job_applications'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        
        conn.commit()
        conn.close()
    
    yield

@pytest.fixture(scope="session", autouse=True)
def override_auth():
    """Override authentication for all tests"""
    try:
        from backend.main import app, get_current_user
        
        # Dummy user override for authentication
        def override_get_current_user():
            return {
                "id": 1,
                "username": "test_user",
                "email": "test@example.com"
            }
        
        # Apply the override globally for testing
        app.dependency_overrides[get_current_user] = override_get_current_user
        print("✅ Authentication override applied for tests")
        
    except ImportError as e:
        print(f"⚠️  Could not import backend modules: {e}")
    
    yield
    
    # Clean up override
    try:
        from backend.main import app, get_current_user
        app.dependency_overrides.pop(get_current_user, None)
    except ImportError:
        pass