import sqlite3
import os

def check_table(conn, table_name):
    cursor = conn.cursor()
    print(f"\n=== {table_name.upper()} TABLE ===")
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        print(f"Error: '{table_name}' table does not exist in the database.")
        return False
    
    # Get table schema
    print("\nTable schema:")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for column in columns:
        print(f"- {column[1]} ({column[2]})")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"\nTotal rows: {row_count}")
    
    # Get sample data
    if row_count > 0:
        print("\nSample data (first 5 rows):")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        for i, row in enumerate(rows, 1):
            print(f"\nRow {i}:")
            for col in zip([desc[0] for desc in cursor.description], row):
                print(f"  {col[0]}: {col[1]}")
    
    return True

def check_database():
    db_path = 'database.db'
    if not os.path.exists(db_path):
        print("Error: database.db file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Get list of all tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("\n=== DATABASE OVERVIEW ===")
        print(f"Database: {os.path.abspath(db_path)}")
        print(f"Tables: {', '.join(tables)}\n")
        
        # Check important tables
        for table in ['users', 'locations', 'equipment', 'tickets', 'ticket_comments']:
            check_table(conn, table)
        
        # Check foreign key relationships
        print("\n=== FOREIGN KEY RELATIONSHIPS ===")
        cursor.execute("""
            SELECT m.name as table_name, 
                   p."from" as column_name, 
                   p."table" as references_table,
                   p."to" as references_column
            FROM sqlite_master m
            JOIN pragma_foreign_key_list(m.name) p ON m.name != p."table"
            WHERE m.type = 'table'
            ORDER BY m.name, p.id
        """)
        fks = cursor.fetchall()
        if fks:
            for fk in fks:
                print(f"{fk['table_name']}.{fk['column_name']} -> {fk['references_table']}.{fk['references_column']}")
        else:
            print("No foreign key relationships found.")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Database Check ===\n")
    if check_database():
        print("\nDatabase check completed successfully!")
