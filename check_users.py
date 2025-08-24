import sqlite3

def check_users():
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Error: 'users' table does not exist in the database.")
            return
            
        # Get all users
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
        else:
            print("\nUsers in database:")
            print("-" * 50)
            print(f"{'ID':<5} | {'Username':<20} | {'Role'}")
            print("-" * 50)
            for user in users:
                print(f"{user['id']:<5} | {user['username']:<20} | {user['role']}")
            print("-" * 50)
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Checking database and users...\n")
    check_users()
