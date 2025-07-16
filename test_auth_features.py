#!/usr/bin/env python3
"""
Test script for enhanced authentication features
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import pyotp
        print("✅ pyotp imported successfully")
    except ImportError as e:
        print(f"❌ pyotp import failed: {e}")
        return False
    
    try:
        import qrcode
        print("✅ qrcode imported successfully")
    except ImportError as e:
        print(f"❌ qrcode import failed: {e}")
        return False
    
    try:
        import bcrypt
        print("✅ bcrypt imported successfully")
    except ImportError as e:
        print(f"❌ bcrypt import failed: {e}")
        return False
    
    try:
        import passlib
        print("✅ passlib imported successfully")
    except ImportError as e:
        print(f"❌ passlib import failed: {e}")
        return False
    
    try:
        import authlib
        print("✅ authlib imported successfully")
    except ImportError as e:
        print(f"❌ authlib import failed: {e}")
        return False
    
    try:
        import httpx
        print("✅ httpx imported successfully")
    except ImportError as e:
        print(f"❌ httpx import failed: {e}")
        return False
    
    return True

def test_2fa_features():
    """Test 2FA functionality"""
    print("\n🔐 Testing 2FA features...")
    
    try:
        import pyotp
        
        # Test secret generation
        secret = pyotp.random_base32()
        print(f"✅ 2FA secret generated: {secret[:10]}...")
        
        # Test TOTP generation
        totp = pyotp.TOTP(secret)
        code = totp.now()
        print(f"✅ TOTP code generated: {code}")
        
        # Test verification
        is_valid = totp.verify(code)
        print(f"✅ TOTP verification: {is_valid}")
        
        return True
    except Exception as e:
        print(f"❌ 2FA test failed: {e}")
        return False

def test_password_hashing():
    """Test password hashing functionality"""
    print("\n🔑 Testing password hashing...")
    
    try:
        import bcrypt
        
        # Test password hashing
        password = "test_password_123"
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        print(f"✅ Password hashed: {hashed[:20].decode()}...")
        
        # Test password verification
        is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed)
        print(f"✅ Password verification: {is_valid}")
        
        return True
    except Exception as e:
        print(f"❌ Password hashing test failed: {e}")
        return False

def test_qr_code_generation():
    """Test QR code generation"""
    print("\n📱 Testing QR code generation...")
    
    try:
        import qrcode
        
        # Test QR code creation
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("otpauth://totp/AutoApplyer:testuser?secret=JBSWY3DPEHPK3PXP&issuer=AutoApplyer")
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        print("✅ QR code generated successfully")
        
        return True
    except Exception as e:
        print(f"❌ QR code test failed: {e}")
        return False

def test_enhanced_auth_module():
    """Test the enhanced auth module"""
    print("\n🚀 Testing enhanced auth module...")
    
    try:
        from backend.auth_enhanced import auth
        
        # Test 2FA secret generation
        secret = auth.generate_2fa_secret()
        print(f"✅ Enhanced auth 2FA secret: {secret[:10]}...")
        
        # Test verification code generation
        code = auth.generate_verification_code()
        print(f"✅ Verification code: {code}")
        
        # Test password hashing
        password = "test_password"
        hashed = auth.hash_password(password)
        print(f"✅ Enhanced auth password hash: {hashed[:20]}...")
        
        # Test password verification
        is_valid = auth.verify_password(password, hashed)
        print(f"✅ Enhanced auth password verification: {is_valid}")
        
        return True
    except Exception as e:
        print(f"❌ Enhanced auth module test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Authentication Features")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_2fa_features,
        test_password_hashing,
        test_qr_code_generation,
        test_enhanced_auth_module
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication features are working correctly!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 