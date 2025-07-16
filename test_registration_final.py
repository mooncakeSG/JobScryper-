#!/usr/bin/env python3
"""
Final test to debug registration issue
"""

import requests
import sqlite3
import time

def test_registration_final():
    """Final test for registration issue"""
    print("🔍 Final registration test...")
    
    # Test registration via API
    data = {
        "username": "final_test_user2",
        "password": "final_test_pass",
        "email": "final_test2@example.com"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=data)
        print(f"Registration response: {response.status_code}")
        print(f"Registration body: {response.json()}")
        
        if response.status_code == 200:
            user_id = response.json().get("user_id")
            print(f"Returned user_id: {user_id}")
            
            # Wait a moment
            time.sleep(0.5)
            
            # Check database directly with SQLite
            db_path = "auto_applyer.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check by user_id
            cursor.execute("SELECT id, username, email, password_hash FROM users WHERE id = ?", (user_id,))
            user_by_id = cursor.fetchone()
            print(f"User by ID {user_id}: {user_by_id}")
            
            # Check by username
            cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", ("final_test_user2",))
            user_by_username = cursor.fetchone()
            print(f"User by username: {user_by_username}")
            
            # Check all users
            cursor.execute("SELECT id, username, email FROM users ORDER BY id")
            all_users = cursor.fetchall()
            print(f"All users: {all_users}")
            
            # Check if we can find the user by any means
            if user_by_id or user_by_username:
                print("✅ User found in database")
                
                # Try to login
                login_data = {
                    "username": "final_test_user2",
                    "password": "final_test_pass"
                }
                login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
                print(f"Login response: {login_response.status_code}")
                print(f"Login body: {login_response.json()}")
            else:
                print("❌ User not found in database")
            
            conn.close()
        else:
            print("❌ Registration failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration_final() 