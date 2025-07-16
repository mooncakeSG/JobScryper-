#!/usr/bin/env python3
"""
Test script for resume upload functionality
"""

import requests
import json
import os

def test_resume_upload():
    """Test the resume upload and analysis functionality"""
    
    base_url = "http://localhost:8000"
    
    # First, let's login to get a token
    print("🔐 Testing login...")
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Login successful, got token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test resume upload
            print("\n📄 Testing resume upload...")
            
            # Check if we have a test resume file
            test_resume_path = "Resume.pdf"
            if not os.path.exists(test_resume_path):
                print(f"❌ Test resume file not found: {test_resume_path}")
                print("Please make sure Resume.pdf exists in the current directory")
                return
            
            # Upload the resume
            with open(test_resume_path, "rb") as f:
                files = {"file": (test_resume_path, f, "application/pdf")}
                upload_response = requests.post(f"{base_url}/api/resume", 
                                              files=files, 
                                              headers=headers)
            
            print(f"Resume upload status: {upload_response.status_code}")
            
            if upload_response.status_code == 200:
                analysis = upload_response.json()
                print("✅ Resume upload and analysis successful!")
                print(f"ATS Score: {analysis.get('ats_score', 'N/A')}")
                print(f"Skills found: {len(analysis.get('sections', {}).get('skills', []))}")
                print(f"Suggestions: {len(analysis.get('suggestions', []))}")
                print(f"Strengths: {len(analysis.get('strengths', []))}")
                
                # Show a sample of the analysis
                print("\n📊 Sample Analysis Results:")
                print(json.dumps(analysis, indent=2)[:500] + "...")
                
            else:
                print(f"❌ Resume upload failed: {upload_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing resume upload: {e}")

if __name__ == "__main__":
    test_resume_upload() 