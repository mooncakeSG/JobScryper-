#!/usr/bin/env python3
"""
Fix demo user password
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db import cloud_db_connection
import hashlib

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def fix_demo_user():
    print("🔧 Fixing demo user password...")
    
    try:
        with cloud_db_connection() as conn:
            # Check current demo user
            demo = conn.execute("SELECT id, username, email FROM users WHERE username = 'demo'").fetchone()
            if not demo:
                print("❌ Demo user not found")
                return
            
            print(f"✅ Found demo user: ID={demo[0]}, Username={demo[1]}, Email={demo[2]}")
            
            # Update password to "demo123"
            new_password_hash = hash_password("demo123")
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (new_password_hash, "demo")
            )
            conn.commit()
            
            print("✅ Demo user password updated successfully!")
            print(f"   New password hash: {new_password_hash[:20]}...")
            
            # Verify the update
            updated_user = conn.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                ("demo",)
            ).fetchone()
            
            if updated_user and updated_user[0] == new_password_hash:
                print("✅ Password update verified!")
            else:
                print("❌ Password update verification failed")
                
    except Exception as e:
        print(f"❌ Error updating demo user: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Demo user fix completed!")
    print("\n📝 Login credentials:")
    print("   Username: demo")
    print("   Password: demo123")

if __name__ == "__main__":
    fix_demo_user() 