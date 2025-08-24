import os
import sqlite3

def check_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    print(f"Database path: {db_path}")
    
    # Check if file exists and is accessible
    if not os.path.exists(db_path):
        print("Error: database file does not exist!")
        return False
    
    try:
        # Check file permissions
        if not os.access(db_path, os.R_OK | os.W_OK):
            print("Error: insufficient permissions to access the database file!")
            return False
            
        # Try to connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("\nSuccessfully connected to the database!")
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\nTables in database:")
        for table in tables:
            print(f"- {table}")
        
        # Check users table
        if 'users' in tables:
            print("\nUsers table columns:")
            cursor.execute("PRAGMA table_info(users)")
            for col in cursor.fetchall():
                print(f"- {col[1]} ({col[2]})")
            
            # Check admin user
            print("\nAdmin users:")
            cursor.execute("SELECT id, username, role FROM users WHERE role = 'admin'")
            admins = cursor.fetchall()
            if admins:
                for admin in admins:
                    print(f"- ID: {admin[0]}, Username: {admin[1]}, Role: {admin[2]}")
            else:
                print("No admin users found!")
        
        # Check for required tables
        required_tables = ['users', 'locations', 'equipment', 'tickets']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"\nMissing required tables: {', '.join(missing_tables)}")
            return False
            
        return True
        
    except sqlite3.Error as e:
        print(f"\nDatabase error: {e}")
        return False
    except Exception as e:
        print(f"\nError: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Database Verification ===\n")
    if check_database():
        print("\nDatabase verification completed successfully!")
    else:
        print("\nDatabase verification failed. Please check the errors above.")
