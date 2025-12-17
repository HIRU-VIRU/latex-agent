"""Delete all users except one"""
import sqlite3

# Connect to database
db_path = "d:/Projects/latex-agent/backend/latex_agent.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT id, email, name FROM users")
users = cursor.fetchall()

print("\n" + "="*80)
print("CURRENT USERS:")
print("="*80)
for i, (user_id, email, name) in enumerate(users, 1):
    print(f"{i}. {email} - {name} (ID: {user_id})")

print("\n" + "="*80)
print("Which user do you want to KEEP? (Enter number)")
print("="*80)
choice = input("Enter number (1-{}): ".format(len(users)))

try:
    choice_idx = int(choice) - 1
    if 0 <= choice_idx < len(users):
        keep_user_id = users[choice_idx][0]
        keep_email = users[choice_idx][1]
        
        print(f"\nKeeping user: {keep_email}")
        print("Deleting all other users...")
        
        # Delete related data first (foreign key constraints)
        cursor.execute("DELETE FROM github_connections WHERE user_id != ?", (keep_user_id,))
        cursor.execute("DELETE FROM projects WHERE user_id != ?", (keep_user_id,))
        cursor.execute("DELETE FROM resumes WHERE user_id != ?", (keep_user_id,))
        cursor.execute("DELETE FROM job_descriptions WHERE user_id != ?", (keep_user_id,))
        cursor.execute("DELETE FROM documents WHERE user_id != ?", (keep_user_id,))
        
        # Delete the users
        cursor.execute("DELETE FROM users WHERE id != ?", (keep_user_id,))
        
        conn.commit()
        
        print("\n✓ Done! Remaining users:")
        cursor.execute("SELECT email, name FROM users")
        remaining = cursor.fetchall()
        for email, name in remaining:
            print(f"  - {email} ({name})")
        
    else:
        print("Invalid choice!")
except ValueError:
    print("Invalid input!")
finally:
    conn.close()
