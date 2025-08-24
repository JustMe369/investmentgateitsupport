import sqlite3
import os
from datetime import datetime

def backup_database():
    """Create a timestamped backup of the current database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"database_backup_{timestamp}.db"
    try:
        with open('database.db', 'rb') as src, open(backup_name, 'wb') as dst:
            dst.write(src.read())
        print(f"Created backup: {backup_name}")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def create_database():
    """Create a new database with the latest schema"""
    try:
        # Backup existing database
        if os.path.exists('database.db'):
            if not backup_database():
                print("Failed to create backup. Aborting.")
                return False
        
        # Create new database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Read and execute schema
        with open('schema.sql', 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nCreated tables:")
        for table in tables:
            print(f"- {table[0]}")
        
        conn.commit()
        conn.close()
        
        print("\nDatabase created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == '__main__':
    print("=== Database Fix Tool ===\n")
    print("This will create a new database with the latest schema.")
    print("A backup of the current database will be created first.")
    
    confirm = input("\nDo you want to continue? (y/n): ").strip().lower()
    if confirm == 'y':
        if create_database():
            print("\nDatabase fix completed successfully!")
        else:
            print("\nFailed to fix the database. Please check the error messages above.")
    else:
        print("\nOperation cancelled.")
