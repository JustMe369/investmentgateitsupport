import os
import sqlite3
from datetime import datetime

def init_fresh_db():
    db_path = 'database.db'
    
    # Backup existing database if it exists
    if os.path.exists(db_path):
        backup_path = f'database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        print(f"Backing up existing database to {backup_path}...")
        try:
            with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            print("Backup created successfully!")
        except Exception as e:
            print(f"Error creating backup: {e}")
            return
    
    try:
        # Connect to the database (this will create it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.executescript('''
        DROP TABLE IF EXISTS ticket_comments;
        DROP TABLE IF EXISTS tickets;
        DROP TABLE IF EXISTS equipment;
        DROP TABLE IF EXISTS locations;
        DROP TABLE IF EXISTS users;
        
        -- Users table
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Locations table
        CREATE TABLE locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            anydesk_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Equipment table
        CREATE TABLE equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            serial_number TEXT,
            location_id INTEGER,
            status TEXT NOT NULL DEFAULT 'Operational',
            purchase_date DATE,
            last_maintenance DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        );
        
        -- Tickets table
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
        );
        
        -- Ticket Comments table
        CREATE TABLE ticket_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        -- Create admin user
        cursor.execute('''
        INSERT INTO users (username, password, full_name, email, role)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'pbkdf2:sha256:260000$eQh5y3Z2$...', 'Admin User', 'admin@example.com', 'admin'))
        
        # Commit the changes
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_fresh_db()
