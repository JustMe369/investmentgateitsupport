import sqlite3

def add_opentickets_role():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # Check if any users already have the 'opentickets' role
        cursor.execute("SELECT id, username, role FROM users WHERE role = 'opentickets'")
        existing = cursor.fetchall()
        
        if existing:
            print("Users with 'opentickets' role already exist:")
            for user in existing:
                print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
        else:
            print("No users currently have the 'opentickets' role.")
            
        # Ask if we should add a new user with this role
        add_new = input("\nWould you like to create a new user with 'opentickets' role? (y/n): ").lower()
        
        if add_new == 'y':
            username = input("Enter username: ")
            password = input("Enter password: ")
            full_name = input("Enter full name: ")
            email = input("Enter email: ")
            
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            cursor.execute(
                "INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_password, full_name, email, 'opentickets')
            )
            conn.commit()
            print(f"User '{username}' created with 'opentickets' role.")
        
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
    add_opentickets_role()
