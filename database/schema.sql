CREATE DATABASE IF NOT EXISTS library_management;
USE library_management;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'member') DEFAULT 'member',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    category VARCHAR(100),
    total_copies INT DEFAULT 1,
    available_copies INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    return_date TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password, role) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/1kKaR4qwe', 'admin');

-- Insert some sample books
INSERT INTO books (title, author, isbn, category, total_copies, available_copies) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'Fiction', 5, 5),
('To Kill a Mockingbird', 'Harper Lee', '9780446310789', 'Fiction', 3, 3),
('1984', 'George Orwell', '9780451524935', 'Dystopian Fiction', 4, 4),
('Pride and Prejudice', 'Jane Austen', '9780141439518', 'Romance', 2, 2),
('The Catcher in the Rye', 'J.D. Salinger', '9780316769174', 'Fiction', 3, 3),
('Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', '9780747532699', 'Fantasy', 6, 6),
('The Lord of the Rings', 'J.R.R. Tolkien', '9780544003415', 'Fantasy', 4, 4),
('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 'Computer Science', 2, 2),
('Clean Code', 'Robert C. Martin', '9780132350884', 'Programming', 3, 3),
('Design Patterns', 'Gang of Four', '9780201633612', 'Software Engineering', 2, 2);