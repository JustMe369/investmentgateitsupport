# Caribou IT Support System

A comprehensive IT support ticketing system built with Flask and SQLite.

## Features

- User authentication (login/logout)
- Create and manage support tickets
- Track IT equipment and locations
- Generate reports
- Responsive design

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd caribou-support
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```

## Running the Application

1. **Start the development server**
   ```bash
   python app.py
   ```

2. **Access the application**
   Open your web browser and go to: http://localhost:5000

## Default Admin Account

- **Username**: admin
- **Password**: admin123

## Project Structure

```
caribou-support/
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
├── templates/            # HTML templates
├── database.db           # SQLite database (created on first run)
├── schema.sql            # Database schema
├── app.py                # Main application file
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## API Endpoints

- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/tickets` - Get all tickets
- `POST /api/tickets` - Create a new ticket
- `GET /api/tickets/<id>` - Get a specific ticket
- `PUT /api/tickets/<id>` - Update a ticket
- `DELETE /api/tickets/<id>` - Delete a ticket

(Similar endpoints exist for locations, equipment, and users)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
