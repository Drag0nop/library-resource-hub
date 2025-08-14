-- Create Database
CREATE DATABASE IF NOT EXISTS library_management;
USE library_management;

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Library Admin',
    books_added INT DEFAULT 0,
    books_deleted INT DEFAULT 0,
    books_issued INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Books Table
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20),
    category VARCHAR(50) DEFAULT 'Other',
    publisher VARCHAR(255),
    publication_year YEAR,
    description TEXT,
    added_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_isbn (isbn),
    INDEX idx_category (category)
);

-- Issued Books Table
CREATE TABLE issued_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_name VARCHAR(255) NOT NULL,
    member_email VARCHAR(100) NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    returned_date DATE NULL,
    issued_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (issued_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_book_id (book_id),
    INDEX idx_member_email (member_email),
    INDEX idx_issue_date (issue_date),
    INDEX idx_due_date (due_date),
    INDEX idx_returned_date (returned_date)
);

-- Members Table (Optional - for future expansion)
CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    membership_date DATE DEFAULT (CURRENT_DATE),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_status (status)
);

-- Book Categories Table (Optional - for future expansion)
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default categories
INSERT INTO categories (name, description) VALUES
('Fiction', 'Fictional literature and novels'),
('Non-Fiction', 'Factual and informational books'),
('Science', 'Scientific and technical books'),
('History', 'Historical books and biographies'),
('Biography', 'Life stories and autobiographies'),
('Technology', 'Technology and computer science books'),
('Other', 'Miscellaneous and uncategorized books');

-- Insert default admin user (password: admin123)
-- Note: In production, use a strong password and hash it properly
INSERT INTO users (username, email, password, role) VALUES
('admin', 'admin@library.com', 'scrypt:32768:8:1$ZQoOGPQjOLfqPfJr$8c6976e5b5410415bde908bd4dee15dfb167a9c0b444b263c8c9be5e7c86d80dc31dc52e2eb3b5f5e63969c3b1b3d1b9e88f8a5f2c9f6f8e3c9c4b7e9d8f3e7e2c', 'Library Admin');

-- Create triggers to update user statistics
DELIMITER //

CREATE TRIGGER update_books_added_count
AFTER INSERT ON books
FOR EACH ROW
BEGIN
    UPDATE users 
    SET books_added = books_added + 1 
    WHERE id = NEW.added_by;
END//

CREATE TRIGGER update_books_deleted_count
AFTER DELETE ON books
FOR EACH ROW
BEGIN
    UPDATE users 
    SET books_deleted = books_deleted + 1 
    WHERE id = OLD.added_by;
END//

CREATE TRIGGER update_books_issued_count
AFTER INSERT ON issued_books
FOR EACH ROW
BEGIN
    UPDATE users 
    SET books_issued = books_issued + 1 
    WHERE id = NEW.issued_by;
END//

DELIMITER ;

-- Create views for common queries
CREATE VIEW available_books AS
SELECT b.*, 
       CASE WHEN ib.id IS NOT NULL THEN 'issued' ELSE 'available' END as status
FROM books b 
LEFT JOIN issued_books ib ON b.id = ib.book_id AND ib.returned_date IS NULL
WHERE ib.id IS NULL;

CREATE VIEW currently_issued_books AS
SELECT ib.*, b.title, b.author, b.isbn,
       DATEDIFF(CURRENT_DATE, ib.due_date) as days_overdue
FROM issued_books ib
JOIN books b ON ib.book_id = b.id
WHERE ib.returned_date IS NULL;

CREATE VIEW overdue_books AS
SELECT ib.*, b.title, b.author, b.isbn,
       DATEDIFF(CURRENT_DATE, ib.due_date) as days_overdue
FROM issued_books ib
JOIN books b ON ib.book_id = b.id
WHERE ib.returned_date IS NULL AND ib.due_date < CURRENT_DATE;

-- Create indexes for better performance
CREATE INDEX idx_books_search ON books(title, author, isbn);
CREATE INDEX idx_issued_books_search ON issued_books(member_name, member_email);

-- Sample data (optional)
INSERT INTO books (title, author, isbn, category, publisher, publication_year, description, added_by) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'Fiction', 'Scribner', 1925, 'A classic American novel about the Jazz Age', 1),
('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 'Fiction', 'J.B. Lippincott & Co.', 1960, 'A story of racial injustice and childhood innocence', 1),
('1984', 'George Orwell', '9780451524935', 'Fiction', 'Secker & Warburg', 1949, 'A dystopian novel about totalitarian control', 1),
('The Catcher in the Rye', 'J.D. Salinger', '9780316769488', 'Fiction', 'Little, Brown and Company', 1951, 'A coming-of-age story', 1),
('Pride and Prejudice', 'Jane Austen', '9780141439518', 'Fiction', 'T. Egerton', 1813, 'A romantic novel about Elizabeth Bennet and Mr. Darcy', 1);

-- Show table structure
DESCRIBE users;
DESCRIBE books;
DESCRIBE issued_books;
DESCRIBE members;
DESCRIBE categories;