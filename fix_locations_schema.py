import sqlite3
import os
from datetime import datetime

def fix_locations_schema():
    db_path = 'database.db'
    backup_path = f'database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    # Create a backup of the database
    print(f"Creating backup at {backup_path}...")
    try:
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        print("Backup created successfully!")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the current table info
        cursor.execute('PRAGMA table_info(locations)')
        columns = [col[1] for col in cursor.fetchall()]
        
        print("Current columns in locations table:", columns)
        
        # Check if we need to fix the schema
        required_columns = ['id', 'name', 'address', 'contact_person', 'contact_phone', 'anydesk_id', 'created_at']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if not missing_columns:
            print("Schema is already correct. No changes needed.")
            return
            
        print(f"Missing columns: {missing_columns}")
        print("Fixing schema...")
        
        # Create a new table with the correct schema
        cursor.execute('''
        CREATE TABLE locations_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            anydesk_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Copy data from the old table to the new one
        cursor.execute('''
        INSERT INTO locations_new (
            id, name, address, contact_person, contact_phone, anydesk_id, created_at
        )
        SELECT 
            id, 
            COALESCE(name, 'Unnamed Location'),
            COALESCE(address, 'No address'),
            COALESCE(contact_person, 'No contact'),
            COALESCE(contact_phone, 'N/A'),
            anydesk_id,
            COALESCE(created_at, CURRENT_TIMESTAMP)
        FROM locations
        ''')
        
        # Drop the old table and rename the new one
        cursor.execute('DROP TABLE locations')
        cursor.execute('ALTER TABLE locations_new RENAME TO locations')
        
        # Commit the changes
        conn.commit()
        print("Schema updated successfully!")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    fix_locations_schema()
