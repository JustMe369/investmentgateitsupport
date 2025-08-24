import os
import sqlite3
from werkzeug.security import generate_password_hash

def init_database():
    db_path = 'database.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Removed existing database file.")
        except Exception as e:
            print(f"Error removing database file: {e}")
    
    try:
        # Create a new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Created new database successfully.")
        
        # Create tables
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
        
        cursor.execute('''
        CREATE TABLE locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            anydesk_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_type TEXT NOT NULL,
            model TEXT NOT NULL,
            serial_number TEXT UNIQUE NOT NULL,
            location_id INTEGER,
            ip_address TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            installation_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            priority TEXT NOT NULL DEFAULT 'Medium',
            created_by INTEGER NOT NULL,
            assigned_to INTEGER,
            location_id INTEGER,
            equipment_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (assigned_to) REFERENCES users (id),
            FOREIGN KEY (location_id) REFERENCES locations (id),
            FOREIGN KEY (equipment_id) REFERENCES equipment (id)
        )
        ''')
        
        # Create admin user
        admin_password = 'admin123'  # Change this in production!
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute('''
        INSERT INTO users (username, password, full_name, email, role)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hashed_password, 'Administrator', 'admin@example.com', 'admin'))
        
        # Create a sample location
        cursor.execute('''
        INSERT INTO locations (name, address, contact_person, contact_phone, anydesk_id)
        VALUES (?, ?, ?, ?, ?)
        ''', ('Main Office', '123 Main St', 'John Doe', '123-456-7890', '123456789'))
        
        conn.commit()
        print("\nDatabase initialized successfully!")
        print("Admin user created:")
        print(f"Username: admin")
        print(f"Password: {admin_password}")
        print("\nPlease change the password after logging in!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Authentication System Fix ===\n")
    print("This will reset the database and create a new admin user.")
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    init_database()
    
    print("\n=== Fix Complete ===")
    print("1. The database has been recreated")
    print("2. All tables have been created")
    print("3. Admin user has been created")
    print("\nYou can now try logging in with the admin credentials.")
