import requests

BASE_URL = "http://localhost:8000"
USERNAME = "testuser"
PASSWORD = "testpassword"
RESUME_PATH = "resume.pdf"  # Path to a sample PDF resume

def signup():
    resp = requests.post(f"{BASE_URL}/api/auth/signup", json={
        "username": USERNAME,
        "password": PASSWORD,
        "email": f"{USERNAME}@example.com"
    })
    print("Signup:", resp.status_code, resp.json())

def login():
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    print("Login:", resp.status_code, resp.json())
    return resp.json()["access_token"]

def upload_resume(token):
    with open(RESUME_PATH, "rb") as f:
        files = {"file": (RESUME_PATH, f, "application/pdf")}
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(f"{BASE_URL}/api/resume", files=files, headers=headers)
    print("Upload Resume:", resp.status_code, resp.json())

def get_matches(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/match", headers=headers)
    print("Job Matches:", resp.status_code)
    if resp.status_code == 200:
        for job in resp.json():
            print(f"- {job['title']} at {job['company']}: Score={job.get('matchScore')}, Explanation={job.get('matchExplanation')}")
    else:
        print(resp.json())

if __name__ == "__main__":
    try:
        signup()
    except Exception:
        pass  # User may already exist
    token = login()
    upload_resume(token)
    get_matches(token)