import sqlite3

conn = sqlite3.connect('latex_agent.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM templates WHERE user_id = 'f8bcae44-85f5-40c6-bf28-a49d34ca1a6c'")
count = cursor.fetchone()[0]
print(f'Hiruthik Sudhakar has {count} template(s)')

cursor.execute("SELECT id, name, is_system FROM templates WHERE user_id = 'f8bcae44-85f5-40c6-bf28-a49d34ca1a6c'")
for row in cursor.fetchall():
    print(f'  - {row[1]} (ID: {row[0]}, System: {row[2]})')

conn.close()
