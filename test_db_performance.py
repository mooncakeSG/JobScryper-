#!/usr/bin/env python3
"""
Database performance test script
"""

import time
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db import cloud_db_connection, fetch_user_by_username_or_email

def test_db_performance():
    print("🔍 Testing database performance...")
    
    # Test 1: Basic connection
    print("\n1️⃣  Testing basic connection...")
    start_time = time.time()
    try:
        with cloud_db_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        connection_time = time.time() - start_time
        print(f"✅ Connection test: {connection_time:.3f}s")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Test 2: User fetch
    print("\n2️⃣  Testing user fetch...")
    start_time = time.time()
    try:
        user = fetch_user_by_username_or_email("demo")
        fetch_time = time.time() - start_time
        print(f"✅ User fetch: {fetch_time:.3f}s")
        if user:
            print(f"   Found user: {user[1]}")
    except Exception as e:
        print(f"❌ User fetch failed: {e}")
    
    # Test 3: Multiple queries
    print("\n3️⃣  Testing multiple queries...")
    start_time = time.time()
    try:
        with cloud_db_connection() as conn:
            # Test 1: Simple select
            conn.execute("SELECT COUNT(*) FROM users").fetchone()
            
            # Test 2: User lookup
            conn.execute("SELECT id, username FROM users WHERE username = ?", ("demo",)).fetchone()
            
            # Test 3: Check activities table
            conn.execute("SELECT COUNT(*) FROM activities").fetchone()
        
        multi_time = time.time() - start_time
        print(f"✅ Multiple queries: {multi_time:.3f}s")
    except Exception as e:
        print(f"❌ Multiple queries failed: {e}")
    
    # Test 4: Simulate auth endpoint
    print("\n4️⃣  Testing auth endpoint simulation...")
    start_time = time.time()
    try:
        # Simulate what get_current_user does
        user = fetch_user_by_username_or_email("demo")
        if user:
            auth_time = time.time() - start_time
            print(f"✅ Auth simulation: {auth_time:.3f}s")
        else:
            print("❌ Auth simulation failed: user not found")
    except Exception as e:
        print(f"❌ Auth simulation failed: {e}")
    
    print("\n🎉 Performance test completed!")
    print("\n📊 Summary:")
    print("   - If any test takes > 5 seconds, there's a performance issue")
    print("   - The auth endpoint should complete in < 1 second")
    print("   - Connection pooling should improve subsequent requests")

if __name__ == "__main__":
    test_db_performance() 