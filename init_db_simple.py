import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_db():
    # Remove existing database if it exists
    if os.path.exists('database.db'):
        try:
            os.remove('database.db')
            print("Removed existing database file.")
        except Exception as e:
            print(f"Error removing database file: {e}")
    
    try:
        # Create a new database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create admin user
        admin_password = 'admin123'  # Change this in production!
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute('''
        INSERT INTO users (username, password, full_name, email, role)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hashed_password, 'Administrator', 'admin@example.com', 'admin'))
        
        conn.commit()
        print("\nDatabase initialized successfully!")
        print("Admin user created:")
        print(f"Username: admin")
        print(f"Password: {admin_password}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Initializing Database ===\n")
    init_db()
