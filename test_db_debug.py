#!/usr/bin/env python3
"""
Debug database issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import cloud_db_connection, create_user, fetch_user_by_username_or_email
import hashlib

def test_database_operations():
    print("🔍 Testing database operations...")
    
    # Test 1: Check database connection
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✅ Database connected. Tables: {[t[0] for t in tables]}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test 2: Check users table structure
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print(f"📋 Users table columns:")
            for col in columns:
                print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PRIMARY KEY' if col[5] else ''}")
    except Exception as e:
        print(f"❌ Failed to get table info: {e}")
    
    # Test 3: Check if test user exists
    test_username = "testuser_debug"
    existing_user = fetch_user_by_username_or_email(test_username)
    if existing_user:
        print(f"⚠️  Test user '{test_username}' already exists (ID: {existing_user[0]})")
        # Delete the test user
        try:
            with cloud_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
                print(f"🗑️  Deleted existing test user")
        except Exception as e:
            print(f"❌ Failed to delete existing user: {e}")
    else:
        print(f"✅ Test user '{test_username}' does not exist")
    
    # Test 4: Try to create a user manually
    try:
        username = "testuser_debug"
        email = "test@example.com"
        password = "testpass123"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        print(f"🔧 Creating user manually...")
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, created_at, is_verified, is_active)
                VALUES (?, ?, ?, datetime('now'), 0, 1)
            """, (username, email, hashed_password))
            user_id = cursor.lastrowid
            print(f"✅ User created successfully with ID: {user_id}")
            
            # Verify the user was created
            cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                print(f"✅ User verified: {user}")
            else:
                print(f"❌ User not found after creation")
                
    except Exception as e:
        print(f"❌ Manual user creation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Test the create_user function
    try:
        print(f"🔧 Testing create_user function...")
        user_id = create_user("testuser_func", "testfunc@example.com", hashed_password)
        if user_id:
            print(f"✅ create_user function succeeded: {user_id}")
        else:
            print(f"❌ create_user function returned None")
    except Exception as e:
        print(f"❌ create_user function failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_operations() 