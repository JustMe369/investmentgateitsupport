import sqlite3
import sys

def check_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_table = cursor.fetchone()
        
        if not users_table:
            print("Error: 'users' table does not exist in the database.")
            print("\nAvailable tables:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for table in cursor.fetchall():
                print(f"- {table['name']}")
            return
        
        # Get users table schema
        print("\nUsers table schema:")
        cursor.execute("PRAGMA table_info(users)")
        for column in cursor.fetchall():
            print(f"- {column['name']} ({column['type']})")
        
        # Get user count
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        print(f"\nTotal users: {user_count}")
        
        if user_count > 0:
            # Get first 5 users (without passwords)
            print("\nFirst 5 users (password hashes are truncated):")
            cursor.execute("SELECT id, username, role, substr(password, 1, 10) || '...' as password_hash FROM users LIMIT 5")
            for user in cursor.fetchall():
                print(f"- ID: {user['id']}, Username: {user['username']}, Role: {user['role']}, Password Hash: {user['password_hash']}")
        
        # Check if there's an admin user
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()['count']
        print(f"\nAdmin users: {admin_count}")
        
        if admin_count == 0:
            print("\nWARNING: No admin user found in the database!")
            print("You can create an admin user by running the following SQL:")
            print("""
            INSERT INTO users (username, password, role, full_name, email, created_at)
            VALUES ('admin', 'pbkdf2:sha256:...', 'admin', 'Admin User', 'admin@example.com', datetime('now'));
            """)
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Database Debug Information ===\n")
    check_database()
