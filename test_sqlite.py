import sqlite3
import os

def test_sqlite():
    # Create a new database file
    db_path = 'test_simple.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a simple table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        ''')
        
        # Insert some test data
        cursor.execute("INSERT INTO test (name) VALUES ('test1')")
        cursor.execute("INSERT INTO test (name) VALUES ('test2')")
        
        # Commit changes
        conn.commit()
        
        # Query the data
        cursor.execute("SELECT * FROM test")
        rows = cursor.fetchall()
        
        print("Test successful!")
        print("Data in test table:")
        for row in rows:
            print(f"- {row[0]}: {row[1]}")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Testing SQLite database...\n")
    if test_sqlite():
        print("\nSQLite test completed successfully!")
    else:
        print("\nSQLite test failed.")
