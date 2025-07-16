#!/usr/bin/env python3
"""
Check database schema
"""

import sqlite3
import sys
from pathlib import Path

def check_database():
    """Check database schema"""
    db_path = Path('data/auto_applyer.db')
    
    if not db_path.exists():
        print("❌ Database file not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("📋 Database tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n" + "=" * 50)
        
        # Check users table schema
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        print("👥 Users table schema:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
        
        print("\n" + "=" * 50)
        
        # Check users table data
        cursor.execute("SELECT COUNT(*) FROM users;")
        count = cursor.fetchone()[0]
        print(f"👥 Users count: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, username, email, password_hash FROM users LIMIT 3;")
            users = cursor.fetchall()
            print("👥 Sample users:")
            for user in users:
                print(f"   - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Password: {'***' if user[3] else 'None'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database() 