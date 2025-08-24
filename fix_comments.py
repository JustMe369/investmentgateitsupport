import sqlite3
import os

def check_and_fix_table():
    try:
        # Connect to the database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ticket_comments'")
        if not cursor.fetchone():
            print("Creating missing 'ticket_comments' table...")
            cursor.execute('''
                CREATE TABLE ticket_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()
            print("Successfully created 'ticket_comments' table")
        else:
            print("'ticket_comments' table already exists")
            
            # Verify table structure
            cursor.execute("PRAGMA table_info(ticket_comments)")
            columns = [col[1] for col in cursor.fetchall()]
            print("\nTable columns:", ", ".join(columns))
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("Checking and fixing 'ticket_comments' table...")
    check_and_fix_table()
    input("\nPress Enter to exit...")
