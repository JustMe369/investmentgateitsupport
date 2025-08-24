import os
import sqlite3
from werkzeug.security import generate_password_hash

def create_test_db():
    # Remove existing database if it exists
    db_path = 'test_database.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create a new database
    conn = sqlite3.connect(db_path)
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
    
    # Insert test users
    test_users = [
        ('admin', 'admin123', 'Admin User', 'admin@example.com', 'admin'),
        ('tech', 'tech123', 'Tech User', 'tech@example.com', 'technician'),
        ('user1', 'user123', 'Regular User', 'user1@example.com', 'user')
    ]
    
    for username, password, full_name, email, role in test_users:
        cursor.execute(
            'INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)',
            (username, generate_password_hash(password), full_name, email, role)
        )
    
    conn.commit()
    conn.close()
    print(f"Test database created at: {os.path.abspath(db_path)}")
    print("Test users created:")
    print("- admin/admin123 (admin)")
    print("- tech/tech123 (technician)")
    print("- user1/user123 (user)")

if __name__ == '__main__':
    create_test_db()
