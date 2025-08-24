import sqlite3

def check_locations():
    db_path = 'database.db'
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if locations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='locations'")
        if not cursor.fetchone():
            print("Error: 'locations' table does not exist in the database.")
            print("Please run the database initialization script to create the required tables.")
            return
        
        # Get table structure
        print("\nLocations table structure:")
        cursor.execute("PRAGMA table_info(locations)")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Count locations
        cursor.execute("SELECT COUNT(*) FROM locations")
        count = cursor.fetchone()[0]
        print(f"\nNumber of locations in database: {count}")
        
        # Show first few locations
        if count > 0:
            print("\nFirst 5 locations:")
            cursor.execute("SELECT * FROM locations LIMIT 5")
            for row in cursor.fetchall():
                print(row)
        
        # Check if there are any tickets with location_id
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE location_id IS NOT NULL")
        tickets_with_location = cursor.fetchone()[0]
        print(f"\nNumber of tickets with location_id: {tickets_with_location}")
        
        # Check if there are any equipment items
        cursor.execute("SELECT COUNT(*) FROM equipment")
        equipment_count = cursor.fetchone()[0]
        print(f"Number of equipment items: {equipment_count}")
        
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    check_locations()
