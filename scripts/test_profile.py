"""Test the profile endpoints"""
import requests
import json

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"

# Test getting profile (needs JWT token from your session)
print("To test the profile endpoints:")
print("1. GET /api/auth/profile - View your profile")
print("2. PUT /api/auth/profile - Update profile fields")
print()
print("Example curl commands:")
print()
print("# Get profile:")
print('curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/auth/profile')
print()
print("# Update profile:")
print('curl -X PUT -H "Authorization: Bearer YOUR_JWT_TOKEN" -H "Content-Type: application/json" \\')
print('  -d \'{"name": "New Name", "phone": "+91-1234567890"}\' \\')
print('  http://localhost:8000/api/auth/profile')
print()
print("Your data is stored in: d:/Projects/latex-agent/backend/latex_agent.db")
print("Table: users")
print()
print("Extracted fields from your resume:")
fields = [
    "name", "headline", "summary", "location", "phone", 
    "city", "state", "country", "zip_code",
    "address_line1", "address_line2",
    "institution", "degree", "field_of_study", "graduation_year",
    "linkedin_url", "website", "skills"
]
for field in fields:
    print(f"  - {field}")
