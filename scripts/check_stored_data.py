#!/usr/bin/env python3
"""Check stored resume data in database"""

import sqlite3
import json

db_path = "d:/Projects/latex-agent/backend/latex_agent.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all profile fields for the user
cursor.execute("""
    SELECT 
        name, email, phone, location,
        city, state, zip_code, country,
        address_line1, address_line2,
        headline, summary,
        institution, degree, field_of_study, graduation_year,
        linkedin_url, website, skills
    FROM users 
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()

if row:
    fields = [
        'name', 'email', 'phone', 'location',
        'city', 'state', 'zip_code', 'country',
        'address_line1', 'address_line2',
        'headline', 'summary',
        'institution', 'degree', 'field_of_study', 'graduation_year',
        'linkedin_url', 'website', 'skills'
    ]
    
    print("=" * 70)
    print("📊 Stored Profile Data (from users table)")
    print("=" * 70)
    
    for i, field in enumerate(fields):
        value = row[i]
        if value:
            if field == 'skills' and value:
                try:
                    skills = json.loads(value)
                    print(f"{field:20} {', '.join(skills[:5])}")
                except:
                    print(f"{field:20} {value}")
            else:
                print(f"{field:20} {value[:60] if len(str(value)) > 60 else value}")
    
    print("\n" + "=" * 70)
    print("✅ Data is stored in SQLite database at:")
    print(f"   {db_path}")
    print("\n💡 You can now edit this via:")
    print("   - GET  /api/auth/profile (view)")
    print("   - PUT  /api/auth/profile (edit)")
    print("=" * 70)
else:
    print("No user data found in database")

conn.close()
