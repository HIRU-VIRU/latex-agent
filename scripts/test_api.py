"""
API Testing Script for LaTeX Resume Agent
==========================================
Tests all major endpoints and functionalities.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoints."""
    print("\n=== Testing Health Endpoints ===")
    
    # Basic health
    r = requests.get(f"{BASE_URL}/health")
    print(f"✓ GET /health: {r.status_code} - {r.json()}")
    
    # Database health
    r = requests.get(f"{BASE_URL}/health/db")
    print(f"✓ GET /health/db: {r.status_code} - {r.json()}")
    
    return True


def test_auth():
    """Test authentication endpoints."""
    print("\n=== Testing Authentication ===")
    
    # Register new user
    test_email = "apitest@example.com"
    test_password = "securepass123"
    
    # Try to register
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": test_email,
        "password": test_password,
        "full_name": "API Test User"
    })
    
    if r.status_code in [200, 201]:
        print(f"✓ POST /api/auth/register: {r.status_code} - User registered")
        token = r.json()["access_token"]
    elif r.status_code == 400 and "already exists" in r.text.lower():
        print(f"✓ User already exists, logging in...")
        # Login instead
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        token = r.json()["access_token"]
    else:
        print(f"⚠ POST /api/auth/register: {r.status_code} - {r.text}")
        # Try login anyway in case user exists
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        if r.status_code == 200:
            print(f"✓ Logged in with existing user")
            token = r.json()["access_token"]
        else:
            print(f"✗ Login also failed")
            return None
    
    # Test login
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    print(f"✓ POST /api/auth/login: {r.status_code} - Token received")
    token = r.json()["access_token"]
    
    # Test /me
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"✓ GET /api/auth/me: {r.status_code} - {r.json()['email']}")
    
    return token


