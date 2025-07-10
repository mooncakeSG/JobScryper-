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

# In-memory store for saved jobs (for demo purposes)
saved_jobs_store = {}

# Simple in-memory user store for demo
users_store = {}
SECRET_KEY = "demo_secret_key"  # In production, use a secure random key!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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
        if username is None or username not in users_store:
            raise credentials_exception
        return {"username": username}
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
    
    try:
        # Save the uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse the resume
        resume_data = resume_parser.parse_resume(temp_path)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        # Mock ATS analysis (replace with actual implementation)
        analysis = {
            "ats_score": 85,
            "suggestions": [
                "Add more technical keywords relevant to your field",
                "Include quantifiable achievements in your experience",
                "Ensure consistent formatting throughout the document"
            ],
            "strengths": [
                "Strong technical skills section",
                "Clear work experience progression",
                "Professional formatting"
            ],
            "keywords": ["Python", "React", "AWS", "Machine Learning", "API", "Database"],
            "improvements": [
                "Add more action verbs",
                "Include relevant certifications",
                "Optimize for ATS scanning"
            ]
        }
        
        return analysis
        
    except Exception as e:
        # Clean up temporary file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to analyze resume: {str(e)}")

@app.post("/api/auth/signup")
async def signup(form: OAuth2PasswordRequestForm = Depends()):
    if form.username in users_store:
        raise HTTPException(status_code=400, detail="Username already registered")
    users_store[form.username] = {"username": form.username, "password": form.password}
    return {"message": "User registered successfully"}

