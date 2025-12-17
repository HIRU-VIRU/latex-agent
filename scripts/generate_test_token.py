"""
Test script to verify profile API endpoint is working
"""
import sqlite3
import jwt
from datetime import datetime, timedelta

# Database path
db_path = r"d:\Projects\latex-agent\backend\latex_agent.db"

# Get user ID for Hiruthik
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, email FROM users WHERE email = 'xmyhiruthik2020@gmail.com'")
result = cursor.fetchone()
conn.close()

if not result:
    print("❌ User not found!")
    exit(1)

user_id = result[0]
email = result[1]

print(f"✅ Found user: {email}")
print(f"User ID: {user_id}")

# Create a JWT token manually for testing
SECRET_KEY = "your-secret-key-here-change-in-production"  # From backend .env
ALGORITHM = "HS256"

payload = {
    "sub": user_id,
    "exp": datetime.utcnow() + timedelta(days=7)
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(f"\n🔑 Test JWT Token:")
print(token)

print(f"\n📋 To test in browser:")
print(f"1. Open browser console (F12)")
print(f"2. Run: localStorage.setItem('token', '{token}')")
print(f"3. Reload the page")
print(f"4. Go to Profile tab")

print(f"\n🧪 Or test with curl:")
print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/auth/profile')
