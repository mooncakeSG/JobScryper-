#!/usr/bin/env python3
"""
Test registration and check database immediately after
"""

import requests
import sys
sys.path.append('backend')
from db import cloud_db_connection

def test_registration_and_check():
    """Test registration and check database"""
    print("🔍 Testing registration and checking database...")
    
    # Test registration
    data = {
        "username": "debuguser",
        "password": "debugpass123",
        "email": "debuguser@example.com"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=data)
        print(f"Registration response: {response.status_code}")
        print(f"Registration body: {response.json()}")
        
        # Check database immediately after
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", ("debuguser",))
            user = cursor.fetchone()
            
            if user:
                user_id, username, email, password_hash = user
                print(f"Database user: ID={user_id}, Username={username}, Email={email}")
                print(f"Password hash: {password_hash}")
                print(f"Password hash length: {len(password_hash) if password_hash else 0}")
            else:
                print("User not found in database after registration")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration_and_check() 