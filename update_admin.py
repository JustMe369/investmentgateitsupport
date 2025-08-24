import sqlite3

def make_user_admin():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    
    # Set the first user as admin
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'admin' WHERE id = 1")
    conn.commit()
    
    # Verify the update
    user = conn.execute("SELECT username, role FROM users WHERE id = 1").fetchone()
    print(f"Updated user {user['username']} to role: {user['role']}")
    
    conn.close()

if __name__ == "__main__":
    make_user_admin()
