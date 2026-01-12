import sqlite3

conn = sqlite3.connect('latex_agent.db')
cursor = conn.cursor()

# Get the system template
cursor.execute("""
    SELECT latex_content 
    FROM templates 
    WHERE is_system = 1
    LIMIT 1
""")

result = cursor.fetchone()
if result:
    print("=== SYSTEM TEMPLATE LATEX CONTENT ===")
    print(result[0])
else:
    print("No system template found")

conn.close()
