"""Test profile endpoint directly"""
import sqlite3
import json

# Connect to database
db_path = "d:/Projects/latex-agent/backend/latex_agent.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all users
cursor.execute("""
SELECT id, email, name, headline, summary, location, phone, 
       institution, degree, field_of_study, graduation_year, 
       city, state, skills
FROM users
""")

users = cursor.fetchall()

print("=" * 80)
print("ALL USERS IN DATABASE:")
print("=" * 80)

for user in users:
    user_id, email, name, headline, summary, location, phone, institution, degree, field, grad_year, city, state, skills = user
    print(f"\nUser ID: {user_id}")
    print(f"Email: {email}")
    print(f"Name: {name}")
    print(f"Headline: {headline}")
    print(f"Location: {location}")
    print(f"Phone: {phone}")
    print(f"Education: {institution}, {degree} in {field}, {grad_year}")
    print(f"City/State: {city}, {state}")
    if skills:
        try:
            skills_list = json.loads(skills)
            print(f"Skills ({len(skills_list)}): {', '.join(skills_list[:5])}...")
        except:
            print(f"Skills: {skills[:100]}...")
    print("-" * 80)

conn.close()

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("1. Make sure you're logged in (check localStorage for 'token')")
print("2. Open browser console (F12) and check for errors")
print("3. The API endpoint is: GET http://localhost:8000/api/auth/profile")
print("4. Check if backend shows any requests when you click Profile")
