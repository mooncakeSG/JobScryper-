#!/usr/bin/env python3
"""
Script to create the user_preferences table
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import cloud_db_connection
from datetime import datetime

def create_user_preferences_table():
    """Create the user_preferences table if it doesn't exist."""
    try:
        with cloud_db_connection() as conn:
            # Check if table exists
            result = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='user_preferences'
            """).fetchone()
            
            if result:
                print("✅ user_preferences table already exists")
                return
            
            # Create the table
            conn.execute("""
                CREATE TABLE user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    preferred_job_titles TEXT,
                    preferred_locations TEXT,
                    preferred_job_types TEXT,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    salary_currency VARCHAR(20) DEFAULT 'USD',
                    remote_work_preference BOOLEAN DEFAULT FALSE,
                    max_results_per_search INTEGER DEFAULT 50,
                    auto_apply_enabled BOOLEAN DEFAULT FALSE,
                    job_sources TEXT,
                    email_notifications BOOLEAN DEFAULT TRUE,
                    application_reminders BOOLEAN DEFAULT TRUE,
                    daily_job_alerts BOOLEAN DEFAULT FALSE,
                    ai_suggestions_enabled BOOLEAN DEFAULT TRUE,
                    ats_analysis_enabled BOOLEAN DEFAULT TRUE,
                    auto_resume_optimization BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
            print("✅ user_preferences table created successfully")
            
            # Create index for better performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id 
                ON user_preferences(user_id)
            """)
            
            conn.commit()
            print("✅ Index created successfully")
            
    except Exception as e:
        print(f"❌ Error creating user_preferences table: {e}")
        raise

if __name__ == "__main__":
    create_user_preferences_table() 