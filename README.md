# Library Resource Hub

A comprehensive library management system built with Flask, MySQL, and modern web technologies.

## Features

### For Users
- **User Authentication**: Secure login and registration system
- **Book Browsing**: Search and filter through the library collection
- **Book Borrowing**: Borrow and return books with due date tracking
- **Dashboard**: Personal dashboard showing borrowed books and recent activity
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### For Administrators
- **Admin Dashboard**: Overview of library statistics and recent activity
- **Book Management**: Add, edit, and delete books from the collection
- **User Management**: View and manage user accounts
- **Transaction Monitoring**: Track all borrowing and returning activities
- **Overdue Management**: Monitor overdue books and send notifications

## Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-Login**: User session management
- **MySQL**: Database for data persistence
- **Werkzeug**: Password hashing and security

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **JavaScript**: Interactive functionality and API calls
- **Font Awesome**: Icons and visual elements

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package installer)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd library-resource-hub
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup

#### Option A: Using MySQL (Recommended)
1. Create a MySQL database:
```sql
CREATE DATABASE library_hub;
```

2. Update the database configuration in `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/library_hub'
```

#### Option B: Using SQLite (Development)
The application will automatically create a SQLite database if MySQL is not available.

### 4. Initialize the Database
```bash
python init_db.py
```

This will create all necessary tables and add sample data including:
- Admin user: `admin@library.com` / `admin123`
- Test user: `user@library.com` / `user123`
- Sample books in various categories

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Quick Setup (Automated)

Run the setup script for automated installation:

```bash
python setup.py
```

This will install dependencies, set up the database, and provide you with login credentials.

## Usage

### User Login
1. Go to `http://localhost:5000`
2. Click "Register" to create a new account or use the test credentials
3. Browse books, borrow them, and manage your account

### Admin Login
1. Login with admin credentials: `admin@library.com` / `admin123`
2. Access the admin panel to manage books and users
3. Monitor transactions and library statistics

## Project Structure

```
library-resource-hub/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── init_db.py           # Database initialization
├── setup.py             # Automated setup script
├── models/              # Database models
│   ├── user.py
│   ├── book.py
│   └── transaction.py
├── routes/              # Application routes
│   ├── auth_routes.py
│   ├── book_routes.py
│   └── admin_routes.py
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── books.html
│   ├── book_detail.html
│   └── admin/
│       ├── dashboard.html
│       ├── books.html
│       ├── add_book.html
│       ├── edit_book.html
│       ├── users.html
│       └── transactions.html
└── static/             # Static files
    ├── css/
    │   └── main.css
    └── js/
        └── main.js
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Books
- `GET /books` - Browse books with pagination and filtering
- `GET /book/<id>` - Get book details
- `POST /borrow/<id>` - Borrow a book
- `POST /return/<id>` - Return a book

### Admin
- `GET /admin` - Admin dashboard
- `GET /admin/books` - Manage books
- `POST /admin/books/add` - Add new book
- `POST /admin/books/edit/<id>` - Edit book
- `POST /admin/books/delete/<id>` - Delete book
- `GET /admin/users` - Manage users
- `POST /admin/users/toggle/<id>` - Toggle user status
- `GET /admin/transactions` - View transactions

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost/library_hub
```

### Database Configuration
The application supports both MySQL and SQLite databases. Update `config.py` to change the database connection.

## Security Features

- Password hashing using Werkzeug
- CSRF protection with Flask-WTF
- Session management with Flask-Login
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy ORM

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.

## Changelog

### Version 1.0.0
- Initial release
- User authentication system
- Book management functionality
- Admin panel
- Responsive design
- MySQL database support