from fastapi import FastAPI, File, UploadFile, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from typing import List, Dict, Any
import json
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib
import secrets
import traceback
import time

# Add the parent directory to the Python path to import existing modules
sys.path.append(str(Path(__file__).parent.parent))

# Import critical database functions first (these must always be available)
from db import fetch_user_by_username_or_email, cloud_db_connection

# Import existing modules
try:
    from resume_parser import ResumeParser
    from jobspy_wrapper import JobSpyWrapper
    from alternative_sources import AlternativeJobAggregator
    from matcher import JobResumeMatcher
    from database.utilities import DatabaseUtils
    from database.models import User, JobApplication, ApplicationStatus
    from database import fetchall, fetchone, execute
    from groq_resume_suggestion import get_groq_match_score_and_explanation
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    print("Some features may not work properly.")

# Import enhanced authentication
try:
    from auth_enhanced import auth, EnhancedAuth
except ImportError as e:
    print(f"Warning: Enhanced auth not available: {e}")
    auth = None

app = FastAPI(
    title="JobScryper API",
    description="AI-powered job application platform API",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
resume_parser = None
job_spy_wrapper = None
job_aggregator = None
job_matcher = None

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "demo_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Use optimized user fetch function
        user = fetch_user_by_username_or_email(username)
        if not user:
            raise credentials_exception
        
        return {"id": user[0], "username": user[1]}
    except JWTError:
        raise credentials_exception
    except Exception as e:
        print(f"❌ get_current_user error: {e}")
        raise credentials_exception

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global resume_parser, job_spy_wrapper, job_aggregator, job_matcher
    
    # Initialize database (optional - don't fail if it doesn't work)
    try:
        from database.migrations import MigrationManager
        mm = MigrationManager()
        mm.migrate_to_latest()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database migration failed (continuing anyway): {e}")
    
    # Initialize core services (these are more critical)
    try:
        resume_parser = ResumeParser()
        print("✅ Resume parser initialized successfully")
    except Exception as e:
        print(f"❌ Resume parser failed to initialize: {e}")
        resume_parser = None
    
    try:
        job_spy_wrapper = JobSpyWrapper()
        print("✅ Job spy wrapper initialized successfully")
    except Exception as e:
        print(f"❌ Job spy wrapper failed to initialize: {e}")
        job_spy_wrapper = None
    
    try:
        job_aggregator = AlternativeJobAggregator()
        print("✅ Job aggregator initialized successfully")
    except Exception as e:
        print(f"❌ Job aggregator failed to initialize: {e}")
        job_aggregator = None
    
    try:
        job_matcher = JobResumeMatcher()
        print("✅ Job matcher initialized successfully")
    except Exception as e:
        print(f"❌ Job matcher failed to initialize: {e}")
        job_matcher = None
    
    print("✅ Startup complete")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "JobScryper API is running!", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": {
        "resume_parser": resume_parser is not None,
        "job_spy_wrapper": job_spy_wrapper is not None,
        "job_aggregator": job_aggregator is not None,
        "job_matcher": job_matcher is not None
    }}

