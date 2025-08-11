class LibraryApp {
    constructor() {
        this.apiUrl = '/api';
        this.token = localStorage.getItem('token');
        this.currentUser = JSON.parse(localStorage.getItem('user') || 'null');
        this.init();
    }

    init() {
        if (window.location.pathname === '/dashboard') {
            this.initDashboard();
        } else {
            this.initLoginPage();
        }
    }

    initLoginPage() {
        const showRegister = document.getElementById('showRegister');
        const showLogin = document.getElementById('showLogin');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const loginFormElement = document.getElementById('loginFormElement');
        const registerFormElement = document.getElementById('registerFormElement');

        showRegister?.addEventListener('click', (e) => {
            e.preventDefault();
            loginForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
        });

        showLogin?.addEventListener('click', (e) => {
            e.preventDefault();
            registerForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
        });

        loginFormElement?.addEventListener('submit', (e) => this.handleLogin(e));
        registerFormElement?.addEventListener('submit', (e) => this.handleRegister(e));
    }

    initDashboard() {
        if (!this.token || !this.currentUser) {
            window.location.href = '/';
            return;
        }

        // Set welcome message
        document.getElementById('welcomeUser').textContent = `Welcome, ${this.currentUser.username}`;

        // Show admin section if user is admin
        if (this.currentUser.role === 'admin') {
            document.getElementById('adminSection').style.display = 'block';
        }

        // Event listeners
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        document.getElementById('searchBtn').addEventListener('click', () => this.searchBooks());
        document.getElementById('showAllBooks').addEventListener('click', () => this.loadBooks());
        document.getElementById('searchBooks').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchBooks();
        });

        // Admin event listeners
        document.getElementById('showAddBookForm')?.addEventListener('click', () => this.toggleAddBookForm());
        document.getElementById('addBookFormElement')?.addEventListener('submit', (e) => this.handleAddBook(e));
        document.getElementById('cancelAddBook')?.addEventListener('click', () => this.hideAddBookForm());

        // Edit book modal listeners
        document.getElementById('editBookForm')?.addEventListener('submit', (e) => this.handleEditBook(e));
        document.getElementById('cancelEditBook')?.addEventListener('click', () => this.hideEditBookModal());

        // Load initial data
        this.loadBooks();
        this.loadMyBooks();
    }

    async handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const loginData = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        try {
            const response = await fetch(`${this.apiUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(loginData)
            });

            const result = await response.json();

            if (result.success) {
                localStorage.setItem('token', result.token);
                localStorage.setItem('user', JSON.stringify(result.user));
                window.location.href = '/dashboard';
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Login failed. Please try again.');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const registerData = {
            username: formData.get('username'),
            password: formData.get('password'),
            role: formData.get('role')
        };

        try {
            const response = await fetch(`${this.apiUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(registerData)
            });

            const result = await response.json();

            if (result.success) {
                alert('Registration successful! Please login.');
                document.getElementById('registerForm').classList.add('hidden');
                document.getElementById('loginForm').classList.remove('hidden');
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('Registration error:', error);
            alert('Registration failed. Please try again.');
        }
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
    }

    async loadBooks(searchTerm = '') {
        try {
            const url = searchTerm ? `${this.apiUrl}/books?search=${encodeURIComponent(searchTerm)}` : `${this.apiUrl}/books`;
            const response = await fetch(url);
            const result = await response.json();

            if (result.success) {
                this.displayBooks(result.books);
            }
        } catch (error) {
            console.error('Error loading books:', error);
        }
    }

    async searchBooks() {
        const searchTerm = document.getElementById('searchBooks').value.trim();
        await this.loadBooks(searchTerm);
    }

    displayBooks(books) {
        const container = document.getElementById('booksContainer');
        
        if (books.length === 0) {
            container.innerHTML = '<p>No books found.</p>';
            return;
        }

        container.innerHTML = books.map(book => `
            <div class="book-card">
                <h4>${book.title}</h4>
                <p><strong>Author:</strong> ${book.author}</p>
                <p><strong>Category:</strong> ${book.category || 'N/A'}</p>
                <p><strong>ISBN:</strong> ${book.isbn || 'N/A'}</p>
                <p><strong>Available:</strong> ${book.available_copies}/${book.total_copies}</p>
                <div class="book-actions">
                    ${this.currentUser.role === 'admin' ? 
                        `<button class="edit-btn" onclick="app.showEditBookModal(${book.id}, '${book.title}', '${book.author}', '${book.isbn || ''}', '${book.category || ''}', ${book.total_copies})">Edit</button>` : 
                        ''
                    }
                    ${book.available_copies > 0 ? 
                        `<button class="issue-btn" onclick="app.issueBook(${book.id})">Issue Book</button>` : 
                        '<button disabled>Not Available</button>'
                    }
                </div>
            </div>
        `).join('');
    }

    async loadMyBooks() {
        try {
            const response = await fetch(`${this.apiUrl}/my-books`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            const result = await response.json();

            if (result.success) {
                this.displayMyBooks(result.books);
            }
        } catch (error) {
            console.error('Error loading my books:', error);
        }
    }

    displayMyBooks(books) {
        const container = document.getElementById('myBooksContainer');
        
        if (books.length === 0) {
            container.innerHTML = '<p>You have no issued books.</p>';
            return;
        }

        container.innerHTML = books.map(book => {
            const dueDate = new Date(book.due_date);
            const isOverdue = dueDate < new Date();
            
            return `
                <div class="book-card ${isOverdue ? 'overdue' : ''}">
                    <h4>${book.title}</h4>
                    <p><strong>Author:</strong> ${book.author}</p>
                    <p><strong>Issue Date:</strong> ${new Date(book.issue_date).toLocaleDateString()}</p>
                    <p><strong>Due Date:</strong> ${dueDate.toLocaleDateString()} ${isOverdue ? '(OVERDUE)' : ''}</p>
                    <div class="book-actions">
                        <button class="return-btn" onclick="app.returnBook(${book.id})">Return Book</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    toggleAddBookForm() {
        const form = document.getElementById('addBookForm');
        form.classList.toggle('hidden');
    }

    hideAddBookForm() {
        document.getElementById('addBookForm').classList.add('hidden');
        document.getElementById('addBookFormElement').reset();
    }

    async handleAddBook(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const bookData = {
            title: formData.get('title'),
            author: formData.get('author'),
            isbn: formData.get('isbn'),
            category: formData.get('category'),
            copies: parseInt(formData.get('copies'))
        };

        try {
            const response = await fetch(`${this.apiUrl}/books`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(bookData)
            });

            const result = await response.json();

            if (result.success) {
                alert('Book added successfully!');
                this.hideAddBookForm();
                this.loadBooks();
            } else {
                alert(result.message || 'Failed to add book');
            }
        } catch (error) {
            console.error('Error adding book:', error);
            alert('Failed to add book. Please try again.');
        }
    }

    showEditBookModal(id, title, author, isbn, category, copies) {
        document.getElementById('editBookId').value = id;
        document.getElementById('editBookTitle').value = title;
        document.getElementById('editBookAuthor').value = author;
        document.getElementById('editBookISBN').value = isbn;
        document.getElementById('editBookCategory').value = category;
        document.getElementById('editBookCopies').value = copies;
        document.getElementById('editBookModal').classList.remove('hidden');
    }

    hideEditBookModal() {
        document.getElementById('editBookModal').classList.add('hidden');
        document.getElementById('editBookForm').reset();
    }

    async handleEditBook(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const bookId = formData.get('id');
        const bookData = {
            title: formData.get('title'),
            author: formData.get('author'),
            isbn: formData.get('isbn'),
            category: formData.get('category'),
            copies: parseInt(formData.get('copies'))
        };

        try {
            const response = await fetch(`${this.apiUrl}/books/${bookId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(bookData)
            });

            const result = await response.json();

            if (result.success) {
                alert('Book updated successfully!');
                this.hideEditBookModal();
                this.loadBooks();
            } else {
                alert(result.message || 'Failed to update book');
            }
        } catch (error) {
            console.error('Error updating book:', error);
            alert('Failed to update book. Please try again.');
        }
    }

    async issueBook(bookId) {
        try {
            const response = await fetch(`${this.apiUrl}/issue-book`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ book_id: bookId })
            });

            const result = await response.json();

            if (result.success) {
                alert('Book issued successfully!');
                this.loadBooks();
                this.loadMyBooks();
            } else {
                alert(result.message || 'Failed to issue book');
            }
        } catch (error) {
            console.error('Error issuing book:', error);
            alert('Failed to issue book. Please try again.');
        }
    }

    async returnBook(bookId) {
        try {
            const response = await fetch(`${this.apiUrl}/return-book`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ book_id: bookId })
            });

            const result = await response.json();

            if (result.success) {
                alert('Book returned successfully!');
                this.loadBooks();
                this.loadMyBooks();
            } else {
                alert(result.message || 'Failed to return book');
            }
        } catch (error) {
            console.error('Error returning book:', error);
            alert('Failed to return book. Please try again.');
        }
    }
}