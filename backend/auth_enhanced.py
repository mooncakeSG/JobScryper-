"""
Enhanced Authentication Module for Auto Applyer
Supports 2FA, social login, email verification, and multiple signup methods
"""

import os
import secrets
import pyotp
import qrcode
import bcrypt
import hashlib
import jwt
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import base64
from io import BytesIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import json

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "demo_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30

# 2FA Configuration
TOTP_ISSUER = "Auto Applyer"
TOTP_DIGITS = 6
TOTP_PERIOD = 30

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Social Login Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

class EnhancedAuth:
    """Enhanced authentication with 2FA, social login, and security features"""
    
    def __init__(self):
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt for better security"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            # Fallback to SHA-256 for existing users
            return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    def create_tokens(self, user_id: int, username: str) -> Dict[str, str]:
        """Create access and refresh tokens"""
        access_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = jwt.encode(
            {"sub": username, "user_id": user_id, "exp": access_expires},
            SECRET_KEY, algorithm=ALGORITHM
        )
        
        refresh_token = jwt.encode(
            {"sub": username, "user_id": user_id, "exp": refresh_expires, "type": "refresh"},
            SECRET_KEY, algorithm=ALGORITHM
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def generate_2fa_secret(self) -> str:
        """Generate a new TOTP secret for 2FA"""
        return pyotp.random_base32()
    
    def generate_2fa_qr(self, username: str, secret: str) -> str:
        """Generate QR code for 2FA setup"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=username,
            issuer_name=TOTP_ISSUER
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_2fa_code(self, secret: str, code: str) -> bool:
        """Verify 2FA TOTP code"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code)
        except:
            return False
    
    def generate_verification_code(self) -> str:
        """Generate email verification code"""
        return str(secrets.randbelow(1000000)).zfill(6)
    
    def send_verification_email(self, email: str, code: str, username: str) -> bool:
        """Send email verification code"""
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("⚠️  SMTP not configured, skipping email verification")
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USERNAME
            msg['To'] = email
            msg['Subject'] = "Auto Applyer - Email Verification"
            
            body = f"""
            <html>
            <body>
                <h2>Welcome to Auto Applyer!</h2>
                <p>Hi {username},</p>
                <p>Please verify your email address by entering this code:</p>
                <h1 style="color: #007bff; font-size: 32px; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;">{code}</h1>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't create an account, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Auto Applyer Team</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token and return user info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    user_info = response.json()
                    return {
                        "email": user_info.get("email"),
                        "name": user_info.get("name"),
                        "picture": user_info.get("picture"),
                        "provider": "google"
                    }
        except Exception as e:
            print(f"❌ Google token verification failed: {e}")
        return None
    
    async def verify_github_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify GitHub OAuth token and return user info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                if response.status_code == 200:
                    user_info = response.json()
                    return {
                        "email": user_info.get("email"),
                        "name": user_info.get("name") or user_info.get("login"),
                        "picture": user_info.get("avatar_url"),
                        "provider": "github"
                    }
        except Exception as e:
            print(f"❌ GitHub token verification failed: {e}")
        return None
    
    def get_current_user(self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login"))):
        """Get current user from token"""
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if username is None or user_id is None:
                raise credentials_exception
            
            return {"id": user_id, "username": username}
        except JWTError:
            raise credentials_exception

# Global auth instance
auth = EnhancedAuth() 