@app.post("/api/resume")
async def analyze_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Analyze uploaded resume for ATS optimization and store resume text for user"""
    if not resume_parser:
        raise HTTPException(status_code=503, detail="Resume parser not available")
    
    # Validate file type
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    temp_path = f"temp_{file.filename}"
    try:
        # Save the uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse the resume
        resume_data = resume_parser.parse_resume(temp_path)
        sections = resume_data.get("sections", {})
        skills = [s.strip() for s in sections.get("skills", "").split(",") if s.strip()]
        tech_skills = [s.strip() for s in sections.get("technical_skills", "").split(",") if s.strip()]
        experience = sections.get("experience", "")
        education = sections.get("education", "")
        summary = sections.get("summary", "")
        
        # Store resume text in users table
        resume_text = resume_data.get("text", "") or "\n".join([experience, education, summary])
        with cloud_db_connection() as conn:
            conn.execute("UPDATE users SET resume_text = ? WHERE id = ?", (resume_text, current_user["id"]))
            conn.commit()
        
        # Dynamic ATS score calculation
        ats_score = 50
        if skills:
            ats_score += min(20, len(skills) * 2)
        if tech_skills:
            ats_score += min(15, len(tech_skills) * 2)
        if experience:
            ats_score += 7
        if education:
            ats_score += 5
        if summary:
            ats_score += 3
        ats_score = min(100, ats_score)
        
        # Improved Strengths
        strengths = []
        # Technical skills: at least 3 unique skills
        if tech_skills and len(set(tech_skills)) >= 3:
            strengths.append("Strong technical skills section")
        # Experience: at least 2 job entries or >100 characters
        if experience and (len([line for line in experience.split('\n') if line.strip()]) >= 2 or len(experience) > 100):
            strengths.append("Clear work experience progression")
        # Education: look for degree keywords
        degree_keywords = ["bachelor", "master", "phd", "associate", "degree", "diploma", "certification", "certified"]
        if education and any(degree in education.lower() for degree in degree_keywords):
            strengths.append("Education section present")
        # Summary: at least 20 words
        if summary and len(summary.split()) >= 20:
            strengths.append("Professional summary included")
        # Skills: at least 5 skills
        if skills and len(skills) >= 5:
            strengths.append("Skills section present")
        
        # Suggestions
        suggestions = []
        if not tech_skills:
            suggestions.append("Add more technical keywords relevant to your field")
        if not experience:
            suggestions.append("Include quantifiable achievements in your experience")
        if not education:
            suggestions.append("Add an education section")
        if not summary:
            suggestions.append("Add a professional summary at the top of your resume")
        if ats_score < 80:
            suggestions.append("Optimize for ATS scanning by using more keywords")
        # Always show at least one suggestion
        if not suggestions:
            suggestions.append("Your resume is strong! Consider tailoring it for each job application for best results.")
        
        # Improvements
        improvements = []
        if ats_score < 90:
            improvements.append("Add more action verbs and measurable results")
        if len(skills) < 5:
            improvements.append("List at least 5 relevant skills")
        
        # Keywords
        keywords = list(set(skills + tech_skills))
        
        analysis = {
            "ats_score": ats_score,
            "suggestions": suggestions,
            "strengths": strengths,
            "keywords": keywords,
            "improvements": improvements,
            "sections": {
                "skills": skills,
                "technical_skills": tech_skills,
                "experience": experience,
                "education": education,
                "summary": summary
            }
        }
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/auth/signup")
async def signup(user_data: dict = Body(...)):
    """Enhanced signup with email verification"""
    username = user_data.get("username")
    password = user_data.get("password")
    email = user_data.get("email", "")
    signup_method = user_data.get("method", "email")  # email, google, github

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    if not email:
        email = f"{username}@example.com"

    try:
        with cloud_db_connection() as conn:
            # Check if username exists
            existing_user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already registered")

            # Check if email exists
            existing_email = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing_email:
                raise HTTPException(status_code=400, detail="Email already registered")

            # Hash password using enhanced auth
            if auth:
                hashed_password = auth.hash_password(password)
            else:
                hashed_password = hash_password(password)

            # Generate verification code for email signup
            verification_code = None
            verification_expires = None
            if signup_method == "email" and auth:
                verification_code = auth.generate_verification_code()
                verification_expires = datetime.utcnow() + timedelta(minutes=10)

            # Create user
            conn.execute(
                """
                INSERT INTO users (
                    username, password_hash, email, is_active, is_verified, 
                    email_verified, email_verification_code, email_verification_expires,
                    social_provider, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (username, hashed_password, email, True, False, 
                 signup_method != "email", verification_code, verification_expires,
                 signup_method if signup_method != "email" else None)
            )
            conn.commit()

            # Send verification email if using email signup
            if signup_method == "email" and auth and verification_code:
                auth.send_verification_email(email, verification_code, username)

        return {
            "message": "User registered successfully",
            "verification_required": signup_method == "email",
            "method": signup_method
        }
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/auth/login")
async def login(user_data: dict = Body(...)):
    """Enhanced login with 2FA support"""
    try:
        username = user_data.get("username")
        password = user_data.get("password")
        two_fa_code = user_data.get("two_fa_code")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")

        user = fetch_user_by_username_or_email(username)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        user_id, db_username, db_password_hash = user
        
        # Verify password
        if auth:
            password_valid = auth.verify_password(password, db_password_hash)
        else:
            password_valid = hash_password(password) == db_password_hash
            
        if not password_valid:
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        # Check if 2FA is enabled
        with cloud_db_connection() as conn:
            two_fa_enabled = conn.execute(
                "SELECT two_fa_enabled, two_fa_secret FROM users WHERE id = ?", 
                (user_id,)
            ).fetchone()
            
            if two_fa_enabled and two_fa_enabled[0]:
                if not two_fa_code:
                    raise HTTPException(
                        status_code=400, 
                        detail="2FA code required",
                        headers={"X-2FA-Required": "true"}
                    )
                
                if not auth.verify_2fa_code(two_fa_enabled[1], two_fa_code):
                    raise HTTPException(status_code=401, detail="Invalid 2FA code")

        # Create tokens
        if auth:
            tokens = auth.create_tokens(user_id, db_username)
        else:
            access_token = create_access_token(data={"sub": db_username})
            tokens = {"access_token": access_token, "token_type": "bearer"}

        # Update last login
        with cloud_db_connection() as conn:
            conn.execute(
                "UPDATE users SET last_login = datetime('now'), failed_login_attempts = 0 WHERE id = ?",
                (user_id,)
            )
            conn.commit()

        return {**tokens, "user_id": user_id}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/social-login")
