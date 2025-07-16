#!/usr/bin/env python3
"""
Test script to check database connectivity and create a test user
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db import cloud_db_connection, fetch_user_by_username_or_email
from database.connection import init_database
import hashlib

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("🔍 Testing database connectivity and user creation...")
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        init_database("development")
        print("✅ Database initialized")
        
        # Test database connection
        print("🔗 Testing database connection...")
        with cloud_db_connection() as conn:
            # Check if users table exists
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
            if result:
                print("✅ Users table exists")
            else:
                print("❌ Users table does not exist")
                return
            
            # Check for demo user
            demo_user = conn.execute("SELECT id, username, email FROM users WHERE username = 'demo' OR email = 'demo@autoapplyer.com'").fetchone()
            if demo_user:
                print(f"✅ Demo user found: ID={demo_user[0]}, Username={demo_user[1]}, Email={demo_user[2]}")
            else:
                print("❌ Demo user not found")
                
                # Create demo user
                print("👤 Creating demo user...")
                hashed_password = hash_password("demo123")
                conn.execute(
                    "INSERT INTO users (username, password_hash, email, is_active, is_verified, created_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                    ("demo", hashed_password, "demo@autoapplyer.com", True, True)
                )
                conn.commit()
                print("✅ Demo user created successfully")
                
                # Verify user was created
                demo_user = conn.execute("SELECT id, username, email FROM users WHERE username = 'demo'").fetchone()
                print(f"✅ Demo user verified: ID={demo_user[0]}, Username={demo_user[1]}, Email={demo_user[2]}")
        
        # Test user lookup function
        print("🔍 Testing user lookup...")
        user = fetch_user_by_username_or_email("demo")
        if user:
            print(f"✅ User lookup successful: ID={user[0]}, Username={user[1]}")
        else:
            print("❌ User lookup failed")
            
        print("\n🎉 Database test completed successfully!")
        print("\n📝 Login credentials:")
        print("   Username: demo")
        print("   Password: demo123")
        print("   Email: demo@autoapplyer.com")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 