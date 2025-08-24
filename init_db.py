import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_db():
    # Delete the database if it exists
    if os.path.exists('database.db'):
        os.remove('database.db')
    
    # Create a new database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Read and execute the schema
    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())
    
    # Create a test admin user
    hashed_password = generate_password_hash('admin123')
    cursor.execute(
        'INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)',
        ('admin', hashed_password, 'Admin User', 'admin@example.com', 'admin')
    )
    
    # Create a test technician user
    cursor.execute(
        'INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)',
        ('tech1', generate_password_hash('tech123'), 'John Doe', 'john@example.com', 'technician')
    )
    
    # Create some sample locations
    locations = [
        ('Main Office', '123 Tech Street, City', 'Sarah Johnson', '+1234567890', '123456789'),
        ('Branch 1', '456 Support Ave, Town', 'Michael Brown', '+1987654321', '987654321'),
        ('Remote', 'Online', 'Remote Support', '+1122334455', '555555555')
    ]
    cursor.executemany(
        'INSERT INTO locations (name, address, contact_person, contact_phone, anydesk_id) VALUES (?, ?, ?, ?, ?)',
        locations
    )
    
    # Create some sample equipment
    equipment = [
        ('Router', 'Cisco RV340', 'SN-RTR-001', 1, '192.168.1.1', 'Active', '2023-01-15'),
        ('CAPS', 'HP EliteDesk', 'SN-CAPS-001', 1, '192.168.1.10', 'Active', '2023-02-20'),
        ('Receipt Printer', 'Epson TM-T88V', 'SN-PRT-001', 2, None, 'Active', '2023-03-10'),
        ('Access Point', 'Ubiquiti UAP-AC-PRO', 'SN-AP-001', 3, '192.168.1.100', 'Active', '2023-01-05')
    ]
    cursor.executemany(
        'INSERT INTO equipment (device_type, model, serial_number, location_id, ip_address, status, installation_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
        equipment
    )
    
    # Create some sample tickets
    tickets = [
        ('Network Issue', 'Internet connection is slow', 'Open', 'High', 2, 1, 1, 1),
        ('Printer Not Working', 'Printer is not responding', 'In Progress', 'Medium', 2, 2, 2, 3),
        ('New Equipment Setup', 'Need to setup new workstation', 'Open', 'Medium', 2, 1, 3, 2)
    ]
    cursor.executemany(
        'INSERT INTO tickets (title, description, status, priority, created_by, assigned_to, location_id, equipment_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        tickets
    )
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
