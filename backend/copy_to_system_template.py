import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect('latex_agent.db')
cursor = conn.cursor()

# Get Hiruthik's base_template
cursor.execute("""
    SELECT name, description, latex_content, category 
    FROM templates 
    WHERE user_id = 'f8bcae44-85f5-40c6-bf28-a49d34ca1a6c' 
    AND name = 'base_template'
""")

template = cursor.fetchone()

if template:
    name, description, latex_content, category = template
    
    # Insert as system template
    new_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO templates (
            id, user_id, name, description, latex_content, 
            category, is_system, is_ats_tested, is_public, use_count, placeholders,
            created_at, updated_at
        ) VALUES (?, NULL, ?, ?, ?, ?, 1, 1, 1, 0, '[]', ?, ?)
    """, (new_id, name, description, latex_content, category, now, now))
    
    conn.commit()
    print(f"Created system template: {name}")
    print(f"  ID: {new_id}")
    print(f"  Description: {description}")
else:
    print("Template not found")

conn.close()
