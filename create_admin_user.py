import sqlite3
from werkzeug.security import generate_password_hash

def create_admin():
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Create admin user
        username = 'admin'
        password = 'admin123'  # Change this to a strong password in production
        hashed_password = generate_password_hash(password)
        
        # Insert admin user
        cursor.execute('''
        INSERT OR REPLACE INTO users (username, password, full_name, email, role)
        VALUES (?, ?, ?, ?, ?)
        ''', (username, hashed_password, 'Administrator', 'admin@example.com', 'admin'))
        
        conn.commit()
        conn.close()
        
        print(f"Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("\nPlease change this password after logging in!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Creating Admin User ===\n")
    create_admin()
