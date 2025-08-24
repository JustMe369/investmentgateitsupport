import os
import sqlite3

def check_database():
    db_path = 'test_database.db'
    print(f"Checking database at: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("Error: Database file does not exist")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Error: 'users' table not found")
            return False
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print("\nTables in database:")
        for table in cursor.fetchall():
            print(f"- {table[0]}")
        
        # Get users
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        
        print("\nUsers in database:")
        for user in users:
            print(f"- ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Database Check ===\n")
    if check_database():
        print("\nDatabase check completed successfully!")
    else:
        print("\nDatabase check failed.")
