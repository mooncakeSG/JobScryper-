#!/usr/bin/env python3
"""
Test the backend's database connection directly
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection
import requests

def test_backend_connection():
    """Test the backend's database connection"""
    print("🔍 Testing backend's database connection...")
    
    # Test registration via API
    data = {
        "username": "backend_test_user",
        "password": "backend_test_pass",
        "email": "backend_test@example.com"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=data)
        print(f"Registration response: {response.status_code}")
        print(f"Registration body: {response.json()}")
        
        # Use the same database connection as the backend
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check database file
            cursor.execute("PRAGMA database_list")
            databases = cursor.fetchall()
            print("Backend database files:")
            for db in databases:
                print(f"  {db[1]}: {db[2]}")
            
            # Check for our test user
            cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", ("backend_test_user",))
            user = cursor.fetchone()
            if user:
                user_id, username, email, password_hash = user
                print(f"Found test user: ID={user_id}, Username={username}, Email={email}")
                print(f"Password hash: {password_hash[:50]}..." if password_hash else "Password hash: None")
                
                # Test login with this user
                login_data = {
                    "username": "backend_test_user",
                    "password": "backend_test_pass"
                }
                login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
                print(f"Login response: {login_response.status_code}")
                print(f"Login body: {login_response.json()}")
            else:
                print("Test user not found in backend database")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backend_connection() 