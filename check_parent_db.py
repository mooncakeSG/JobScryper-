#!/usr/bin/env python3
"""
Check the parent directory's database
"""

import sqlite3
import os

def check_parent_db():
    """Check the parent directory's database"""
    print("🔍 Checking parent directory's database...")
    
    parent_db_path = "../auto_applyer.db"
    
    if os.path.exists(parent_db_path):
        print(f"Found database at: {os.path.abspath(parent_db_path)}")
        
        conn = sqlite3.connect(parent_db_path)
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
        
        # Check for our test user
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", ("db_test_user",))
        user = cursor.fetchone()
        if user:
            user_id, username, email, password_hash = user
            print(f"Found test user: ID={user_id}, Username={username}, Email={email}")
            print(f"Password hash: {password_hash[:50]}..." if password_hash else "Password hash: None")
        else:
            print("Test user not found")
        
        # List all users
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        print("\nAll users:")
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        
        conn.close()
    else:
        print(f"Database not found at: {os.path.abspath(parent_db_path)}")

if __name__ == "__main__":
    check_parent_db() 