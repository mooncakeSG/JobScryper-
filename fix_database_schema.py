#!/usr/bin/env python3
"""
Fix database schema by adding missing columns
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection

def fix_database_schema():
    """Fix database schema by adding missing columns"""
    print("🔍 Fixing database schema...")
    
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check current schema
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("Current columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Add missing columns
            missing_columns = [
                "two_fa_secret TEXT",
                "backup_codes TEXT", 
                "email_verification_code TEXT",
                "email_verification_expires DATETIME",
                "email_verified BOOLEAN DEFAULT FALSE",
                "social_provider TEXT",
                "social_id TEXT",
                "profile_picture TEXT",
                "failed_login_attempts INTEGER DEFAULT 0",
                "password_changed_at DATETIME",
                "last_login DATETIME"
            ]
            
            for column_def in missing_columns:
                column_name = column_def.split()[0]
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_def}")
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️  Column {column_name} already exists")
                    else:
                        print(f"❌ Error adding column {column_name}: {e}")
            
            # Check final schema
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("\nFinal columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            print(f"\n✅ Database schema fixed! Total columns: {len(columns)}")
            
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_database_schema() 