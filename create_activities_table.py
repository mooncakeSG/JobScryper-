#!/usr/bin/env python3
"""
Create activities table manually
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db import cloud_db_connection

def create_activities_table():
    print("🔧 Creating activities table...")
    
    try:
        with cloud_db_connection() as conn:
            # Check if activities table exists
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activities'").fetchone()
            if result:
                print("✅ Activities table already exists")
                return
            
            # Create activities table
            print("📊 Creating activities table...")
            conn.execute("""
                CREATE TABLE activities (
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
            """)
            
            # Create indexes
            print("📈 Creating indexes...")
            conn.execute("""
                CREATE INDEX ix_activities_user_created 
                ON activities(user_id, created_at)
            """)
            conn.execute("""
                CREATE INDEX ix_activities_type 
                ON activities(activity_type)
            """)
            conn.execute("""
                CREATE INDEX ix_activities_entity 
                ON activities(entity_type, entity_id)
            """)
            
            conn.commit()
            print("✅ Activities table created successfully!")
            
            # Verify table was created
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activities'").fetchone()
            if result:
                print("✅ Activities table verified!")
                
                # Check table structure
                columns = conn.execute("PRAGMA table_info(activities)").fetchall()
                print(f"📋 Table has {len(columns)} columns:")
                for col in columns:
                    print(f"   - {col[1]} ({col[2]})")
            else:
                print("❌ Activities table not found after creation")
                
    except Exception as e:
        print(f"❌ Error creating activities table: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_activities_table() 