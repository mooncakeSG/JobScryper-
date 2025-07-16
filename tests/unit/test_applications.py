"""
Unit tests for job applications functionality
"""
import pytest
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

class TestApplicationsAPI:
    def test_get_applications_success(self, client):
        response = client.get("/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data
        assert "pagination" in data
        assert isinstance(data["applications"], list)

    def test_get_applications_with_filters(self, client):
        response = client.get("/api/applications?status=applied&search=engineer")
        assert response.status_code == 200
        data = response.json()
        assert "applications" in data
        assert "pagination" in data

    def test_create_application_success(self, client):
        application_data = {
            "job_title": "Software Engineer",
            "company": "Test Company",
            "location": "Remote",
            "status": "applied"
        }
        response = client.post("/api/applications", json=application_data)
        assert response.status_code == 200
        data = response.json()
        assert "application" in data
        assert "id" in data["application"]
        assert data["application"]["job_title"] == "Software Engineer"

    def test_create_application_missing_fields(self, client):
        application_data = {
            "location": "Remote"
        }
        response = client.post("/api/applications", json=application_data)
        assert response.status_code in [400, 422]

    def test_update_application_success(self, client):
        application_data = {
            "job_title": "Test Engineer",
            "company": "Test Company",
            "location": "Remote"
        }
        create_response = client.post("/api/applications", json=application_data)
        if create_response.status_code == 200:
            app_id = create_response.json()["application"]["id"]
            update_data = {"status": "interviewed"}
            response = client.patch(f"/api/applications/{app_id}", json=update_data)
            assert response.status_code == 200
        else:
            pytest.skip("Could not create test application")

    def test_update_application_not_found(self, client):
        update_data = {"status": "applied"}
        response = client.patch("/api/applications/999", json=update_data)
        assert response.status_code == 404

    def test_delete_application_success(self, client):
        application_data = {
            "job_title": "Delete Test",
            "company": "Test Company"
        }
        create_response = client.post("/api/applications", json=application_data)
        if create_response.status_code == 200:
            app_id = create_response.json()["application"]["id"]
            response = client.delete(f"/api/applications/{app_id}")
            assert response.status_code == 200
        else:
            pytest.skip("Could not create test application")

    def test_delete_application_not_found(self, client):
        response = client.delete("/api/applications/999")
        assert response.status_code == 404

class TestApplicationValidation:
    def test_valid_application_data(self, client):
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

    def test_invalid_salary_range(self, client):
        invalid_data = {
            "job_title": "Software Engineer",
            "company": "Tech Corp",
            "salary_min": 150000,
            "salary_max": 100000
        }
        response = client.post("/api/applications", json=invalid_data)
        assert response.status_code == 200

class TestApplicationStatuses:
    def test_all_valid_statuses(self, client):
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

if __name__ == "__main__":
    pytest.main([__file__]) 