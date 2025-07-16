"""
Complete Authentication System for FastAPI Backend
"""
import os
import bcrypt
import jwt
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, validator
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_EXPIRE_MINUTES = 30
EMAIL_VERIFICATION_EXPIRE_MINUTES = 60

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@yourapp.com")

# Pydantic Models for Validation
class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class EmailVerification(BaseModel):
    token: str

class RefreshToken(BaseModel):
    refresh_token: str

class AuthService:
    """Complete authentication service"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError:
            logger.warning("Invalid token")
            return None
    
    def create_password_reset_token(self, user_id: int) -> str:
        """Create password reset token"""
        return secrets.token_urlsafe(32)
    
    def create_email_verification_token(self, user_id: int) -> str:
        """Create email verification token"""
        return secrets.token_urlsafe(32)
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SMTP"""
        try:
            if not SMTP_USERNAME or not SMTP_PASSWORD:
                logger.warning("SMTP credentials not configured, skipping email send")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = FROM_EMAIL
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_password_reset_email(self, email: str, token: str, username: str) -> bool:
        """Send password reset email"""
        reset_url = f"http://localhost:3000/reset-password?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello {username},</p>
            <p>You requested a password reset for your account.</p>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Reset Password
            </a>
            <p>This link will expire in {PASSWORD_RESET_EXPIRE_MINUTES} minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """
        
        return self.send_email(email, "Password Reset Request", html_content)
    
    def send_email_verification(self, email: str, token: str, username: str) -> bool:
        """Send email verification"""
        verify_url = f"http://localhost:3000/verify-email?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Email Verification</h2>
            <p>Hello {username},</p>
            <p>Please verify your email address by clicking the link below:</p>
            <a href="{verify_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Verify Email
            </a>
            <p>This link will expire in {EMAIL_VERIFICATION_EXPIRE_MINUTES} minutes.</p>
        </body>
        </html>
        """
        
        return self.send_email(email, "Email Verification", html_content)
    
    def send_welcome_email(self, email: str, username: str) -> bool:
        """Send welcome email"""
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to JobScryper!</h2>
            <p>Hello {username},</p>
            <p>Thank you for registering with JobScryper. Your account has been created successfully!</p>
            <p>You can now:</p>
            <ul>
                <li>Upload your resume for ATS optimization</li>
                <li>Search for jobs with AI-powered matching</li>
                <li>Track your applications</li>
                <li>Get personalized job recommendations</li>
            </ul>
            <p>Start your job search journey today!</p>
        </body>
        </html>
        """
        
        return self.send_email(email, "Welcome to JobScryper!", html_content)

# Global auth service instance
auth_service = AuthService() 