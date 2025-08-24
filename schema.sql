-- Drop tables if they exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS ticket_comments;

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations table
CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    contact_person TEXT NOT NULL,
    contact_phone TEXT NOT NULL,
    anydesk_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Equipment table
CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_type TEXT NOT NULL,
    model TEXT NOT NULL,
    serial_number TEXT UNIQUE NOT NULL,
    location_id INTEGER,
    ip_address TEXT,
    status TEXT NOT NULL DEFAULT 'Active',
    installation_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES locations (id)
);

-- Tickets table
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    priority TEXT NOT NULL DEFAULT 'Medium',
    created_by INTEGER NOT NULL,
    assigned_to INTEGER,
    location_id INTEGER,
    equipment_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (id),
    FOREIGN KEY (assigned_to) REFERENCES users (id),
    FOREIGN KEY (location_id) REFERENCES locations (id),
    FOREIGN KEY (equipment_id) REFERENCES equipment (id)
);

-- Ticket comments table
CREATE TABLE ticket_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Maintenance table
CREATE TABLE IF NOT EXISTS maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    maintenance_type TEXT NOT NULL,
    description TEXT,
    date_performed DATE NOT NULL,
    performed_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment (id),
    FOREIGN KEY (performed_by) REFERENCES users (id)
);

-- Create indexes
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_equipment_location ON equipment(location_id);
CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_maintenance_equipment ON maintenance(equipment_id);
CREATE INDEX idx_maintenance_date ON maintenance(date_performed);