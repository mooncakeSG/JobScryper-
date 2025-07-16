#!/usr/bin/env python3
"""
Check password hash in backend database
"""

import sqlite3
import hashlib

def check_backend_db_password():
    """Check password hash in backend database"""
    print("🔍 Checking password hash in backend database...")
    
    try:
        # Connect to backend database
        conn = sqlite3.connect("backend/auto_applyer.db")
        cursor = conn.cursor()
        
        # Get the user we just created
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", ("db_check_user",))
        user = cursor.fetchone()
        
        if user:
            user_id, username, email, password_hash = user
            print(f"User: ID={user_id}, Username={username}, Email={email}")
            print(f"Stored password hash: {password_hash}")
            
            # Test password verification
            test_password = "db_check_pass"
            test_hash = hashlib.sha256(test_password.encode()).hexdigest()
            print(f"Test password hash: {test_hash}")
            
            if password_hash == test_hash:
                print("✅ Password hashes match!")
            else:
                print("❌ Password hashes don't match!")
                print(f"Length comparison: stored={len(password_hash)}, test={len(test_hash)}")
                
                # Check if it's a bcrypt hash
                if password_hash.startswith('$2b$'):
                    print("Stored hash appears to be bcrypt")
                else:
                    print("Stored hash appears to be SHA-256")
        else:
            print("❌ User not found in backend database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_backend_db_password() 