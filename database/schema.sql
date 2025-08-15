-- Create database
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    genre VARCHAR(100),
    publication_year INT,
    copies_available INT DEFAULT 1,
    total_copies INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_genre (genre)
);

-- Create members table
CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    membership_date DATE DEFAULT (CURDATE()),
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_email (email),
    INDEX idx_status (status)
);

-- Create borrowings table
CREATE TABLE IF NOT EXISTS borrowings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    borrow_date DATE DEFAULT (CURDATE()),
    due_date DATE NOT NULL,
    return_date DATE NULL,
    status ENUM('borrowed', 'returned', 'overdue') DEFAULT 'borrowed',
    fine_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    INDEX idx_book_id (book_id),
    INDEX idx_member_id (member_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date)
);

-- Insert sample data
INSERT INTO books (title, author, isbn, genre, publication_year, copies_available, total_copies) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', '978-0-7432-7356-5', 'Fiction', 1925, 3, 3),
('To Kill a Mockingbird', 'Harper Lee', '978-0-06-112008-4', 'Fiction', 1960, 2, 2),
('1984', 'George Orwell', '978-0-452-28423-4', 'Dystopian Fiction', 1949, 4, 4),
('Pride and Prejudice', 'Jane Austen', '978-0-14-143951-8', 'Romance', 1813, 2, 2),
('The Catcher in the Rye', 'J.D. Salinger', '978-0-316-76948-0', 'Fiction', 1951, 1, 1),
('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', '978-0-439-70818-8', 'Fantasy', 1997, 5, 5),
('The Lord of the Rings', 'J.R.R. Tolkien', '978-0-544-00341-5', 'Fantasy', 1954, 3, 3),
('Dune', 'Frank Herbert', '978-0-441-17271-9', 'Science Fiction', 1965, 2, 2);

INSERT INTO members (name, email, phone, address) VALUES
('John Smith', 'john.smith@email.com', '555-0101', '123 Main St, Anytown, USA'),
('Emily Johnson', 'emily.johnson@email.com', '555-0102', '456 Oak Ave, Anytown, USA'),
('Michael Brown', 'michael.brown@email.com', '555-0103', '789 Pine Rd, Anytown, USA'),
('Sarah Davis', 'sarah.davis@email.com', '555-0104', '321 Elm St, Anytown, USA'),
('David Wilson', 'david.wilson@email.com', '555-0105', '654 Maple Dr, Anytown, USA');

-- Sample borrowings (some current, some returned)
INSERT INTO borrowings (book_id, member_id, borrow_date, due_date, return_date, status, fine_amount) VALUES
(1, 1, '2024-07-15', '2024-07-29', '2024-07-28', 'returned', 0.00),
(2, 2, '2024-07-20', '2024-08-03', NULL, 'borrowed', 0.00),
(3, 3, '2024-07-10', '2024-07-24', '2024-07-30', 'returned', 6.00),
(4, 4, '2024-08-01', '2024-08-15', NULL, 'borrowed', 0.00),
(5, 5, '2024-07-05', '2024-07-19', NULL, 'borrowed', 0.00);