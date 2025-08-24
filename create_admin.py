from werkzeug.security import generate_password_hash
import sqlite3

def create_admin():
    # Connect to the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create admin user
    username = 'admin'
    password = 'admin123'  # You should change this to a strong password
    hashed_password = generate_password_hash(password)
    
    try:
        cursor.execute(
            'INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)',
            (username, hashed_password, 'Administrator', 'admin@example.com', 'admin')
        )
        conn.commit()
        print(f"Admin user created successfully!\nUsername: {username}\nPassword: {password}")
    except sqlite3.IntegrityError:
        print("Admin user already exists!")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin()
