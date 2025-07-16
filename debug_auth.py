#!/usr/bin/env python3
"""
Debug script for authentication issues
"""

import hashlib
import requests
import json

BACKEND_URL = "http://localhost:8000"

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def test_password_hashing():
    """Test password hashing consistency"""
    password = "testpass123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    print(f"Password: {password}")
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    print(f"Hashes match: {hash1 == hash2}")
    return hash1

def test_signup_and_verify():
    """Test signup and then verify the stored password"""
    username = "debugtest"
    password = "testpass123"
    
    # Delete user if exists
    try:
        requests.delete(f"{BACKEND_URL}/api/auth/users/{username}")
    except:
        pass
    
    # Signup
    signup_data = {
        "username": username,
        "password": password,
        "email": "debug@test.com"
    }
    
    print(f"\n=== Testing Signup ===")
    response = requests.post(f"{BACKEND_URL}/api/auth/signup", json=signup_data)
    print(f"Signup Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Signup Response: {response.json()}")
    else:
        print(f"Signup Error: {response.text}")
        return
    
    # Check what's stored in database
    print(f"\n=== Checking Database ===")
    try:
        import sqlite3
        conn = sqlite3.connect('data/auto_applyer.db')
        cursor = conn.execute("SELECT username, password_hash FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            print(f"Stored username: {user[0]}")
            print(f"Stored password_hash: {user[1]}")
            print(f"Expected hash: {hash_password(password)}")
            print(f"Hash matches: {user[1] == hash_password(password)}")
        else:
            print("User not found in database")
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
    
    # Test login
    print(f"\n=== Testing Login ===")
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Login Response: {response.json()}")
    else:
        print(f"Login Error: {response.text}")

def test_existing_user():
    """Test login with an existing user"""
    print(f"\n=== Testing Existing User ===")
    
    # Try to login with the user we created in the integration test
    login_data = {
        "username": "frontendtest",
        "password": "testpass123"
    }
    response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Login Response: {response.json()}")
    else:
        print(f"Login Error: {response.text}")
        
        # Check what's in the database
        try:
            import sqlite3
            conn = sqlite3.connect('data/auto_applyer.db')
            cursor = conn.execute("SELECT username, password_hash FROM users WHERE username = ?", ("frontendtest",))
            user = cursor.fetchone()
            if user:
                print(f"Stored username: {user[0]}")
                print(f"Stored password_hash: {user[1]}")
                print(f"Expected hash: {hash_password('testpass123')}")
                print(f"Hash matches: {user[1] == hash_password('testpass123')}")
            else:
                print("User not found in database")
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")

def main():
    """Run all debug tests"""
    print("🔍 Debugging Authentication Issues")
    print("=" * 50)
    
    # Test password hashing
    test_password_hashing()
    
    # Test signup and verify
    test_signup_and_verify()
    
    # Test existing user
    test_existing_user()

if __name__ == "__main__":
    main() 