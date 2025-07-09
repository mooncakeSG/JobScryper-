from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from typing import List, Dict, Any
import json
from pathlib import Path

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
        # Mock application creation
        application = {
            "id": "app_123",
            "job_title": application_data.get("job_title", ""),
            "company": application_data.get("company", ""),
            "location": application_data.get("location", ""),
            "status": "applied",
            "date_applied": "2024-01-15",
            "match_score": application_data.get("match_score", 0)
        }
        
        return {"message": "Application created successfully", "application": application}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {str(e)}")

@app.get("/api/applications")
async def get_applications(user_id: str = "demo"):
    """Get user's job applications"""
    try:
        # Mock applications data
        applications = [
            {
                "id": "app_1",
                "job_title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "location": "San Francisco, CA",
                "status": "interview",
                "date_applied": "2024-01-10",
                "match_score": 95
            },
            {
                "id": "app_2",
                "job_title": "Frontend Developer",
                "company": "StartupXYZ",
                "location": "Remote",
                "status": "applied",
                "date_applied": "2024-01-08",
                "match_score": 88
            }
        ]
        
        return applications
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch applications: {str(e)}")

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 