// Library Management System JavaScript

// Data Storage (In a real app, this would be connected to a backend database)
let library = {
    books: [
        {
            id: 1,
            title: "To Kill a Mockingbird",
            author: "Harper Lee",
            isbn: "978-0-06-112008-4",
            category: "Fiction",
            publisher: "J.B. Lippincott & Co.",
            year: 1960,
            description: "A gripping tale of racial injustice and childhood innocence.",
            available: true,
            addedBy: "admin",
            dateAdded: "2024-01-15"
        },
        {
            id: 2,
            title: "1984",
            author: "George Orwell",
            isbn: "978-0-452-28423-4",
            category: "Fiction",
            publisher: "Secker & Warburg",
            year: 1949,
            description: "A dystopian social science fiction novel and cautionary tale.",
            available: false,
            addedBy: "admin",
            dateAdded: "2024-01-16"
        },
        {
            id: 3,
            title: "The Great Gatsby",
            author: "F. Scott Fitzgerald",
            isbn: "978-0-7432-7356-5",
            category: "Fiction",
            publisher: "Charles Scribner's Sons",
            year: 1925,
            description: "A classic American novel set in the Jazz Age.",
            available: true,
            addedBy: "admin",
            dateAdded: "2024-01-17"
        }
    ],
    issuedBooks: [
        {
            id: 1,
            bookId: 2,
            bookTitle: "1984",
            memberName: "John Doe",
            memberEmail: "john.doe@email.com",
            issueDate: "2024-01-20",
            dueDate: "2024-02-03",
            returned: false
        }
    ],
    userStats: {
        booksAdded: 0,
        booksDeleted: 0,
        booksIssued: 0
    }
};

// Current user data
let currentUser = {
    name: "Library Admin",
    role: "Administrator",
    initial: "A"
};

// DOM Elements
const pages = document.querySelectorAll('.page');
const navLinks = document.querySelectorAll('.nav-link');
const userAvatar = document.getElementById('userAvatar');
const userDropdown = document.getElementById('userDropdown');
const toast = document.getElementById('toast');
const deleteModal = document.getElementById('deleteModal');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    updateUserProfile();
    updateStatistics();
});

// Initialize the application
function initializeApp() {
    showPage('home');
    populateBookSelect();
    displayRecentBooks();
    displayBooksForDelete();
    displayIssuedBooks();
}

// Setup event listeners
function setupEventListeners() {
    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            showPage(page);
            setActiveNav(this);
        });
    });

    // User dropdown toggle
    userAvatar.addEventListener('click', function(e) {
        e.stopPropagation();
        userDropdown.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function() {
        userDropdown.classList.remove('active');
    });

    // Form submissions
    document.getElementById('addBookForm').addEventListener('submit', handleAddBook);
    document.getElementById('issueBookForm').addEventListener('submit', handleIssueBook);

    // Search functionality
    document.getElementById('deleteSearchInput').addEventListener('input', filterBooksForDelete);
    document.getElementById('deleteFilterCategory').addEventListener('change', filterBooksForDelete);

    // Modal close
    document.querySelector('.modal-close').addEventListener('click', closeDeleteModal);
    document.querySelector('.toast-close').addEventListener('click', hideToast);

    // Set default dates for issue form
    const today = new Date().toISOString().split('T')[0];
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 14);
    const dueDateString = dueDate.toISOString().split('T')[0];
    
    document.getElementById('issueDate').value = today;
    document.getElementById('dueDate').value = dueDateString;
}

// Page navigation
function showPage(pageId) {
    pages.forEach(page => page.classList.remove('active'));
    document.getElementById(pageId + 'Page').classList.add('active');
}

function setActiveNav(activeLink) {
    navLinks.forEach(link => link.classList.remove('active'));
    activeLink.classList.add('active');
}

// User profile management
function updateUserProfile() {
    document.getElementById('userName').textContent = currentUser.name;
    document.getElementById('userRole').textContent = currentUser.role;
    document.querySelector('.user-initial').textContent = currentUser.initial;
    
    document.getElementById('booksAdded').textContent = library.userStats.booksAdded;
    document.getElementById('booksDeleted').textContent = library.userStats.booksDeleted;
    document.getElementById('booksIssued').textContent = library.userStats.booksIssued;
}

// Statistics management
function updateStatistics() {
    const totalBooks = library.books.length;
    const availableBooks = library.books.filter(book => book.available).length;
    const issuedBooks = library.issuedBooks.filter(issue => !issue.returned).length;
    
    document.getElementById('totalBooks').textContent = totalBooks;
    document.getElementById('availableBooks').textContent = availableBooks;
    document.getElementById('totalIssued').textContent = issuedBooks;
}

