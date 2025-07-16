#!/usr/bin/env python3
"""
Check password hash format for existing users
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import cloud_db_connection
import hashlib

def check_password_hashes():
    print("🔍 Checking password hash formats...")
    
    try:
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash FROM users LIMIT 5")
            users = cursor.fetchall()
            
            print(f"📋 Password hash analysis:")
            for user in users:
                user_id, username, password_hash = user
                print(f"\n👤 User: {username} (ID: {user_id})")
                print(f"   Hash: {password_hash}")
                print(f"   Hash length: {len(password_hash) if password_hash else 0}")
                print(f"   Hash type: {'SHA-256' if password_hash and len(password_hash) == 64 else 'Other'}")
                
                # Test common passwords
                test_passwords = ["password", "123456", "demo", "test", "admin"]
                for test_pwd in test_passwords:
                    test_hash = hashlib.sha256(test_pwd.encode()).hexdigest()
                    if test_hash == password_hash:
                        print(f"   ✅ Password found: '{test_pwd}'")
                        break
                else:
                    print(f"   ❓ Password not found in common list")
                    
    except Exception as e:
        print(f"❌ Failed to check password hashes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_password_hashes() 