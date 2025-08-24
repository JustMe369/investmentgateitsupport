import os
import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    # Remove existing database if it exists
    if os.path.exists('database.db'):
        os.remove('database.db')
    
    # Create a new database and initialize schema
    conn = sqlite3.connect('database.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    # Create admin user
    cursor = conn.cursor()
    username = 'admin'
    password = 'admin123'  # Change this to a strong password in production
    hashed_password = generate_password_hash(password)
    
    cursor.execute(
        'INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)',
        (username, hashed_password, 'Administrator', 'admin@example.com', 'admin')
    )
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")
    print(f"Admin credentials - Username: {username}, Password: {password}")

if __name__ == "__main__":
    init_db()