// Add book functionality
function handleAddBook(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const bookData = {
        id: Date.now(),
        title: formData.get('title'),
        author: formData.get('author'),
        isbn: formData.get('isbn') || '',
        category: formData.get('category'),
        publisher: formData.get('publisher') || '',
        year: parseInt(formData.get('year')) || '',
        description: formData.get('description') || '',
        available: true,
        addedBy: currentUser.name,
        dateAdded: new Date().toISOString().split('T')[0]
    };
    
    // Add book to library
    library.books.push(bookData);
    library.userStats.booksAdded++;
    
    // Update UI
    updateUserProfile();
    updateStatistics();
    displayRecentBooks();
    displayBooksForDelete();
    populateBookSelect();
    
    // Reset form
    e.target.reset();
    
    // Show success message
    showToast('Book added successfully!', 'success');
}

// Display recent books
function displayRecentBooks() {
    const recentBooksContainer = document.getElementById('recentBooks');
    const recentBooks = library.books.slice(-5).reverse();
    
    if (recentBooks.length === 0) {
        recentBooksContainer.innerHTML = '<p style="text-align: center; color: #666;">No books added yet.</p>';
        return;
    }
    
    recentBooksContainer.innerHTML = recentBooks.map(book => `
        <div class="book-item">
            <div class="book-title">${book.title}</div>
            <div class="book-author">by ${book.author}</div>
            <div class="book-details">
                <strong>Category:</strong> ${book.category}<br>
                <strong>Year:</strong> ${book.year || 'N/A'}<br>
                <strong>Added:</strong> ${formatDate(book.dateAdded)}
            </div>
        </div>
    `).join('');
}

