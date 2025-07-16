#!/usr/bin/env python3
"""
Fix database path issue
"""

import os
import shutil

def fix_db_path():
    """Fix database path issue"""
    print("🔍 Fixing database path issue...")
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if backend database exists
    backend_db = "backend/auto_applyer.db"
    current_db = "auto_applyer.db"
    
    if os.path.exists(backend_db):
        print(f"✅ Backend database exists: {backend_db}")
        
        # Copy backend database to current directory
        if os.path.exists(current_db):
            print(f"⚠️  Current database exists, backing up...")
            backup_db = "auto_applyer.db.backup"
            shutil.copy2(current_db, backup_db)
            print(f"✅ Backed up to: {backup_db}")
        
        # Copy backend database to current directory
        shutil.copy2(backend_db, current_db)
        print(f"✅ Copied backend database to current directory")
        
        # Verify the copy
        if os.path.exists(current_db):
            print(f"✅ Current database now exists: {current_db}")
            
            # Check if user exists in the copied database
            import sqlite3
            conn = sqlite3.connect(current_db)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email FROM users WHERE username = ?", ("error_test_user",))
            user = cursor.fetchone()
            if user:
                print(f"✅ User found in copied database: {user}")
            else:
                print("❌ User not found in copied database")
            conn.close()
        else:
            print("❌ Failed to copy database")
    else:
        print(f"❌ Backend database not found: {backend_db}")

if __name__ == "__main__":
    fix_db_path() 