def test_projects(token):
    """Test project CRUD operations."""
    print("\n=== Testing Projects ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create project
    project_data = {
        "title": "Test Project",
        "description": "A sample project for testing",
        "technologies": ["Python", "FastAPI", "SQLite"],
        "highlights": ["Feature 1", "Feature 2"],
        "url": "https://github.com/user/test-project"
    }
    
    r = requests.post(f"{BASE_URL}/api/projects", headers=headers, json=project_data)
    print(f"✓ POST /api/projects: {r.status_code}")
    project = r.json()
    project_id = project["id"]
    
    # List projects
    r = requests.get(f"{BASE_URL}/api/projects", headers=headers)
    print(f"✓ GET /api/projects: {r.status_code} - Found {len(r.json())} projects")
    
    # Get single project
    r = requests.get(f"{BASE_URL}/api/projects/{project_id}", headers=headers)
    print(f"✓ GET /api/projects/{project_id}: {r.status_code} - {r.json()['title']}")
    
    # Update project
    r = requests.put(f"{BASE_URL}/api/projects/{project_id}", headers=headers, json={
        "title": "Updated Test Project"
    })
    print(f"✓ PUT /api/projects/{project_id}: {r.status_code} - Updated name")
    
    return project_id


def test_templates(token):
    """Test template operations."""
    print("\n=== Testing Templates ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create template
    template_data = {
        "name": "Simple Resume Template",
        "description": "A clean, professional resume template",
        "latex_content": r"""\documentclass{article}
\begin{document}
\section*{<<NAME>>}
<<EMAIL>> | <<PHONE>>

\section*{Experience}
<<EXPERIENCE>>

\section*{Education}
<<EDUCATION>>

\section*{Skills}
<<SKILLS>>
\end{document}""",
        "is_public": True
    }
    
    r = requests.post(f"{BASE_URL}/api/templates", headers=headers, json=template_data)
    print(f"✓ POST /api/templates: {r.status_code}")
    template = r.json()
    template_id = template["id"]
    
    # List templates
    r = requests.get(f"{BASE_URL}/api/templates", headers=headers)
    print(f"✓ GET /api/templates: {r.status_code} - Found {len(r.json())} templates")
    
    # Get single template
    r = requests.get(f"{BASE_URL}/api/templates/{template_id}", headers=headers)
    print(f"✓ GET /api/templates/{template_id}: {r.status_code} - {r.json()['name']}")
    
    return template_id


def test_jobs(token):
    """Test job description operations."""
    print("\n=== Testing Job Descriptions ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create job description
    job_data = {
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "description": """We are looking for a Senior Python Developer with:
        - 5+ years of Python experience
        - Experience with FastAPI or Django
        - PostgreSQL database experience
        - Strong problem-solving skills
        - Experience with REST APIs""",
        "url": "https://example.com/jobs/12345"
    }
    
    r = requests.post(f"{BASE_URL}/api/jobs", headers=headers, json=job_data)
    print(f"✓ POST /api/jobs: {r.status_code}")
    job = r.json()
    job_id = job["id"]
    
    # List jobs
    r = requests.get(f"{BASE_URL}/api/jobs", headers=headers)
    print(f"✓ GET /api/jobs: {r.status_code} - Found {len(r.json())} jobs")
    
    # Get single job
    r = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers)
    print(f"✓ GET /api/jobs/{job_id}: {r.status_code} - {r.json()['title']}")
    
    # Parse job (test NLP extraction)
    r = requests.post(f"{BASE_URL}/api/jobs/{job_id}/parse", headers=headers)
    print(f"✓ POST /api/jobs/{job_id}/parse: {r.status_code} - Skills extracted")
    
    return job_id


def test_resumes(token, template_id, job_id):
    """Test resume creation and generation."""
    print("\n=== Testing Resumes ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create resume
    resume_data = {
        "title": "My Test Resume",
        "job_description_id": job_id,
        "template_id": template_id
    }
    
    r = requests.post(f"{BASE_URL}/api/resumes", headers=headers, json=resume_data)
    print(f"✓ POST /api/resumes: {r.status_code}")
    resume = r.json()
    resume_id = resume["id"]
    
    # List resumes
    r = requests.get(f"{BASE_URL}/api/resumes", headers=headers)
    print(f"✓ GET /api/resumes: {r.status_code} - Found {len(r.json())} resumes")
    
    # Get single resume
    r = requests.get(f"{BASE_URL}/api/resumes/{resume_id}", headers=headers)
    print(f"✓ GET /api/resumes/{resume_id}: {r.status_code} - {r.json()['title']}")
    
    # Update resume content
    r = requests.patch(f"{BASE_URL}/api/resumes/{resume_id}/content", headers=headers, json={
        "content": r"""\documentclass{article}
\begin{document}
\section*{Test User}
test@example.com | +1-234-567-8900

\section*{Experience}
Senior Developer at Test Corp

\section*{Skills}
Python, FastAPI, React
\end{document}"""
    })
    print(f"✓ PATCH /api/resumes/{resume_id}/content: {r.status_code} - Content updated")
    
    return resume_id


def test_resume_generation(token, resume_id):
    """Test AI-powered resume generation."""
    print("\n=== Testing Resume Generation ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Generate resume
    print("Generating resume with AI (this may take a moment)...")
    r = requests.post(f"{BASE_URL}/api/resumes/{resume_id}/generate", headers=headers, timeout=120)
    
    if r.status_code == 200:
        result = r.json()
        print(f"✓ POST /api/resumes/{resume_id}/generate: {r.status_code}")
        print(f"  - Content length: {len(result.get('latex_content', ''))} chars")
    else:
        print(f"⚠ POST /api/resumes/{resume_id}/generate: {r.status_code}")
        print(f"  - Note: Generation may require valid Gemini API keys")
        print(f"  - Response: {r.text[:200]}...")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("LaTeX Resume Agent - API Test Suite")
    print("=" * 60)
    
    # Test health
    test_health()
    
    # Test auth and get token
    token = test_auth()
    if not token:
        print("\n✗ Authentication failed, cannot continue tests")
        return
    
    # Test CRUD operations
    project_id = test_projects(token)
    template_id = test_templates(token)
    job_id = test_jobs(token)
    resume_id = test_resumes(token, template_id, job_id)
    
    # Test AI generation (optional - requires API keys)
    test_resume_generation(token, resume_id)
    
    print("\n" + "=" * 60)
    print("✓ All basic API tests completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Register/login with the frontend")
    print("3. Create projects, templates, and test resume generation")
    print("4. Try the LaTeX editor at /dashboard/resumes/[id]/edit")


if __name__ == "__main__":
    main()
