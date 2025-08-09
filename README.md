# Library Management System

A comprehensive library management system built with Flask and SQLite.

## Features

- User authentication (login/logout/register)
- Book management (add, edit, delete, list)
- Member management (add, edit, delete, list)
- Transaction management (issue, return, overdue tracking)
- Fine calculation for overdue books
- Responsive web interface

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Access the application at `http://localhost:5000`

## Default Login

- Username: admin
- Password: admin123

## Project Structure

- `app.py` - Main Flask application
- `config.py` - Configuration settings
- `models/database.py` - Database schema and connections
- `routes/` - Route handlers for different modules
- `utils/validators.py` - Helper functions and validators
- `templates/` - HTML templates
- `static/` - CSS, JS, and image files

## Usage

1. Login with the default admin account
2. Add books to the library catalog
3. Register library members
4. Issue books to members
5. Track returns and calculate fines
6. View overdue books and transactions