async def social_login(login_data: dict = Body(...)):
    """Social login with Google or GitHub"""
    try:
        provider = login_data.get("provider")  # google, github
        token = login_data.get("token")
        
        if not provider or not token:
            raise HTTPException(status_code=400, detail="Provider and token are required")

        # Verify token with provider
        user_info = None
        if provider == "google" and auth:
            user_info = await auth.verify_google_token(token)
        elif provider == "github" and auth:
            user_info = await auth.verify_github_token(token)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid social token")

        email = user_info["email"]
        name = user_info["name"]
        
        with cloud_db_connection() as conn:
            # Check if user exists
            existing_user = conn.execute(
                "SELECT id, username FROM users WHERE email = ? OR (social_provider = ? AND social_id = ?)",
                (email, provider, email)
            ).fetchone()
            
            if existing_user:
                # User exists, log them in
                user_id, username = existing_user
                tokens = auth.create_tokens(user_id, username) if auth else {"access_token": "demo_token"}
                
                # Update last login
                conn.execute(
                    "UPDATE users SET last_login = datetime('now') WHERE id = ?",
                    (user_id,)
                )
                conn.commit()
                
                return {**tokens, "user_id": user_id, "is_new_user": False}
            else:
                # Create new user
                username = f"{provider}_{email.split('@')[0]}"
                hashed_password = auth.hash_password(secrets.token_urlsafe(32)) if auth else "demo_hash"
                
                conn.execute(
                    """
                    INSERT INTO users (
                        username, password_hash, email, is_active, is_verified,
                        email_verified, social_provider, social_id, profile_picture,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    """,
                    (username, hashed_password, email, True, True, True, 
                     provider, email, user_info.get("picture"))
                )
                conn.commit()
                
                user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                tokens = auth.create_tokens(user_id, username) if auth else {"access_token": "demo_token"}
                
                return {**tokens, "user_id": user_id, "is_new_user": True}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Social login error: {e}")
        raise HTTPException(status_code=500, detail="Social login failed")

@app.post("/api/auth/verify-email")
async def verify_email(verification_data: dict = Body(...)):
    """Verify email with code"""
    try:
        email = verification_data.get("email")
        code = verification_data.get("code")
        
        if not email or not code:
            raise HTTPException(status_code=400, detail="Email and verification code are required")

        with cloud_db_connection() as conn:
            user = conn.execute(
                "SELECT id, email_verification_code, email_verification_expires FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_id, stored_code, expires = user
            
            if not stored_code:
                raise HTTPException(status_code=400, detail="No verification code found")
            
            if datetime.fromisoformat(expires) < datetime.utcnow():
                raise HTTPException(status_code=400, detail="Verification code expired")
            
            if stored_code != code:
                raise HTTPException(status_code=400, detail="Invalid verification code")
            
            # Mark email as verified
            conn.execute(
                "UPDATE users SET email_verified = TRUE, email_verification_code = NULL, email_verification_expires = NULL WHERE id = ?",
                (user_id,)
            )
            conn.commit()
            
            return {"message": "Email verified successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Email verification error: {e}")
        raise HTTPException(status_code=500, detail="Email verification failed")

@app.post("/api/auth/resend-verification")
async def resend_verification(resend_data: dict = Body(...)):
    """Resend email verification code"""
    try:
        email = resend_data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        with cloud_db_connection() as conn:
            user = conn.execute(
                "SELECT id, username, email_verified FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_id, username, email_verified = user
            
            if email_verified:
                raise HTTPException(status_code=400, detail="Email already verified")
            
            # Generate new verification code
            if auth:
                verification_code = auth.generate_verification_code()
                verification_expires = datetime.utcnow() + timedelta(minutes=10)
                
                conn.execute(
                    "UPDATE users SET email_verification_code = ?, email_verification_expires = ? WHERE id = ?",
                    (verification_code, verification_expires, user_id)
                )
                conn.commit()
                
                # Send verification email
                auth.send_verification_email(email, verification_code, username)
                
                return {"message": "Verification code sent successfully"}
            else:
                raise HTTPException(status_code=503, detail="Email service not available")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Resend verification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend verification")

@app.post("/api/auth/setup-2fa")
async def setup_2fa(current_user: dict = Depends(get_current_user)):
    """Setup 2FA for user"""
    try:
        if not auth:
            raise HTTPException(status_code=503, detail="2FA service not available")

        # Generate new 2FA secret
        secret = auth.generate_2fa_secret()
        qr_code = auth.generate_2fa_qr(current_user["username"], secret)
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(8)]
        
        with cloud_db_connection() as conn:
            conn.execute(
                "UPDATE users SET two_fa_secret = ?, backup_codes = ? WHERE id = ?",
                (secret, json.dumps(backup_codes), current_user["id"])
            )
            conn.commit()
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"2FA setup error: {e}")
        raise HTTPException(status_code=500, detail="2FA setup failed")