// Display books for deletion
function displayBooksForDelete() {
    const deleteBookList = document.getElementById('deleteBookList');
    
    if (library.books.length === 0) {
        deleteBookList.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1 / -1;">No books available to delete.</p>';
        return;
    }
    
    deleteBookList.innerHTML = library.books.map(book => `
        <div class="book-item" data-book-id="${book.id}">
            <div class="book-title">${book.title}</div>
            <div class="book-author">by ${book.author}</div>
            <div class="book-details">
                <strong>ISBN:</strong> ${book.isbn || 'N/A'}<br>
                <strong>Category:</strong> ${book.category}<br>
                <strong>Status:</strong> ${book.available ? 'Available' : 'Issued'}
            </div>
            <div class="book-actions">
                <button class="btn-danger" onclick="showDeleteModal(${book.id})">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
}

// Filter books for delete page
function filterBooksForDelete() {
    const searchTerm = document.getElementById('deleteSearchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('deleteFilterCategory').value;
    
    let filteredBooks = library.books;
    
    if (searchTerm) {
        filteredBooks = filteredBooks.filter(book => 
            book.title.toLowerCase().includes(searchTerm) ||
            book.author.toLowerCase().includes(searchTerm) ||
            book.isbn.toLowerCase().includes(searchTerm)
        );
    }
    
    if (categoryFilter) {
        filteredBooks = filteredBooks.filter(book => book.category === categoryFilter);
    }
    
    const deleteBookList = document.getElementById('deleteBookList');
    
    if (filteredBooks.length === 0) {
        deleteBookList.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1 / -1;">No books match your search criteria.</p>';
        return;
    }
    
    deleteBookList.innerHTML = filteredBooks.map(book => `
        <div class="book-item" data-book-id="${book.id}">
            <div class="book-title">${book.title}</div>
            <div class="book-author">by ${book.author}</div>
            <div class="book-details">
                <strong>ISBN:</strong> ${book.isbn || 'N/A'}<br>
                <strong>Category:</strong> ${book.category}<br>
                <strong>Status:</strong> ${book.available ? 'Available' : 'Issued'}
            </div>
            <div class="book-actions">
                <button class="btn-danger" onclick="showDeleteModal(${book.id})">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
}

// Delete book functionality
let bookToDelete = null;

function showDeleteModal(bookId) {
    const book = library.books.find(b => b.id === bookId);
    if (!book) return;
    
    bookToDelete = book;
    
    document.getElementById('deleteBookDetails').innerHTML = `
        <div class="book-item">
            <div class="book-title">${book.title}</div>
            <div class="book-author">by ${book.author}</div>
            <div class="book-details">
                <strong>ISBN:</strong> ${book.isbn || 'N/A'}<br>
                <strong>Category:</strong> ${book.category}<br>
                <strong>Year:</strong> ${book.year || 'N/A'}
            </div>
        </div>
    `;
    
    deleteModal.classList.add('show');
}

function closeDeleteModal() {
    deleteModal.classList.remove('show');
    bookToDelete = null;
}

function confirmDelete() {
    if (!bookToDelete) return;
    
    // Remove book from library
    library.books = library.books.filter(book => book.id !== bookToDelete.id);
    
    // Remove from issued books if it was issued
    library.issuedBooks = library.issuedBooks.filter(issue => issue.bookId !== bookToDelete.id);
    
    library.userStats.booksDeleted++;
    
    // Update UI
    updateUserProfile();
    updateStatistics();
    displayBooksForDelete();
    populateBookSelect();
    displayIssuedBooks();
    
    closeDeleteModal();
    showToast('Book deleted successfully!', 'success');
}

// Issue book functionality
function populateBookSelect() {
    const bookSelect = document.getElementById('bookSelect');
    const availableBooks = library.books.filter(book => book.available);
    
    bookSelect.innerHTML = '<option value="">Choose a book...</option>' +
        availableBooks.map(book => 
            `<option value="${book.id}">${book.title} by ${book.author}</option>`
        ).join('');
}

function handleIssueBook(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const bookId = parseInt(formData.get('bookSelect'));
    const memberName = formData.get('memberName');
    const memberEmail = formData.get('memberEmail');
    const issueDate = formData.get('issueDate');
    const dueDate = formData.get('dueDate');
    
    if (!bookId) {
        showToast('Please select a book to issue.', 'error');
        return;
    }
    
    const book = library.books.find(b => b.id === bookId);
    if (!book || !book.available) {
        showToast('Selected book is not available.', 'error');
        return;
    }
    
    // Create issue record
    const issueRecord = {
        id: Date.now(),
        bookId: bookId,
        bookTitle: book.title,
        memberName: memberName,
        memberEmail: memberEmail,
        issueDate: issueDate,
        dueDate: dueDate,
        returned: false
    };
    
    // Add to issued books
    library.issuedBooks.push(issueRecord);
    
    // Mark book as unavailable
    book.available = false;
    
    library.userStats.booksIssued++;
    
    // Update UI
    updateUserProfile();
    updateStatistics();
    populateBookSelect();
    displayIssuedBooks();
    displayBooksForDelete();
    
    // Reset form
    e.target.reset();
    
    // Reset default dates
    const today = new Date().toISOString().split('T')[0];
    const newDueDate = new Date();
    newDueDate.setDate(newDueDate.getDate() + 14);
    const newDueDateString = newDueDate.toISOString().split('T')[0];
    
    document.getElementById('issueDate').value = today;
    document.getElementById('dueDate').value = newDueDateString;
    
    showToast('Book issued successfully!', 'success');
}

// Display issued books
function displayIssuedBooks() {
    const issuedBooksContainer = document.getElementById('issuedBooksList');
    const activeIssues = library.issuedBooks.filter(issue => !issue.returned);
    
    if (activeIssues.length === 0) {
        issuedBooksContainer.innerHTML = '<p style="text-align: center; color: #666;">No books currently issued.</p>';
        return;
    }
    
    issuedBooksContainer.innerHTML = activeIssues.map(issue => {
        const isOverdue = new Date(issue.dueDate) < new Date();
        return `
            <div class="issued-book-item">
                <div class="issued-book-title">${issue.bookTitle}</div>
                <div class="issued-book-member">Issued to: ${issue.memberName}</div>
                <div class="issued-book-dates">
                    <span>Issued: ${formatDate(issue.issueDate)}</span>
                    <span class="due-date ${isOverdue ? 'overdue' : ''}">
                        Due: ${formatDate(issue.dueDate)} ${isOverdue ? '(OVERDUE)' : ''}
                    </span>
                </div>
                <button class="return-btn" onclick="returnBook(${issue.id})">
                    Return Book
                </button>
            </div>
        `;
    }).join('');
}

// Return book functionality
function returnBook(issueId) {
    const issue = library.issuedBooks.find(i => i.id === issueId);
    if (!issue) return;
    
    // Mark as returned
    issue.returned = true;
    
    // Mark book as available
    const book = library.books.find(b => b.id === issue.bookId);
    if (book) {
        book.available = true;
    }
    
    // Update UI
    updateStatistics();
    populateBookSelect();
    displayIssuedBooks();
    displayBooksForDelete();
    
    showToast('Book returned successfully!', 'success');
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showToast(message, type = 'success') {
    const toastMessage = toast.querySelector('.toast-message');
    toastMessage.textContent = message;
    
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        hideToast();
    }, 4000);
}

function hideToast() {
    toast.classList.remove('show');
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        // In a real application, this would clear session data and redirect to login
        alert('Logout functionality would redirect to login page.');
        // window.location.href = 'login.html';
    }
}

// Initialize tooltips and additional features
function initializeTooltips() {
    // Add tooltips for better user experience
    const elements = document.querySelectorAll('[data-tooltip]');
    elements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + H for Home
    if (e.altKey && e.key === 'h') {
        e.preventDefault();
        showPage('home');
        setActiveNav(document.querySelector('[data-page="home"]'));
    }
    
    // Alt + A for Add Books
    if (e.altKey && e.key === 'a') {
        e.preventDefault();
        showPage('add');
        setActiveNav(document.querySelector('[data-page="add"]'));
    }
    
    // Alt + D for Delete Books
    if (e.altKey && e.key === 'd') {
        e.preventDefault();
        showPage('delete');
        setActiveNav(document.querySelector('[data-page="delete"]'));
    }
    
    // Alt + I for Issue Books
    if (e.altKey && e.key === 'i') {
        e.preventDefault();
        showPage('issue');
        setActiveNav(document.querySelector('[data-page="issue"]'));
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        closeDeleteModal();
        hideToast();
        userDropdown.classList.remove('active');
    }
});