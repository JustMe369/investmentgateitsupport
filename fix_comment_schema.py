import sqlite3
import os
from datetime import datetime

def backup_database():
    """Create a backup of the current database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f'database_backup_{timestamp}.db'
    
    if os.path.exists('database.db'):
        with open('database.db', 'rb') as src, open(backup_file, 'wb') as dst:
            dst.write(src.read())
        print(f"Created backup: {backup_file}")
    else:
        print("No database file found to backup")

def check_comments_table():
    """Check and fix the ticket_comments table schema"""
    conn = None
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
                CREATE TABLE ticket_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES tickets (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            print("✅ Created ticket_comments table")
        else:
            print("ℹ️ ticket_comments table exists")
            
        # Verify table structure
        cursor.execute("PRAGMA table_info(ticket_comments)")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"- {col[1]}: {col[2]}")
            
        # Check foreign key constraints
        cursor.execute("PRAGMA foreign_key_check;")
        fk_issues = cursor.fetchall()
        if fk_issues:
            print("\n⚠️ Foreign key issues found:")
            for issue in fk_issues:
                print(f"- {issue}")
        else:
            print("\n✅ No foreign key issues found")
            
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def main():
    print("🔍 Starting database check...")
    backup_database()
    check_comments_table()
    print("\n✅ Database check complete!")

if __name__ == '__main__':
    main()
