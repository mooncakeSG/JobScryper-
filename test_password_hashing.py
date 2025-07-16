#!/usr/bin/env python3
"""
Test password hashing to debug login issues
"""

import hashlib
import bcrypt

def test_password_hashing():
    """Test different password hashing methods"""
    password = "testpass123"
    
    print("🔍 Testing password hashing methods...")
    
    # Test SHA-256 hashing
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"SHA-256 hash: {sha256_hash}")
    
    # Test bcrypt hashing
    try:
        bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"bcrypt hash: {bcrypt_hash}")
        
        # Test bcrypt verification
        is_valid = bcrypt.checkpw(password.encode('utf-8'), bcrypt_hash.encode('utf-8'))
        print(f"bcrypt verification: {is_valid}")
        
        # Test SHA-256 verification
        sha256_check = hashlib.sha256(password.encode()).hexdigest() == sha256_hash
        print(f"SHA-256 verification: {sha256_check}")
        
    except ImportError:
        print("❌ bcrypt not available")
    
    # Test the hash_password function from main.py
    try:
        import sys
        sys.path.append('backend')
        from main import hash_password
        
        main_hash = hash_password(password)
        print(f"main.py hash_password: {main_hash}")
        print(f"main.py verification: {hash_password(password) == main_hash}")
        
    except Exception as e:
        print(f"❌ Error importing main.py: {e}")

if __name__ == "__main__":
    test_password_hashing() 