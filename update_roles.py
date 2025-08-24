import sqlite3
from werkzeug.security import generate_password_hash

def update_roles():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check if any users have the 'opentickets' role
        cursor.execute("SELECT id, username, role FROM users WHERE role = 'opentickets'")
        existing = cursor.fetchall()
        
        if existing:
            print("Users with 'opentickets' role:")
            for user in existing:
                print(f"ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")
        else:
            print("No users currently have the 'opentickets' role.")
        
        # Update the add_user.html template to include the new role
        try:
            with open('templates/add_user.html', 'r+', encoding='utf-8') as f:
                content = f.read()
                if 'opentickets' not in content:
                    # Add the new role option before the closing select tag
                    updated_content = content.replace(
                        '<option value="technician">Technician</option>',
                        '<option value="technician">Technician</option>\n                                <option value="opentickets">Open Tickets Only</option>'
                    )
                    f.seek(0)
                    f.write(updated_content)
                    f.truncate()
                    print("\nUpdated add_user.html to include the 'Open Tickets Only' role option.")
                else:
                    print("\n'Open Tickets Only' role already exists in add_user.html")
        except Exception as e:
            print(f"\nError updating add_user.html: {e}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_roles()
