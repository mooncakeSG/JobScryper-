#!/usr/bin/env python3
"""
Test password verification logic directly
"""

import sys
sys.path.append('backend')
from main import hash_password
import hashlib

def test_password_verification():
    """Test password verification logic directly"""
    print("🔍 Testing password verification logic...")
    
    password = "error_test_pass"
    stored_hash = "f9477ccd7c792e44aa165b13d0d40cf25644c55c260ec5a5bedd3d9a652e0e26"
    
    # Test the hash_password function
    test_hash = hash_password(password)
    print(f"hash_password result: {test_hash}")
    print(f"Stored hash: {stored_hash}")
    print(f"Hashes match: {test_hash == stored_hash}")
    
    # Test direct hashlib
    direct_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"Direct hashlib result: {direct_hash}")
    print(f"Direct hash matches: {direct_hash == stored_hash}")
    
    # Test the login verification logic
    try:
        import bcrypt
        print("\nTesting bcrypt fallback logic...")
        
        # Simulate the login verification logic
        password_valid = False
        try:
            # Check if the stored hash looks like bcrypt
            if stored_hash.startswith('$2b$'):
                password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
                print("Using bcrypt verification")
            else:
                # It's SHA-256, compare directly
                password_valid = hash_password(password) == stored_hash
                print("Using SHA-256 verification")
        except Exception as e:
            # Fallback to SHA-256 for existing users
            password_valid = hash_password(password) == stored_hash
            print(f"Fallback to SHA-256 due to error: {e}")
        
        print(f"Password verification result: {password_valid}")
        
    except ImportError:
        print("bcrypt not available, using SHA-256 only")
        password_valid = hash_password(password) == stored_hash
        print(f"Password verification result: {password_valid}")

if __name__ == "__main__":
    test_password_verification() 