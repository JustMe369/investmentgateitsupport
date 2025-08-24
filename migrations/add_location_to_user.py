import sqlite3
import os

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_location_to_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if location_id column exists in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'location_id' not in columns:
            # Add location_id column to users table
            cursor.execute('''
                ALTER TABLE users 
                ADD COLUMN location_id INTEGER 
                REFERENCES locations(id) ON DELETE SET NULL
            ''')
            conn.commit()
            print("Successfully added location_id column to users table")
            
            # If you want to set a default location for existing users, uncomment and modify this:
            # cursor.execute('''
            #     UPDATE users 
            #     SET location_id = (SELECT id FROM locations LIMIT 1)
            #     WHERE location_id IS NULL
            # ''')
            # conn.commit()
            # print("Set default location for existing users")
            
        else:
            print("location_id column already exists in users table")
            
    except Exception as e:
        print(f"Error adding location_id to users table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_location_to_user()
