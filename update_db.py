import sqlite3
import os

def update_database():
    # Backup existing database
    if os.path.exists('database.db'):
        if os.path.exists('database.db.bak'):
            os.remove('database.db.bak')
        os.rename('database.db', 'database.db.bak')
        print("Created backup of existing database as 'database.db.bak'")
    
    # Read schema and execute it
    with open('schema.sql', 'r') as f:
        schema = f.read()
    
    conn = sqlite3.connect('database.db')
    conn.executescript(schema)
    conn.close()
    
    print("Database schema updated successfully!")

if __name__ == '__main__':
    update_database()
