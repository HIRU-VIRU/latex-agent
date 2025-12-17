import sqlite3
import json

db_path = r"d:\Projects\latex-agent\backend\latex_agent.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get Hiruthik's full profile
cursor.execute("""
    SELECT 
        email, name, headline, summary, location, phone, 
        website, linkedin_url, 
        address_line1, address_line2, city, state, zip_code, country,
        institution, degree, field_of_study, graduation_year,
        skills
    FROM users 
    WHERE email = 'xmyhiruthik2020@gmail.com'
""")

result = cursor.fetchone()

if result:
    print("=== HIRUTHIK'S PROFILE DATA ===\n")
    print(f"Email: {result[0]}")
    print(f"Name: {result[1]}")
    print(f"Headline: {result[2]}")
    print(f"Summary: {result[3][:100] if result[3] else 'None'}...")
    print(f"Location: {result[4]}")
    print(f"Phone: {result[5]}")
    print(f"Website: {result[6]}")
    print(f"LinkedIn: {result[7]}")
    print(f"\nAddress Line 1: {result[8]}")
    print(f"Address Line 2: {result[9]}")
    print(f"City: {result[10]}")
    print(f"State: {result[11]}")
    print(f"Zip Code: {result[12]}")
    print(f"Country: {result[13]}")
    print(f"\nInstitution: {result[14]}")
    print(f"Degree: {result[15]}")
    print(f"Field of Study: {result[16]}")
    print(f"Graduation Year: {result[17]}")
    print(f"\nSkills (raw): {result[18]}")
    print(f"Skills type: {type(result[18])}")
    
    # Try to parse skills
    if result[18]:
        try:
            skills_data = json.loads(result[18])
            print(f"Skills parsed: {skills_data}")
            print(f"Skills count: {len(skills_data)}")
        except:
            print(f"Skills cannot be parsed as JSON")
else:
    print("User not found!")

conn.close()