@app.post("/api/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = users_store.get(form.username)
    if not user or user["password"] != form.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": form.username})
    return {"access_token": access_token, "token_type": "bearer"}

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
async def create_application(application_data: Dict[str, Any]):
    """Create a new job application"""
    try:
        # Validate required fields
        required_fields = ["job_title", "company"]
        for field in required_fields:
            if not application_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create application object
        application = {
            "id": len(saved_jobs_store.get("applications", [])) + 1,
            "job_title": application_data.get("job_title"),
            "company": application_data.get("company"),
            "location": application_data.get("location", ""),
            "status": application_data.get("status", "applied"),
            "application_date": datetime.now().isoformat(),
            "salary_min": application_data.get("salary_min"),
            "salary_max": application_data.get("salary_max"),
            "job_url": application_data.get("job_url"),
            "interview_date": application_data.get("interview_date"),
            "notes": application_data.get("notes"),
            "match_score": application_data.get("match_score", 0)
        }
        
        # Store in memory (replace with database in production)
        if "applications" not in saved_jobs_store:
            saved_jobs_store["applications"] = []
        saved_jobs_store["applications"].append(application)
        
        return {"message": "Application created successfully", "application": application}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {str(e)}")

@app.get("/api/applications")
async def get_applications(
    user_id: str = "demo",
    status: str = None,
    search: str = None,
    page: int = 1,
    limit: int = 20
):
    """Get user's job applications with filtering and pagination"""
    try:
        # Get applications from memory (replace with database in production)
        applications = saved_jobs_store.get("applications", [])
        
        # Add mock data if empty
        if not applications:
            applications = [
                {
                    "id": 1,
                    "job_title": "Senior Software Engineer",
                    "company": "TechCorp",
                    "location": "San Francisco, CA",
                    "status": "interview_scheduled",
                    "application_date": "2024-01-15T10:00:00",
                    "salary_min": 120000,
                    "salary_max": 180000,
                    "job_url": "https://example.com/job1",
                    "interview_date": "2024-01-25T14:00:00",
                    "notes": "Phone interview scheduled with hiring manager",
                    "match_score": 95
                },
                {
                    "id": 2,
                    "job_title": "Full Stack Developer",
                    "company": "StartupXYZ",
                    "location": "Remote",
                    "status": "applied",
                    "application_date": "2024-01-14T09:30:00",
                    "salary_min": 90000,
                    "salary_max": 130000,
                    "job_url": "https://example.com/job2",
                    "notes": "Applied via company website",
                    "match_score": 88
                },
                {
                    "id": 3,
                    "job_title": "Frontend Engineer",
                    "company": "BigTech Inc",
                    "location": "New York, NY",
                    "status": "rejected",
                    "application_date": "2024-01-10T11:15:00",
                    "salary_min": 110000,
                    "salary_max": 160000,
                    "notes": "Rejected after technical interview",
                    "match_score": 92
                },
                {
                    "id": 4,
                    "job_title": "DevOps Engineer",
                    "company": "CloudSolutions",
                    "location": "Austin, TX",
                    "status": "offer_received",
                    "application_date": "2024-01-08T16:45:00",
                    "salary_min": 100000,
                    "salary_max": 140000,
                    "notes": "Great offer! Considering acceptance",
                    "match_score": 87
                },
                {
                    "id": 5,
                    "job_title": "Product Manager",
                    "company": "Innovation Labs",
                    "location": "Seattle, WA",
                    "status": "pending",
                    "application_date": "2024-01-12T13:20:00",
                    "salary_min": 130000,
                    "salary_max": 190000,
                    "notes": "Application submitted, waiting for response",
                    "match_score": 78
                }
            ]
            saved_jobs_store["applications"] = applications
        
        # Apply filters
        filtered_applications = applications
        
        if status and status != "all":
            filtered_applications = [app for app in filtered_applications if app["status"] == status]
        
        if search:
            search_lower = search.lower()
            filtered_applications = [
                app for app in filtered_applications 
                if (search_lower in app["job_title"].lower() or 
                    search_lower in app["company"].lower() or 
                    search_lower in app.get("location", "").lower())
            ]
        
        # Apply pagination
        total_count = len(filtered_applications)
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_applications = filtered_applications[start_index:end_index]
        
        return {
            "applications": paginated_applications,
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
async def update_application(application_id: int, update_data: Dict[str, Any]):
    """Update an existing job application"""
    try:
        applications = saved_jobs_store.get("applications", [])
        application = next((app for app in applications if app["id"] == application_id), None)
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update allowed fields
        allowed_fields = ["status", "notes", "interview_date", "salary_min", "salary_max"]
        for field in allowed_fields:
            if field in update_data:
                application[field] = update_data[field]
        
        return {"message": "Application updated successfully", "application": application}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update application: {str(e)}")

@app.delete("/api/applications/{application_id}")
async def delete_application(application_id: int):
    """Delete a job application"""
    try:
        applications = saved_jobs_store.get("applications", [])
        application = next((app for app in applications if app["id"] == application_id), None)
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        applications.remove(application)
        saved_jobs_store["applications"] = applications
        
        return {"message": "Application deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")

@app.get("/api/analytics")
async def get_analytics(user_id: str = "demo"):
    """Get user's analytics data"""
    try:
        # Mock analytics data
        analytics = {
            "total_applications": 150,
            "interview_rate": 18.7,
            "response_rate": 34.5,
            "avg_response_time": 5.2,
            "monthly_applications": [
                {"month": "Jan", "applications": 12, "interviews": 2, "offers": 0},
                {"month": "Feb", "applications": 18, "interviews": 3, "offers": 1},
                {"month": "Mar", "applications": 25, "interviews": 4, "offers": 1},
                {"month": "Apr", "applications": 32, "interviews": 6, "offers": 2},
                {"month": "May", "applications": 28, "interviews": 5, "offers": 1},
                {"month": "Jun", "applications": 35, "interviews": 7, "offers": 3}
            ],
            "application_status": [
                {"name": "Applied", "value": 45},
                {"name": "Under Review", "value": 25},
                {"name": "Interview", "value": 15},
                {"name": "Rejected", "value": 12},
                {"name": "Offer", "value": 3}
            ]
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")

@app.post("/api/saved-jobs")
async def save_job(user_id: str = "demo", job: dict = Body(...)):
    """Save a job for a user (in-memory demo)."""
    if user_id not in saved_jobs_store:
        saved_jobs_store[user_id] = []
    # Avoid duplicates by job id/url
    for saved in saved_jobs_store[user_id]:
        if saved.get("id") == job.get("id") or saved.get("url") == job.get("url"):
            return {"message": "Job already saved"}
    saved_jobs_store[user_id].append(job)
    return {"message": "Job saved successfully"}

@app.get("/api/saved-jobs")
async def get_saved_jobs(user_id: str = "demo"):
    """Get saved jobs for a user (in-memory demo)."""
    return saved_jobs_store.get(user_id, [])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 