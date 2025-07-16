#!/usr/bin/env python3
"""
Check all possible database files
"""

import requests
import sqlite3
import os
import glob

def check_all_databases():
    """Check all possible database files"""
    print("🔍 Checking all possible database files...")
    
    # Test registration via API
    data = {
        "username": "db_check_user",
        "password": "db_check_pass",
        "email": "db_check@example.com"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=data)
        print(f"Registration response: {response.status_code}")
        print(f"Registration body: {response.json()}")
        
        if response.status_code == 200:
            user_id = response.json().get("user_id")
            print(f"Returned user_id: {user_id}")
            
            # Find all database files
            db_files = []
            
            # Check current directory
            if os.path.exists("auto_applyer.db"):
                db_files.append("auto_applyer.db")
            
            # Check parent directory
            if os.path.exists("../auto_applyer.db"):
                db_files.append("../auto_applyer.db")
            
            # Check backend directory
            if os.path.exists("backend/auto_applyer.db"):
                db_files.append("backend/auto_applyer.db")
            
            # Check for any .db files
            db_files.extend(glob.glob("*.db"))
            db_files.extend(glob.glob("../*.db"))
            db_files.extend(glob.glob("backend/*.db"))
            
            # Remove duplicates
            db_files = list(set(db_files))
            
            print(f"Found database files: {db_files}")
            
            # Check each database file
            for db_file in db_files:
                print(f"\nChecking {db_file}:")
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Check if users table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                    if not cursor.fetchone():
                        print(f"  No users table in {db_file}")
                        conn.close()
                        continue
                    
                    # Check for our test user
                    cursor.execute("SELECT id, username, email FROM users WHERE username = ?", ("db_check_user",))
                    user = cursor.fetchone()
                    if user:
                        print(f"  ✅ Found user: {user}")
                    else:
                        print(f"  ❌ User not found")
                    
                    # Check total users
                    cursor.execute("SELECT COUNT(*) FROM users")
                    count = cursor.fetchone()[0]
                    print(f"  Total users: {count}")
                    
                    # List all users
                    cursor.execute("SELECT id, username, email FROM users ORDER BY id")
                    users = cursor.fetchall()
                    print(f"  All users: {users}")
                    
                    conn.close()
                    
                except Exception as e:
                    print(f"  ❌ Error checking {db_file}: {e}")
            
        else:
            print("❌ Registration failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_all_databases() 