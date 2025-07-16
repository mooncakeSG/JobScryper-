#!/usr/bin/env python3
"""
Test for transaction issues with user creation
"""

import sys
sys.path.append('backend')
from db import cloud_db_connection
import requests
import time

def test_transaction():
    """Test for transaction issues"""
    print("🔍 Testing for transaction issues...")
    
    # Test registration via API
    data = {
        "username": "transaction_test_user",
        "password": "transaction_test_pass",
        "email": "transaction_test@example.com"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=data)
        print(f"Registration response: {response.status_code}")
        print(f"Registration body: {response.json()}")
        
        # Wait a moment for any async operations
        time.sleep(1)
        
        # Check database multiple times
        for i in range(3):
            print(f"\nCheck {i+1}:")
            with cloud_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check database file
                cursor.execute("PRAGMA database_list")
                databases = cursor.fetchall()
                print(f"  Database: {databases[0][2] if databases else 'Unknown'}")
                
                # Check for our test user
                cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", ("transaction_test_user",))
                user = cursor.fetchone()
                if user:
                    user_id, username, email, password_hash = user
                    print(f"  Found user: ID={user_id}, Username={username}")
                    print(f"  Password hash: {password_hash[:50]}..." if password_hash else "  Password hash: None")
                else:
                    print("  User not found")
                
                # Check total user count
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                print(f"  Total users: {count}")
            
            if i < 2:  # Don't sleep after the last check
                time.sleep(2)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transaction() 