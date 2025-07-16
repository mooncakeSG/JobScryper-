#!/usr/bin/env python3
"""
Check users in the database to debug login issues
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection

def check_users():
    """Check all users in the database"""
    print("🔍 Checking users in database...")
    
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("Users table columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            print()
            
            # Check if table has data
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            print(f"Total users in database: {count}")
            
            if count > 0:
                cursor.execute("SELECT id, username, email, password_hash FROM users")
                users = cursor.fetchall()
                
                print(f"Found {len(users)} users:")
                for user in users:
                    user_id, username, email, password_hash = user
                    print(f"  ID: {user_id}, Username: {username}, Email: {email}")
                    print(f"  Password hash: {password_hash[:50]}..." if password_hash else "  Password hash: None")
                    print()
            else:
                print("No users found in database")
                
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_users() 