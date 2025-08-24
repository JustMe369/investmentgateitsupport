@echo off
echo Attempting to fix database issues...

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
) else (
    echo Please run this script as Administrator!
    pause
    exit /b 1
)

:: Change to the script directory
cd /d "%~dp0"

:: Remove existing database if it exists
if exist database.db (
    echo Removing existing database file...
    del /f /q database.db
)

:: Create a new database with a simple schema
echo Creating new database...
echo ""

:: Run Python script to initialize database
python -c "
import sqlite3
from werkzeug.security import generate_password_hash

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

# Commit changes and close connection
conn.commit()
conn.close()

print('\nDatabase initialized successfully!')
print('Admin user created:')
print(f'Username: admin')
print(f'Password: {admin_password}')
"

echo ""
echo Please try logging in with the admin credentials shown above.
pause
