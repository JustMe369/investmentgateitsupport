import os
import sqlite3

def init_database():
    # Remove existing database if it exists
    if os.path.exists('database.db'):
        os.remove('database.db')
    
    # Create a new database and initialize schema
    conn = sqlite3.connect('database.db')
    print("Database created successfully!")
    
    # Read and execute the SQL script
    with open('init_db.sql', 'r') as f:
        sql_script = f.read()
    
    try:
        conn.executescript(sql_script)
        conn.commit()
        print("Database schema created successfully!")
    except Exception as e:
        print(f"Error creating database schema: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    if init_database():
        print("""
        Database initialization complete!
        
        You can now log in with the following credentials:
        Username: admin
        Password: admin123
        
        Please change the password after your first login.
        """)
    else:
        print("Failed to initialize database. Please check the error message above.")
