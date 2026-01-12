import sqlite3

conn = sqlite3.connect('latex_agent.db')
cursor = conn.cursor()

# Delete all system templates
cursor.execute('DELETE FROM templates WHERE is_system = 1')
deleted_system = cursor.rowcount

# Delete all other user templates except Hiruthik's base_template
cursor.execute("""
    DELETE FROM templates 
    WHERE user_id != 'f8bcae44-85f5-40c6-bf28-a49d34ca1a6c' 
    OR (user_id = 'f8bcae44-85f5-40c6-bf28-a49d34ca1a6c' AND name != 'base_template')
""")
deleted_other = cursor.rowcount

conn.commit()

print(f'Deleted {deleted_system} system template(s)')
print(f'Deleted {deleted_other} other template(s)')

# Show remaining templates
cursor.execute('SELECT name, user_id FROM templates')
remaining = cursor.fetchall()
print(f'\nRemaining templates: {len(remaining)}')
for r in remaining:
    print(f'  - {r[0]} (user_id: {r[1]})')

conn.close()
