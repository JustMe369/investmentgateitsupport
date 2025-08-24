import sqlite3
from werkzeug.security import generate_password_hash

def setup_database():
    try:
        # Connect to SQLite database (will create if it doesn't exist)
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
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
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            # Create admin user
            hashed_password = generate_password_hash('admin123')
            cursor.execute('''
            INSERT INTO users (username, password, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
            ''', ('admin', hashed_password, 'Administrator', 'admin@example.com', 'admin'))
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Admin user already exists in the database.")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("=== Setting up database and admin user ===\n")
    setup_database()
    print("\nPlease try logging in with the admin credentials provided above.")
