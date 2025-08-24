import os
import sqlite3
from werkzeug.security import generate_password_hash

def test_database():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    print(f"Database path: {db_path}")
    
    try:
        # Check if database file exists
        if not os.path.exists(db_path):
            print("Database file does not exist. Creating new database...")
            
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Successfully connected to the database!")
        
        # Create users table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Create admin user
        username = 'admin'
        password = 'admin123'  # Change this in production!
        hashed_password = generate_password_hash(password)
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO users (username, password, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed_password, 'Administrator', 'admin@example.com', 'admin'))
            print("\nAdmin user created successfully!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print("\nPlease change this password after logging in!")
        else:
            print("\nAdmin user already exists in the database.")
        
        conn.commit()
        
        # List all users
        print("\nCurrent users in the database:")
        cursor.execute("SELECT id, username, role FROM users")
        for user in cursor.fetchall():
            print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    print("=== Database Test ===\n")
    test_db()
