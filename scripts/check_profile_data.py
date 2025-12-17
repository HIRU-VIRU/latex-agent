"""Check current user's profile data"""
import sys
sys.path.insert(0, 'd:/Projects/latex-agent/backend')

import sqlite3
import json

# Connect to database
db_path = "d:/Projects/latex-agent/backend/latex_agent.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the most recent user (likely the one you're logged in as)
cursor.execute("""
SELECT 
    email, name, headline, summary, phone, location,
    institution, degree, field_of_study, graduation_year,
    city, state, skills, updated_at
FROM users 
ORDER BY updated_at DESC 
LIMIT 3
""")

users = cursor.fetchall()

print("\n" + "="*100)
print("RECENT USERS (sorted by last update):")
print("="*100)

for i, row in enumerate(users, 1):
    email, name, headline, summary, phone, location, institution, degree, field, grad_year, city, state, skills, updated = row
    
    print(f"\n{i}. {email}")
    print(f"   Name: {name}")
    print(f"   Headline: {headline if headline else 'NOT SET'}")
    print(f"   Phone: {phone if phone else 'NOT SET'}")
    print(f"   Location: {location if location else 'NOT SET'}")
    print(f"   Education: {institution if institution else 'NOT SET'}")
    print(f"   Last Updated: {updated}")
    
    if skills:
        try:
            skills_list = json.loads(skills)
            print(f"   Skills: {len(skills_list)} skills - {', '.join(skills_list[:3])}...")
        except:
            print(f"   Skills: {skills[:50]}...")
    else:
        print(f"   Skills: NOT SET")
    
    print("   " + "-"*90)

conn.close()

print("\n" + "="*100)
print("If your profile shows 'NOT SET', the resume upload did not work.")
print("Check browser console for errors during upload.")
print("="*100)
