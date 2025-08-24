import sqlite3

def check_and_fix_comments_table():
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='ticket_comments'
        """)
        
        if not cursor.fetchone():
            print("Creating ticket_comments table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ticket_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES tickets (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            print("Created ticket_comments table successfully!")
        else:
            print("ticket_comments table already exists")
            
        # Verify table structure
        cursor.execute("PRAGMA table_info(ticket_comments)")
        print("\nTable structure:")
        for col in cursor.fetchall():
            print(f"- {col[1]}: {col[2]}")
            
        conn.commit()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("Checking and fixing ticket_comments table...")
    check_and_fix_comments_table()
    input("\nPress Enter to exit...")
