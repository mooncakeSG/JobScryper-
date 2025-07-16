"""
Authentication Endpoints for FastAPI
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
import traceback
from datetime import datetime, timedelta

from auth_system import (
    auth_service, UserRegistration, UserLogin, PasswordResetRequest, 
    PasswordReset, EmailVerification, RefreshToken
)
from db import cloud_db_connection, fetch_user_by_username_or_email, create_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = auth_service.verify_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception
    
    username = payload.get("sub")
    if not username:
        raise credentials_exception
    
    user = fetch_user_by_username_or_email(username)
    if not user:
        raise credentials_exception
    
    return {"id": user[0], "username": user[1], "email": user[2]}

@router.post("/register")
async def register(user_data: UserRegistration):
    """User registration endpoint"""
    try:
        # Check if user already exists
        existing_user = fetch_user_by_username_or_email(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        existing_email = fetch_user_by_username_or_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = auth_service.hash_password(user_data.password)
        
        # Create user
        user_id = create_user(user_data.username, user_data.email, hashed_password)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create tokens
        access_token = auth_service.create_access_token(data={"sub": user_data.username})
        refresh_token = auth_service.create_refresh_token(data={"sub": user_data.username})
        
        # Send welcome email
        auth_service.send_welcome_email(user_data.email, user_data.username)
        
        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login")
async def login(user_data: UserLogin):
    """User login endpoint"""
    try:
        # Find user
        user = fetch_user_by_username_or_email(user_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        user_id, username, password_hash, email, is_active, is_verified = user[:6]
        
        # Verify password
        if not auth_service.verify_password(user_data.password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Check if user is active
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Create tokens
        access_token = auth_service.create_access_token(data={"sub": username})
        refresh_token = auth_service.create_refresh_token(data={"sub": username})
        
        # Update last login
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = datetime('now') WHERE id = ?",
                (user_id,)
            )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user_id,
            "username": username,
            "email": email,
            "is_verified": bool(is_verified)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh")
async def refresh_token(refresh_data: RefreshToken):
    """Refresh access token"""
    try:
        payload = auth_service.verify_token(refresh_data.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token = auth_service.create_access_token(data={"sub": username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Request password reset"""
    try:
        # Find user by email
        user = fetch_user_by_username_or_email(request.email)
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, a password reset link has been sent"}
        
        user_id, username, _, email = user[:4]
        
        # Create reset token
        reset_token = auth_service.create_password_reset_token(user_id)
        
        # Store reset token in database
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
                VALUES (?, ?, datetime('now', '+30 minutes'))
            """, (user_id, reset_token))
        
        # Send reset email
        auth_service.send_password_reset_email(email, reset_token, username)
        
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Reset password with token"""
    try:
        # Find valid reset token
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id FROM password_reset_tokens 
                WHERE token_hash = ? AND expires_at > datetime('now') AND used_at IS NULL
            """, (reset_data.token,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )
            
            user_id = result[0]
            
            # Hash new password
            hashed_password = auth_service.hash_password(reset_data.new_password)
            
            # Update password
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            
            # Mark token as used
            cursor.execute(
                "UPDATE password_reset_tokens SET used_at = datetime('now') WHERE token_hash = ?",
                (reset_data.token,)
            )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.post("/verify-email")
async def verify_email(verification_data: EmailVerification):
    """Verify email with token"""
    try:
        # Find valid verification token
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id FROM users 
                WHERE email_verification_code = ? AND email_verification_expires > datetime('now')
            """, (verification_data.token,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired verification token"
                )
            
            user_id = result[0]
            
            # Mark email as verified
            cursor.execute("""
                UPDATE users SET 
                    email_verified = 1, 
                    is_verified = 1,
                    email_verification_code = NULL,
                    email_verification_expires = NULL
                WHERE id = ?
            """, (user_id,))
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@router.post("/resend-verification")
async def resend_verification(request: PasswordResetRequest):
    """Resend email verification"""
    try:
        user = fetch_user_by_username_or_email(request.email)
        if not user:
            return {"message": "If the email exists, a verification link has been sent"}
        
        user_id, username, _, email, is_verified = user[:5]
        
        if is_verified:
            return {"message": "Email is already verified"}
        
        # Create new verification token
        verification_token = auth_service.create_email_verification_token(user_id)
        
        # Update verification token in database
        with cloud_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET 
                    email_verification_code = ?,
                    email_verification_expires = datetime('now', '+60 minutes')
                WHERE id = ?
            """, (verification_token, user_id))
        
        # Send verification email
        auth_service.send_email_verification(email, verification_token, username)
        
        return {"message": "If the email exists, a verification link has been sent"}
        
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (invalidate refresh token)"""
    # In a real implementation, you might want to blacklist the refresh token
    # For now, we'll just return success
    return {"message": "Logged out successfully"} 