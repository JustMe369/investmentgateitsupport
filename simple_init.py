import sqlite3
import os
from werkzeug.security import generate_password_hash

def create_database():
    # Remove existing database if it exists
    if os.path.exists('database.db'):
        os.remove('database.db')
    
    # Create a new database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert test users
    test_users = [
        ('admin', 'admin123', 'Admin User', 'admin@example.com', 'admin'),
        ('tech', 'tech123', 'Tech User', 'tech@example.com', 'technician'),
        ('user1', 'user123', 'Regular User', 'user1@example.com', 'user')
    ]
    
    for username, password, full_name, email, role in test_users:
        try:
            cursor.execute(
                'INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)',
                (username, generate_password_hash(password), full_name, email, role)
            )
            print(f"Created user: {username}")
        except sqlite3.IntegrityError:
            print(f"User {username} already exists")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    create_database()
