#!/usr/bin/env python3
"""
Comprehensive API Testing Script for JobScryper Backend
Tests all endpoints and identifies what's needed for the frontend
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8000"
DEMO_USER = "demo"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            return {
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests"""
        print("🚀 Starting comprehensive API testing...\n")
        
        # Test 1: Health Check
        print("1. Testing Health Check...")
        self.results["health"] = self.test_endpoint("GET", "/health")
        print(f"   Status: {self.results['health']['status_code']}")
        
        # Test 2: Root endpoint
        print("2. Testing Root Endpoint...")
        self.results["root"] = self.test_endpoint("GET", "/")
        print(f"   Status: {self.results['root']['status_code']}")
        
        # Test 3: Applications API - GET
        print("3. Testing Applications GET...")
        self.results["applications_get"] = self.test_endpoint("GET", "/api/applications", params={"user_id": DEMO_USER})
        print(f"   Status: {self.results['applications_get']['status_code']}")
        
        # Test 4: Applications API - POST (Create)
        print("4. Testing Applications POST...")
        test_application = {
            "job_title": "API Test Engineer",
            "company": "Test Company Inc",
            "location": "Remote",
            "status": "applied",
            "salary_min": 80000,
            "salary_max": 120000,
            "notes": "Created via API test"
        }
        self.results["applications_post"] = self.test_endpoint("POST", "/api/applications", data=test_application)
        print(f"   Status: {self.results['applications_post']['status_code']}")
        
        # Test 5: Applications API - PATCH (Update)
        print("5. Testing Applications PATCH...")
        if self.results["applications_post"]["success"]:
            app_id = self.results["applications_post"]["data"]["application"]["id"]
            update_data = {
                "status": "interview_scheduled",
                "notes": "Updated via API test"
            }
            self.results["applications_patch"] = self.test_endpoint("PATCH", f"/api/applications/{app_id}", data=update_data)
            print(f"   Status: {self.results['applications_patch']['status_code']}")
        else:
            print("   Skipped - No application created")
        
        # Test 6: Applications API - DELETE
        print("6. Testing Applications DELETE...")
        if self.results["applications_post"]["success"]:
            app_id = self.results["applications_post"]["data"]["application"]["id"]
            self.results["applications_delete"] = self.test_endpoint("DELETE", f"/api/applications/{app_id}")
            print(f"   Status: {self.results['applications_delete']['status_code']}")
        else:
            print("   Skipped - No application created")
        
        # Test 7: Analytics API
        print("7. Testing Analytics API...")
        self.results["analytics"] = self.test_endpoint("GET", "/api/analytics", params={"user_id": DEMO_USER})
        print(f"   Status: {self.results['analytics']['status_code']}")
        
        # Test 8: Job Search API
        print("8. Testing Job Search API...")
        search_params = {
            "query": "software engineer",
            "location": "remote",
            "max_results": 5
        }
        self.results["job_search"] = self.test_endpoint("GET", "/api/match", params=search_params)
        print(f"   Status: {self.results['job_search']['status_code']}")
        
        # Test 9: Saved Jobs API - GET
        print("9. Testing Saved Jobs GET...")
        self.results["saved_jobs_get"] = self.test_endpoint("GET", "/api/saved-jobs", params={"user_id": DEMO_USER})
        print(f"   Status: {self.results['saved_jobs_get']['status_code']}")
        
        # Test 10: Saved Jobs API - POST
        print("10. Testing Saved Jobs POST...")
        test_job = {
            "id": "test_job_1",
            "title": "Test Job",
            "company": "Test Company",
            "location": "Remote",
            "url": "https://example.com/test-job"
        }
        self.results["saved_jobs_post"] = self.test_endpoint("POST", "/api/saved-jobs", data=test_job, params={"user_id": DEMO_USER})
        print(f"   Status: {self.results['saved_jobs_post']['status_code']}")
        
        # Test 11: Resume Analysis API
        print("11. Testing Resume Analysis API...")
        # Note: This would require a file upload, so we'll just test the endpoint structure
        self.results["resume_analysis"] = {"note": "Requires file upload - manual testing needed"}
        print("   Note: Requires file upload")
        
        # Test 12: Authentication APIs
        print("12. Testing Authentication APIs...")
        self.results["auth_signup"] = self.test_endpoint("POST", "/api/auth/signup", data={"username": "testuser", "password": "testpass"})
        print(f"   Signup Status: {self.results['auth_signup']['status_code']}")
        
        self.results["auth_login"] = self.test_endpoint("POST", "/api/auth/login", data={"username": "testuser", "password": "testpass"})
        print(f"   Login Status: {self.results['auth_login']['status_code']}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("=" * 60)
        report.append("🔍 JOBSCRYPER API TESTING REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if isinstance(result, dict) and result.get("success", False))
        failed_tests = total_tests - successful_tests
        
        report.append(f"📊 SUMMARY:")
        report.append(f"   Total Tests: {total_tests}")
        report.append(f"   Successful: {successful_tests}")
        report.append(f"   Failed: {failed_tests}")
        report.append(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        report.append("")
        
        # Detailed Results
        report.append("📋 DETAILED RESULTS:")
        report.append("-" * 40)
        
        for test_name, result in self.results.items():
            if isinstance(result, dict):
                if result.get("success", False):
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                
                report.append(f"{status} {test_name.upper()}")
                if "status_code" in result:
                    report.append(f"   Status Code: {result['status_code']}")
                if "error" in result:
                    report.append(f"   Error: {result['error']}")
                report.append("")
        
        # Frontend Requirements Analysis
        report.append("🎯 FRONTEND API REQUIREMENTS:")
        report.append("-" * 40)
        
        frontend_apis = {
            "applications": {
                "GET /api/applications": "List user applications",
                "POST /api/applications": "Create new application",
                "PATCH /api/applications/{id}": "Update application status",
                "DELETE /api/applications/{id}": "Delete application"
            },
            "analytics": {
                "GET /api/analytics": "Get user analytics data"
            },
            "job_search": {
                "GET /api/match": "Search for jobs"
            },
            "saved_jobs": {
                "GET /api/saved-jobs": "Get saved jobs",
                "POST /api/saved-jobs": "Save a job"
            },
            "authentication": {
                "POST /api/auth/signup": "User registration",
                "POST /api/auth/login": "User login",
                "GET /api/auth/me": "Get current user"
            },
            "resume": {
                "POST /api/resume": "Analyze resume"
            }
        }
        
        for category, apis in frontend_apis.items():
            report.append(f"\n📁 {category.upper()}:")
            for endpoint, description in apis.items():
                # Check if this endpoint was tested
                tested = False
                for test_name, result in self.results.items():
                    if endpoint.split()[1] in test_name:
                        tested = result.get("success", False)
                        break
                
                status = "✅" if tested else "❌"
                report.append(f"   {status} {endpoint} - {description}")
        
        # Recommendations
        report.append("\n💡 RECOMMENDATIONS:")
        report.append("-" * 40)
        
        if self.results.get("applications_get", {}).get("success"):
            report.append("✅ Applications API is working - Frontend can display applications")
        else:
            report.append("❌ Applications API needs fixing - Frontend applications page won't work")
        
        if self.results.get("analytics", {}).get("success"):
            report.append("✅ Analytics API is working - Frontend can show analytics")
        else:
            report.append("❌ Analytics API needs fixing - Frontend analytics page won't work")
        
        if self.results.get("job_search", {}).get("success"):
            report.append("✅ Job Search API is working - Frontend can search jobs")
        else:
            report.append("❌ Job Search API needs fixing - Frontend job search won't work")
        
        if self.results.get("auth_login", {}).get("success"):
            report.append("✅ Authentication API is working - Frontend can handle login")
        else:
            report.append("❌ Authentication API needs fixing - Frontend login won't work")
        
        return "\n".join(report)

def main():
    """Main function to run the API tests"""
    print("🔧 JobScryper API Testing Tool")
    print("=" * 40)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend is not responding properly. Status: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend at {BASE_URL}")
        print(f"   Error: {e}")
        print("   Make sure the backend is running with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Run tests
    tester = APITester(BASE_URL)
    results = tester.run_all_tests()
    
    # Generate and print report
    report = tester.generate_report()
    print("\n" + report)
    
    # Save report to file
    with open("api_test_report.txt", "w") as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: api_test_report.txt")

if __name__ == "__main__":
    main() 