@app.post("/api/auth/enable-2fa")
async def enable_2fa(enable_data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Enable 2FA after verification"""
    try:
        code = enable_data.get("code")
        
        if not code:
            raise HTTPException(status_code=400, detail="2FA code is required")

        with cloud_db_connection() as conn:
            user = conn.execute(
                "SELECT two_fa_secret FROM users WHERE id = ?",
                (current_user["id"],)
            ).fetchone()
            
            if not user or not user[0]:
                raise HTTPException(status_code=400, detail="2FA not set up")
            
            secret = user[0]
            
            if not auth.verify_2fa_code(secret, code):
                raise HTTPException(status_code=400, detail="Invalid 2FA code")
            
            # Enable 2FA
            conn.execute(
                "UPDATE users SET two_fa_enabled = TRUE WHERE id = ?",
                (current_user["id"],)
            )
            conn.commit()
            
            return {"message": "2FA enabled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"2FA enable error: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable 2FA")

@app.post("/api/auth/disable-2fa")
async def disable_2fa(disable_data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Disable 2FA"""
    try:
        code = disable_data.get("code")
        
        if not code:
            raise HTTPException(status_code=400, detail="2FA code is required")

        with cloud_db_connection() as conn:
            user = conn.execute(
                "SELECT two_fa_secret FROM users WHERE id = ?",
                (current_user["id"],)
            ).fetchone()
            
            if not user or not user[0]:
                raise HTTPException(status_code=400, detail="2FA not enabled")
            
            secret = user[0]
            
            if not auth.verify_2fa_code(secret, code):
                raise HTTPException(status_code=400, detail="Invalid 2FA code")
            
            # Disable 2FA
            conn.execute(
                "UPDATE users SET two_fa_enabled = FALSE, two_fa_secret = NULL, backup_codes = NULL WHERE id = ?",
                (current_user["id"],)
            )
            conn.commit()
            
            return {"message": "2FA disabled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"2FA disable error: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable 2FA")

@app.post("/api/auth/refresh-token")
async def refresh_token(refresh_data: dict = Body(...)):
    """Refresh access token using refresh token"""
    try:
        refresh_token = refresh_data.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")

        # Verify refresh token
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            user_id = payload.get("user_id")
            token_type = payload.get("type")
            
            if not username or not user_id or token_type != "refresh":
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Create new access token
            if auth:
                tokens = auth.create_tokens(user_id, username)
            else:
                access_token = create_access_token(data={"sub": username})
                tokens = {"access_token": access_token, "token_type": "bearer"}
            
            return tokens

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.post("/api/auth/forgot-password")
async def forgot_password(forgot_data: dict = Body(...)):
    """Send password reset email"""
    try:
        email = forgot_data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        with cloud_db_connection() as conn:
            user = conn.execute(
                "SELECT id, username FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            
            if not user:
                # Don't reveal if email exists
                return {"message": "If the email exists, a reset link has been sent"}
            
            user_id, username = user
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(hours=1)
            
            # Store reset token
            conn.execute(
                "INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) VALUES (?, ?, ?)",
                (user_id, hashlib.sha256(reset_token.encode()).hexdigest(), expires)
            )
            conn.commit()
            
            # Send reset email (simplified for demo)
            if auth and SMTP_USERNAME and SMTP_PASSWORD:
                reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
                auth.send_verification_email(email, f"Reset your password: {reset_url}", username)
            
            return {"message": "If the email exists, a reset link has been sent"}

    except Exception as e:
        print(f"Forgot password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process request")

@app.post("/api/auth/reset-password")
async def reset_password(reset_data: dict = Body(...)):
    """Reset password using token"""
    try:
        token = reset_data.get("token")
        new_password = reset_data.get("new_password")
        
        if not token or not new_password:
            raise HTTPException(status_code=400, detail="Token and new password are required")

        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        with cloud_db_connection() as conn:
            reset_record = conn.execute(
                "SELECT user_id, expires_at, used_at FROM password_reset_tokens WHERE token_hash = ?",
                (token_hash,)
            ).fetchone()
            
            if not reset_record:
                raise HTTPException(status_code=400, detail="Invalid reset token")
            
            user_id, expires, used_at = reset_record
            
            if used_at:
                raise HTTPException(status_code=400, detail="Reset token already used")
            
            if datetime.fromisoformat(expires) < datetime.utcnow():
                raise HTTPException(status_code=400, detail="Reset token expired")
            
            # Update password
            if auth:
                hashed_password = auth.hash_password(new_password)
            else:
                hashed_password = hash_password(new_password)
            
            conn.execute(
                "UPDATE users SET password_hash = ?, password_changed_at = datetime('now') WHERE id = ?",
                (hashed_password, user_id)
            )
            
            # Mark token as used
            conn.execute(
                "UPDATE password_reset_tokens SET used_at = datetime('now') WHERE token_hash = ?",
                (token_hash,)
            )
            
            conn.commit()
            
            return {"message": "Password reset successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail="Password reset failed")

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/api/match")
async def search_jobs(
    query: str = "software engineer",
    location: str = "remote",
    job_type: str = "all",
    min_salary: str = "",
    company: str = "",
    max_results: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Search for job matches using the stored resume for the current user"""
    try:
        print("[MATCH] Starting job search for:", query, location)
        # Fetch resume_text from users table
        with cloud_db_connection() as conn:
            row = conn.execute("SELECT resume_text FROM users WHERE id = ?", (current_user["id"],)).fetchone()
            resume_text = row[0] if row else None
        if not resume_text:
            print("[MATCH] No resume uploaded for user", current_user["id"])
            raise HTTPException(status_code=400, detail="No resume uploaded. Please upload your resume first.")
        all_jobs = []
        # Search using JobSpy if available
        if job_spy_wrapper:
            try:
                jobspy_jobs = job_spy_wrapper.search_jobs(
                    job_title=query,
                    location=location,
                    max_results=max_results
                )
                for job in jobspy_jobs:
                    job['source'] = 'JobSpy'
                all_jobs.extend(jobspy_jobs)
            except Exception as e:
                print(f"JobSpy search failed: {e}")
        # Search using Alternative APIs if available
        if job_aggregator:
            try:
                alt_jobs = job_aggregator.search_all_sources(
                    job_title=query,
                    location=location,
                    max_per_source=max_results
                )
                for job in alt_jobs:
                    job['source'] = 'Alternative'
                all_jobs.extend(alt_jobs)
            except Exception as e:
                print(f"Alternative API search failed: {e}")
        # If no results from APIs, return mock data
        if not all_jobs:
            all_jobs = [
                {
                    "id": "1",
                    "title": "Senior Software Engineer",
                    "company": "TechCorp Inc.",
                    "location": "San Francisco, CA",
                    "salary": "$120,000 - $180,000",
                    "description": "Join our team to build scalable web applications using React, Node.js, and cloud technologies.",
                    "datePosted": "2 days ago",
                    "jobType": "Full-time",
                    "source": "JobSpy",
                    "url": "https://example.com/job1"
                },
                {
                    "id": "2",
                    "title": "Frontend Developer",
                    "company": "StartupXYZ",
                    "location": "Remote",
                    "salary": "$80,000 - $120,000",
                    "description": "Remote position for a passionate frontend developer. Experience with React and TypeScript required.",
                    "datePosted": "1 week ago",
                    "jobType": "Full-time",
                    "source": "Indeed",
                    "url": "https://example.com/job2"
                }
            ]
        # For each job, get Groq match score and explanation
        print("[MATCH] Total jobs found:", len(all_jobs))
        jobs = all_jobs[:max_results]
        scored_jobs = []
        print("[MATCH] Starting Groq scoring for up to 5 jobs...")
        for i, job in enumerate(jobs):
            print(f"[MATCH] Scoring job {i+1}/{len(jobs)}: {job.get('title') or job.get('job_title')}")
            if i < 5:
                try:
                    result = get_groq_match_score_and_explanation(resume_text, job)
                    job["matchScore"] = result.get("score")
                    job["matchExplanation"] = result.get("explanation")
                except Exception as e:
                    print(f"[MATCH] Error scoring job {i+1}: {e}")
                    if hasattr(e, 'status_code') and getattr(e, 'status_code', None) == 429:
                        job["matchScore"] = None
                        job["matchExplanation"] = "Rate limit reached. Try again later."
                    else:
                        job["matchScore"] = None
                        job["matchExplanation"] = f"Error: {str(e)}"
                time.sleep(0.5)
            else:
                job["matchScore"] = None
                job["matchExplanation"] = "Not scored due to rate limit."
            scored_jobs.append(job)
        print("[MATCH] Finished scoring. Returning jobs.")
        return {"jobs": scored_jobs}
    except Exception as e:
        print("[MATCH] Exception in /api/match:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/applications")
async def create_application(application_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Create a new job application"""
    try:
        required_fields = ["job_title", "company"]
        for field in required_fields:
            if not application_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        with cloud_db_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO job_applications (
                    user_id, job_title, company, location, status, application_date,
                    salary_min, salary_max, job_url, interview_date, notes, match_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    current_user["id"],
                    application_data.get("job_title"),
                    application_data.get("company"),
                    application_data.get("location", ""),
                    application_data.get("status", "applied"),
                    datetime.now().isoformat(),
                    application_data.get("salary_min"),
                    application_data.get("salary_max"),
                    application_data.get("job_url"),
                    application_data.get("interview_date"),
                    application_data.get("notes"),
                    application_data.get("match_score", 0)
                )
            )
            application_id = cursor.lastrowid
            conn.commit()
            application = conn.execute(
                """
                SELECT id, job_title, company, location, status, application_date,
                       salary_min, salary_max, job_url, interview_date, notes, match_score
                FROM job_applications WHERE id = ?
                """, (application_id,)
            ).fetchone()
        return {
            "message": "Application created successfully",
            "application": {
                "id": application[0],
                "job_title": application[1],
                "company": application[2],
                "location": application[3],
                "status": application[4],
                "application_date": application[5],
                "salary_min": application[6],
                "salary_max": application[7],
                "job_url": application[8],
                "interview_date": application[9],
                "notes": application[10],
                "match_score": application[11]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {str(e)}")

@app.get("/api/applications")
async def get_applications(
    current_user: dict = Depends(get_current_user),
    status: str = None,
    search: str = None,
    page: int = 1,
    limit: int = 20
):
    """Get user's job applications with filtering and pagination"""
    try:
        query = """
            SELECT id, job_title, company, location, status, application_date,
                   salary_min, salary_max, job_url, interview_date, notes, match_score
            FROM job_applications WHERE user_id = ?
        """
        params = [current_user["id"]]
        if status and status != "all":
            query += " AND status = ?"
            params.append(status)
        if search:
            query += " AND (job_title LIKE ? OR company LIKE ? OR location LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        count_query = query.replace(
            "SELECT id, job_title, company, location, status, application_date, salary_min, salary_max, job_url, interview_date, notes, match_score",
            "SELECT COUNT(*)"
        )
        with cloud_db_connection() as conn:
            result = conn.execute(count_query, params).fetchone()
            total_count = result[0] if result is not None else 0
            query += " ORDER BY application_date DESC LIMIT ? OFFSET ?"
            params.extend([limit, (page - 1) * limit])
            applications_data = conn.execute(query, params).fetchall()
        applications = []
        for app in applications_data:
            applications.append({
                "id": app[0],
                "job_title": app[1],
                "company": app[2],
                "location": app[3],
                "status": app[4],
                "application_date": app[5],
                "salary_min": app[6],
                "salary_max": app[7],
                "job_url": app[8],
                "interview_date": app[9],
                "notes": app[10],
                "match_score": app[11]
            })
        return {
            "applications": applications,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch applications: {str(e)}")

@app.patch("/api/applications/{application_id}")
async def update_application(application_id: int, update_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Update an existing job application"""
    try:
        with cloud_db_connection() as conn:
            application = conn.execute(
                """
                SELECT id FROM job_applications 
                WHERE id = ? AND user_id = ?
                """, (application_id, current_user["id"])
            ).fetchone()
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            allowed_fields = ["status", "notes", "interview_date", "salary_min", "salary_max"]
            update_parts = []
            params = []
            for field in allowed_fields:
                if field in update_data:
                    update_parts.append(f"{field} = ?")
                    params.append(update_data[field])
            if not update_parts:
                raise HTTPException(status_code=400, detail="No valid fields to update")
            query = f"UPDATE job_applications SET {', '.join(update_parts)} WHERE id = ? AND user_id = ?"
            params.extend([application_id, current_user["id"]])
            conn.execute(query, params)
            conn.commit()
            updated_app = conn.execute(
                """
                SELECT id, job_title, company, location, status, application_date,
                       salary_min, salary_max, job_url, interview_date, notes, match_score
                FROM job_applications WHERE id = ?
                """, (application_id,)
            ).fetchone()
        return {
            "message": "Application updated successfully",
            "application": {
                "id": updated_app[0],
                "job_title": updated_app[1],
                "company": updated_app[2],
                "location": updated_app[3],
                "status": updated_app[4],
                "application_date": updated_app[5],
                "salary_min": updated_app[6],
                "salary_max": updated_app[7],
                "job_url": updated_app[8],
                "interview_date": updated_app[9],
                "notes": updated_app[10],
                "match_score": updated_app[11]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update application: {str(e)}")

@app.delete("/api/applications/{application_id}")
async def delete_application(application_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a job application"""
    try:
        with cloud_db_connection() as conn:
            application = conn.execute(
                """
                SELECT id FROM job_applications 
                WHERE id = ? AND user_id = ?
                """, (application_id, current_user["id"])
            ).fetchone()
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            conn.execute("DELETE FROM job_applications WHERE id = ? AND user_id = ?", (application_id, current_user["id"]))
            conn.commit()
        return {"message": "Application deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")

@app.get("/api/analytics")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    """Get user's analytics data"""
    try:
        with cloud_db_connection() as conn:
            total_applications = conn.execute(
                "SELECT COUNT(*) FROM job_applications WHERE user_id = ?",
                (current_user["id"],)
            ).fetchone()[0]
            status_counts = conn.execute(
                """
                SELECT status, COUNT(*) as count 
                FROM job_applications 
                WHERE user_id = ? 
                GROUP BY status
                """, (current_user["id"],)
            ).fetchall()
            monthly_data = conn.execute(
                """
                SELECT 
                    strftime('%Y-%m', application_date) as month,
                    COUNT(*) as applications,
                    SUM(CASE WHEN status IN ('interview_scheduled', 'interview_completed') THEN 1 ELSE 0 END) as interviews,
                    SUM(CASE WHEN status = 'offer_received' THEN 1 ELSE 0 END) as offers
                FROM job_applications 
                WHERE user_id = ? 
                AND application_date >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', application_date)
                ORDER BY month DESC
                """, (current_user["id"],)
            ).fetchall()
        interview_count = sum(count for _, count in status_counts if _ in ['interview_scheduled', 'interview_completed'])
        interview_rate = (interview_count / total_applications * 100) if total_applications > 0 else 0
        response_count = sum(count for _, count in status_counts if _ not in ['applied', 'pending'])
        response_rate = (response_count / total_applications * 100) if total_applications > 0 else 0
        monthly_applications = []
        for month, apps, interviews, offers in monthly_data:
            monthly_applications.append({
                "month": month,
                "applications": apps,
                "interviews": interviews,
                "offers": offers
            })
        application_status = []
        for status, count in status_counts:
            application_status.append({
                "name": status.replace('_', ' ').title(),
                "value": count
            })
        analytics = {
            "total_applications": total_applications,
            "interview_rate": round(interview_rate, 1),
            "response_rate": round(response_rate, 1),
            "avg_response_time": 5.2,  # Mock data for now
            "monthly_applications": monthly_applications,
            "application_status": application_status
        }
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@app.post("/api/saved-jobs")
async def save_job(job: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Save a job for a user"""
    try:
        with cloud_db_connection() as conn:
            existing = conn.execute(
                """
                SELECT id FROM saved_jobs 
                WHERE user_id = ? AND (job_id = ? OR job_url = ?)
                """, (current_user["id"], job.get("id"), job.get("url"))
            ).fetchone()
            if existing:
                return {"message": "Job already saved"}
            conn.execute(
                """
                INSERT INTO saved_jobs (user_id, job_id, job_url, job_data, saved_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    current_user["id"],
                    job.get("id"),
                    job.get("url"),
                    json.dumps(job),
                    datetime.now().isoformat()
                )
            )
            conn.commit()
        return {"message": "Job saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save job: {str(e)}")

@app.get("/api/saved-jobs")
async def get_saved_jobs(current_user: dict = Depends(get_current_user)):
    """Get saved jobs for a user"""
    try:
        with cloud_db_connection() as conn:
            saved_jobs_data = conn.execute(
                """
                SELECT job_data FROM saved_jobs 
                WHERE user_id = ? 
                ORDER BY saved_at DESC
                """, (current_user["id"],)
            ).fetchall()
        saved_jobs = []
        for (job_data,) in saved_jobs_data:
            saved_jobs.append(json.loads(job_data))
        return saved_jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch saved jobs: {str(e)}")

@app.get("/api/preferences")
async def get_user_preferences(current_user: dict = Depends(get_current_user)):
    """Get user preferences"""
    try:
        with cloud_db_connection() as conn:
            # Get user preferences
            cursor = conn.execute(
                "SELECT * FROM user_preferences WHERE user_id = ?",
                (current_user["id"],)
            )
            preferences = cursor.fetchone()
            
            if not preferences:
                # Create default preferences if none exist
                conn.execute("""
                    INSERT INTO user_preferences (
                        user_id, max_results_per_search, auto_apply_enabled, 
                        email_notifications, ai_suggestions_enabled, ats_analysis_enabled,
                        salary_currency, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    current_user["id"], 50, False, True, True, True, "USD",
                    datetime.now().isoformat()
                ))
                conn.commit()
                
                # Fetch the newly created preferences
                cursor = conn.execute(
                    "SELECT * FROM user_preferences WHERE user_id = ?",
                    (current_user["id"],)
                )
                preferences = cursor.fetchone()
            
            # Convert to dictionary
            columns = [desc[0] for desc in cursor.description]
            preferences_dict = dict(zip(columns, preferences))
            
            return {
                "preferred_job_titles": json.loads(preferences_dict.get("preferred_job_titles") or "[]"),
                "preferred_locations": json.loads(preferences_dict.get("preferred_locations") or "[]"),
                "preferred_job_types": json.loads(preferences_dict.get("preferred_job_types") or "[]"),
                "salary_min": preferences_dict.get("salary_min"),
                "salary_max": preferences_dict.get("salary_max"),
                "salary_currency": preferences_dict.get("salary_currency") or "USD",
                "remote_work_preference": bool(preferences_dict.get("remote_work_preference")),
                "max_results_per_search": preferences_dict.get("max_results_per_search") or 50,
                "auto_apply_enabled": bool(preferences_dict.get("auto_apply_enabled")),
                "job_sources": json.loads(preferences_dict.get("job_sources") or "[]"),
                "email_notifications": bool(preferences_dict.get("email_notifications")),
                "application_reminders": bool(preferences_dict.get("application_reminders")),
                "daily_job_alerts": bool(preferences_dict.get("daily_job_alerts")),
                "ai_suggestions_enabled": bool(preferences_dict.get("ai_suggestions_enabled")),
                "ats_analysis_enabled": bool(preferences_dict.get("ats_analysis_enabled")),
                "auto_resume_optimization": bool(preferences_dict.get("auto_resume_optimization"))
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch preferences: {str(e)}")

@app.patch("/api/preferences")
async def update_user_preferences(
    preferences_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        with cloud_db_connection() as conn:
            # Check if preferences exist
            existing = conn.execute(
                "SELECT id FROM user_preferences WHERE user_id = ?",
                (current_user["id"],)
            ).fetchone()
            
            if not existing:
                # Create default preferences first
                conn.execute("""
                    INSERT INTO user_preferences (
                        user_id, max_results_per_search, auto_apply_enabled, 
                        email_notifications, ai_suggestions_enabled, ats_analysis_enabled,
                        salary_currency, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    current_user["id"], 50, False, True, True, True, "USD",
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            # Build update query
            update_fields = []
            update_values = []
            
            if "jobTypes" in preferences_data:
                update_fields.append("preferred_job_types = ?")
                update_values.append(json.dumps(preferences_data["jobTypes"]))
            
            if "locations" in preferences_data:
                update_fields.append("preferred_locations = ?")
                update_values.append(json.dumps(preferences_data["locations"]))
            
            if "industries" in preferences_data:
                update_fields.append("preferred_job_titles = ?")
                update_values.append(json.dumps(preferences_data["industries"]))
            
            if "salaryRange" in preferences_data:
                # Parse salary range (e.g., "80000-150000")
                range_parts = preferences_data["salaryRange"].split("-")
                if len(range_parts) == 2:
                    update_fields.append("salary_min = ?")
                    update_values.append(int(range_parts[0]))
                    update_fields.append("salary_max = ?")
                    update_values.append(int(range_parts[1]))
            
            if "salaryCurrency" in preferences_data:
                update_fields.append("salary_currency = ?")
                update_values.append(preferences_data["salaryCurrency"])
            
            if update_fields:
                update_fields.append("updated_at = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(current_user["id"])
                
                query = f"""
                    UPDATE user_preferences 
                    SET {', '.join(update_fields)}
                    WHERE user_id = ?
                """
                
                conn.execute(query, update_values)
                conn.commit()
            
            return {"message": "Preferences updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

@app.get("/api/activity/recent")
async def get_recent_activity(
    current_user: dict = Depends(get_current_user),
    limit: int = 10
):
    """Get recent activity for a user"""
    try:
        with cloud_db_connection() as conn:
            activities = conn.execute(
                """
                SELECT id, activity_type, title, description, entity_type, entity_id, activity_metadata, created_at
                FROM activities 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
                """, (current_user["id"], limit)
            ).fetchall()
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                "id": activity[0],
                "activity_type": activity[1],
                "title": activity[2],
                "description": activity[3],
                "entity_type": activity[4],
                "entity_id": activity[5],
                "metadata": json.loads(activity[6]) if activity[6] else None,
                "created_at": activity[7]
            })
        
        return {"activities": activity_list}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent activity: {str(e)}")

@app.post("/api/activity")
async def log_activity(
    activity_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Log a new activity for a user"""
    print(f"🔍 [DEBUG] Activity logging request received")
    print(f"📋 [DEBUG] Current user: {current_user}")
    print(f"📋 [DEBUG] Activity data: {json.dumps(activity_data, indent=2)}")
    
    try:
        # Validate required fields - accept both 'type' and 'activity_type'
        activity_type = activity_data.get("activity_type") or activity_data.get("type")
        if not activity_type:
            print("❌ [DEBUG] Missing required field: activity_type or type")
            raise HTTPException(status_code=400, detail="Missing required field: activity_type or type")
        
        if not activity_data.get("title"):
            print("❌ [DEBUG] Missing required field: title")
            raise HTTPException(status_code=400, detail="Missing required field: title")
        
        print(f"✅ [DEBUG] Required fields validated")
        print(f"✅ [DEBUG] Using activity_type: {activity_type}")
        
        # Prepare data for insertion
        insert_data = (
            current_user["id"],
            activity_type,
            activity_data.get("title"),
            activity_data.get("description"),
            activity_data.get("entity_type"),
            activity_data.get("entity_id"),
            json.dumps(activity_data.get("metadata", {}))
        )
        
        print(f"📋 [DEBUG] Insert data: {insert_data}")
        
        with cloud_db_connection() as conn:
            print(f"🔗 [DEBUG] Database connection established")
            conn.execute(
                """
                INSERT INTO activities (user_id, activity_type, title, description, entity_type, entity_id, activity_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                insert_data
            )
            print(f"✅ [DEBUG] SQL executed successfully")
            conn.commit()
            print(f"✅ [DEBUG] Transaction committed")
        
        print(f"🎉 [DEBUG] Activity logged successfully")
        return {"message": "Activity logged successfully"}
    except HTTPException:
        print(f"❌ [DEBUG] HTTPException raised")
        raise
    except Exception as e:
        print(f"❌ [DEBUG] Exception occurred: {e}")
        print(f"❌ [DEBUG] Exception type: {type(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to log activity: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 