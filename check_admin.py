import sqlite3

def check_and_update_admin():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    
    # Get all users
    users = conn.execute('SELECT id, username, role FROM users').fetchall()
    
    print("Current users:")
    print("ID | Username | Role")
    print("-------------------")
    for user in users:
        print(f"{user['id']} | {user['username']} | {user['role']}")
    
    # Check if any admin exists
    admin_exists = any(user['role'] == 'admin' for user in users)
    
    if not admin_exists and users:
        print("\nNo admin user found. Would you like to make a user an admin?")
        user_id = input("Enter user ID to make admin (or press Enter to skip): ")
        
        if user_id.strip():
            try:
                user_id = int(user_id)
                if any(user['id'] == user_id for user in users):
                    conn.execute('UPDATE users SET role = ? WHERE id = ?', ('admin', user_id))
                    conn.commit()
                    print(f"User ID {user_id} has been given admin privileges.")
                else:
                    print("Invalid user ID.")
            except ValueError:
                print("Please enter a valid number.")
    
    conn.close()

if __name__ == "__main__":
    check_and_update_admin()
