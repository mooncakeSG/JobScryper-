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

# Add the parent directory to the Python path to import existing modules
sys.path.append(str(Path(__file__).parent.parent))

# Import existing modules
try:
    from resume_parser import ResumeParser
    from jobspy_wrapper import JobSpyWrapper
    from alternative_sources import AlternativeJobAggregator
    from matcher import JobResumeMatcher
    from database.utilities import DatabaseUtils
    from database.models import User, JobApplication, ApplicationStatus
    from database import fetchall, fetchone, execute
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    print("Some features may not work properly.")

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
        
        # Verify user exists in database
        user = fetchone("SELECT id, username FROM users WHERE username = ?", (username,))
        if not user:
            raise credentials_exception
        
        return {"id": user[0], "username": user[1]}
    except JWTError:
        raise credentials_exception

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global resume_parser, job_spy_wrapper, job_aggregator, job_matcher
    
    try:
        resume_parser = ResumeParser()
        job_spy_wrapper = JobSpyWrapper()
        job_aggregator = AlternativeJobAggregator()
        job_matcher = JobResumeMatcher()
        print("✅ All services initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Some services failed to initialize: {e}")

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
async def analyze_resume(file: UploadFile = File(...)):
    """Analyze uploaded resume for ATS optimization"""
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
    """User registration endpoint"""
    username = user_data.get("username")
    password = user_data.get("password")
    email = user_data.get("email", "")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    # If no email provided, use username@example.com as placeholder
    if not email:
        email = f"{username}@example.com"
    
    try:
        # Check if username already exists
        existing_user = fetchone("SELECT id FROM users WHERE username = ?", (username,))
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check if email already exists
        existing_email = fetchone("SELECT id FROM users WHERE email = ?", (email,))
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user
        hashed_password = hash_password(password)
        user_id = execute(
            "INSERT INTO users (username, password_hash, email, is_active, is_verified, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (username, hashed_password, email, True, False, datetime.now().isoformat())
        )
        
        return {"message": "User registered successfully", "user_id": user_id}
    except Exception as e:
        print(f"Signup error: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/auth/login")
async def login(user_data: dict = Body(...)):
    """User login endpoint"""
    username = user_data.get("username")
    password = user_data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    # Get user from database (try username first, then email)
    user = fetchone("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    if not user:
        # Try email if username not found
        user = fetchone("SELECT id, username, password_hash FROM users WHERE email = ?", (username,))
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Verify password
    hashed_password = hash_password(password)
    if user[2] != hashed_password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user[1]})  # Use actual username from DB
    return {"access_token": access_token, "token_type": "bearer", "user_id": user[0]}

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
    max_results: int = 50
):
    """Search for job matches"""
    try:
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
                    job['matchScore'] = 85  # Mock match score
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
                    job['matchScore'] = 78  # Mock match score
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
                    "matchScore": 95,
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
                    "matchScore": 88,
                    "datePosted": "1 week ago",
                    "jobType": "Full-time",
                    "source": "Indeed",
                    "url": "https://example.com/job2"
                }
            ]
        
        return all_jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/applications")
async def create_application(application_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Create a new job application"""
    try:
        # Validate required fields
        required_fields = ["job_title", "company"]
        for field in required_fields:
            if not application_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Insert application into database
        application_id = execute("""
            INSERT INTO job_applications (
                user_id, job_title, company, location, status, application_date,
                salary_min, salary_max, job_url, interview_date, notes, match_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
        ))
        
        # Fetch the created application
        application = fetchone("""
            SELECT id, job_title, company, location, status, application_date,
                   salary_min, salary_max, job_url, interview_date, notes, match_score
            FROM job_applications WHERE id = ?
        """, (application_id,))
        
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
        # Build query with filters
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
        
        # Get total count for pagination
        count_query = query.replace("SELECT id, job_title, company, location, status, application_date, salary_min, salary_max, job_url, interview_date, notes, match_score", "SELECT COUNT(*)")
        total_count = fetchone(count_query, params)[0]
        
        # Add pagination
        query += " ORDER BY application_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, (page - 1) * limit])
        
        # Execute query
        applications_data = fetchall(query, params)
        
        # Format applications
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
        raise HTTPException(status_code=500, detail=f"Failed to fetch applications: {str(e)}")

