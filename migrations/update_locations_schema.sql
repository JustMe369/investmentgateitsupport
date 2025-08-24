-- Add any missing columns to the locations table
BEGIN TRANSACTION;

-- Create a temporary table with the correct schema
CREATE TABLE locations_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    contact_person TEXT NOT NULL,
    contact_phone TEXT NOT NULL,
    anydesk_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Copy data from the old table to the new one
INSERT INTO locations_new (id, name, address, contact_person, contact_phone, anydesk_id, created_at)
SELECT 
    id, 
    COALESCE(name, 'Unnamed Location'),
    COALESCE(address, 'No address'),
    COALESCE(contact_person, 'No contact'),
    COALESCE(contact_phone, 'N/A'),
    anydesk_id,
    COALESCE(created_at, CURRENT_TIMESTAMP)
FROM locations;

-- Drop the old table
DROP TABLE locations;

-- Rename the new table to the original name
ALTER TABLE locations_new RENAME TO locations;

-- Recreate any indexes
-- (Add any indexes that were on the original table)

COMMIT;
