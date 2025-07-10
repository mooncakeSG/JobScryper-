"""
Unit tests for job applications functionality
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

class TestApplicationsAPI:
    """Test cases for applications API endpoints"""
    
    def test_get_applications_success(self):
        """Test successful retrieval of applications"""
        response = client.get("/api/applications?user_id=demo")
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data
        assert "pagination" in data
        assert isinstance(data["applications"], list)
    
    def test_get_applications_with_filters(self):
        """Test applications retrieval with filters"""
        response = client.get("/api/applications?user_id=demo&status=applied&search=engineer")
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data
    
    def test_create_application_success(self):
        """Test successful application creation"""
        application_data = {
            "job_title": "Software Engineer",
            "company": "Test Company",
            "location": "Remote",
            "status": "applied"
        }
        response = client.post("/api/applications", json=application_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "application" in data
        assert data["application"]["job_title"] == "Software Engineer"
    
    def test_create_application_missing_fields(self):
        """Test application creation with missing required fields"""
        application_data = {
            "location": "Remote"
        }
        response = client.post("/api/applications", json=application_data)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_update_application_success(self):
        """Test successful application update"""
        # First create an application
        application_data = {
            "job_title": "Test Engineer",
            "company": "Test Company",
            "location": "Remote"
        }
        create_response = client.post("/api/applications", json=application_data)
        assert create_response.status_code == 200
        
        # Update the application
        update_data = {
            "status": "interview_scheduled",
            "notes": "Interview scheduled for next week"
        }
        response = client.patch("/api/applications/1", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["application"]["status"] == "interview_scheduled"
    
    def test_update_application_not_found(self):
        """Test updating non-existent application"""
        update_data = {"status": "applied"}
        response = client.patch("/api/applications/999", json=update_data)
        assert response.status_code == 404
    
    def test_delete_application_success(self):
        """Test successful application deletion"""
        # First create an application
        application_data = {
            "job_title": "Delete Test",
            "company": "Test Company"
        }
        create_response = client.post("/api/applications", json=application_data)
        assert create_response.status_code == 200
        
        # Delete the application
        response = client.delete("/api/applications/1")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_delete_application_not_found(self):
        """Test deleting non-existent application"""
        response = client.delete("/api/applications/999")
        assert response.status_code == 404

class TestApplicationValidation:
    """Test cases for application data validation"""
    
    def test_valid_application_data(self):
        """Test valid application data structure"""
        valid_data = {
            "job_title": "Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "salary_min": 100000,
            "salary_max": 150000,
            "job_url": "https://example.com/job",
            "notes": "Great opportunity"
        }
        response = client.post("/api/applications", json=valid_data)
        assert response.status_code == 200
    
    def test_invalid_salary_range(self):
        """Test application with invalid salary range"""
        invalid_data = {
            "job_title": "Software Engineer",
            "company": "Tech Corp",
            "salary_min": 150000,
            "salary_max": 100000  # Max less than min
        }
        response = client.post("/api/applications", json=invalid_data)
        # This should still work as we're not validating salary ranges yet
        assert response.status_code == 200

class TestApplicationStatuses:
    """Test cases for application status management"""
    
    def test_all_valid_statuses(self):
        """Test that all valid statuses are accepted"""
        valid_statuses = [
            "pending", "applied", "screening", "interview_scheduled",
            "interviewed", "technical_test", "offer_received",
            "offer_accepted", "offer_rejected", "rejected", "withdrawn"
        ]
        
        for status in valid_statuses:
            application_data = {
                "job_title": f"Test {status}",
                "company": "Test Company",
                "status": status
            }
            response = client.post("/api/applications", json=application_data)
            assert response.status_code == 200
            data = response.json()
            assert data["application"]["status"] == status

if __name__ == "__main__":
    pytest.main([__file__]) 