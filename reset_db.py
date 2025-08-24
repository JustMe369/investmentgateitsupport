import os
import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    # Delete existing database if it exists
    if os.path.exists('database.db'):
        os.remove('database.db')
    
    # Create a new database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Read and execute the schema
    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())
    
    # Create test users
    users = [
        ('admin', 'admin123', 'Admin User', 'admin@example.com', 'admin'),
        ('tech1', 'tech123', 'John Doe', 'tech1@example.com', 'technician'),
        ('user1', 'user123', 'Jane Smith', 'user1@example.com', 'user')
    ]
    
    for username, password, full_name, email, role in users:
        cursor.execute(
            'INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)',
            (username, generate_password_hash(password), full_name, email, role)
        )
    
    conn.commit()
    conn.close()
    print("Database reset and initialized successfully!")

if __name__ == '__main__':
    init_db()