@app.patch("/api/applications/{application_id}")
async def update_application(application_id: int, update_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Update an existing job application"""
    try:
        # Verify application belongs to user
        application = fetchone("""
            SELECT id FROM job_applications 
            WHERE id = ? AND user_id = ?
        """, (application_id, current_user["id"]))
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Build update query
        allowed_fields = ["status", "notes", "interview_date", "salary_min", "salary_max"]
        update_parts = []
        params = []
        
        for field in allowed_fields:
            if field in update_data:
                update_parts.append(f"{field} = ?")
                params.append(update_data[field])
        
        if not update_parts:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Execute update
        query = f"UPDATE job_applications SET {', '.join(update_parts)} WHERE id = ? AND user_id = ?"
        params.extend([application_id, current_user["id"]])
        execute(query, params)
        
        # Fetch updated application
        updated_app = fetchone("""
            SELECT id, job_title, company, location, status, application_date,
                   salary_min, salary_max, job_url, interview_date, notes, match_score
            FROM job_applications WHERE id = ?
        """, (application_id,))
        
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
        # Verify application belongs to user
        application = fetchone("""
            SELECT id FROM job_applications 
            WHERE id = ? AND user_id = ?
        """, (application_id, current_user["id"]))
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Delete application
        execute("DELETE FROM job_applications WHERE id = ? AND user_id = ?", (application_id, current_user["id"]))
        
        return {"message": "Application deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")

@app.get("/api/analytics")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    """Get user's analytics data"""
    try:
        # Get real analytics from database
        total_applications = fetchone("""
            SELECT COUNT(*) FROM job_applications WHERE user_id = ?
        """, (current_user["id"],))[0]
        
        # Get status distribution
        status_counts = fetchall("""
            SELECT status, COUNT(*) as count 
            FROM job_applications 
            WHERE user_id = ? 
            GROUP BY status
        """, (current_user["id"],))
        
        # Get monthly applications (last 6 months)
        monthly_data = fetchall("""
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
        """, (current_user["id"],))
        
        # Calculate rates
        interview_count = sum(count for _, count in status_counts if _ in ['interview_scheduled', 'interview_completed'])
        interview_rate = (interview_count / total_applications * 100) if total_applications > 0 else 0
        
        response_count = sum(count for _, count in status_counts if _ not in ['applied', 'pending'])
        response_rate = (response_count / total_applications * 100) if total_applications > 0 else 0
        
        # Format monthly data
        monthly_applications = []
        for month, apps, interviews, offers in monthly_data:
            monthly_applications.append({
                "month": month,
                "applications": apps,
                "interviews": interviews,
                "offers": offers
            })
        
        # Format status data
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
        # Check if job already saved
        existing = fetchone("""
            SELECT id FROM saved_jobs 
            WHERE user_id = ? AND (job_id = ? OR job_url = ?)
        """, (current_user["id"], job.get("id"), job.get("url")))
        
        if existing:
            return {"message": "Job already saved"}
        
        # Save job
        execute("""
            INSERT INTO saved_jobs (user_id, job_id, job_url, job_data, saved_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            current_user["id"],
            job.get("id"),
            job.get("url"),
            json.dumps(job),
            datetime.now().isoformat()
        ))
        
        return {"message": "Job saved successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save job: {str(e)}")

@app.get("/api/saved-jobs")
async def get_saved_jobs(current_user: dict = Depends(get_current_user)):
    """Get saved jobs for a user"""
    try:
        saved_jobs_data = fetchall("""
            SELECT job_data FROM saved_jobs 
            WHERE user_id = ? 
            ORDER BY saved_at DESC
        """, (current_user["id"],))
        
        saved_jobs = []
        for (job_data,) in saved_jobs_data:
            saved_jobs.append(json.loads(job_data))
        
        return saved_jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch saved jobs: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 