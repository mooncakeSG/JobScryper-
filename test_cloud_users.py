#!/usr/bin/env python3
"""
Test users in SQLite Cloud database
"""

import os
from dotenv import load_dotenv
import sqlitecloud

load_dotenv()

SQLITE_CLOUD_URL = (
    f"sqlitecloud://{os.getenv('SQLITE_CLOUD_HOST')}:{os.getenv('SQLITE_CLOUD_PORT', '8860')}/"
    f"{os.getenv('SQLITE_CLOUD_DATABASE')}?apikey={os.getenv('SQLITE_CLOUD_API_KEY')}"
)

def test_cloud_users():
    """Test users in SQLite Cloud database"""
    print("🔍 Testing users in SQLite Cloud database...")
    
    try:
        conn = sqlitecloud.connect(SQLITE_CLOUD_URL)
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("Users table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        print()
        
        # Check user count
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"Total users: {count}")
        
        # Get all users
        cursor.execute("SELECT id, username, email, password_hash FROM users")
        users = cursor.fetchall()
        print("\nAll users:")
        for user in users:
            user_id, username, email, password_hash = user
            print(f"  ID: {user_id}, Username: {username}, Email: {email}")
            print(f"  Password hash: {password_hash[:50]}..." if password_hash else "  Password hash: None")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cloud_users() 