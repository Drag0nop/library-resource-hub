// Main JavaScript functionality for Library Resource Hub

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile navigation
    initMobileNav();
    
    // Initialize flash message auto-hide
    initFlashMessages();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize tooltips and interactions
    initInteractions();
});

// Mobile Navigation
function initMobileNav() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Close mobile menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }
}

// Flash Messages
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Auto-hide success messages after 5 seconds
        if (message.classList.contains('flash-success')) {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    if (message.parentNode) {
                        message.parentNode.removeChild(message);
                    }
                }, 300);
            }, 5000);
        }
        
        // Auto-hide info messages after 3 seconds
        if (message.classList.contains('flash-info')) {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    if (message.parentNode) {
                        message.parentNode.removeChild(message);
                    }
                }, 300);
            }, 3000);
        }
    });
}

// Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    // Password confirmation validation
    const passwordField = form.querySelector('input[name="password"]');
    const confirmPasswordField = form.querySelector('input[name="confirm_password"]');
    
    if (passwordField && confirmPasswordField) {
        if (passwordField.value !== confirmPasswordField.value) {
            showFieldError(confirmPasswordField, 'Passwords do not match');
            isValid = false;
        }
    }
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = 'var(--error-color)';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = 'var(--error-color)';
}

function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.style.borderColor = '';
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// General Interactions
function initInteractions() {
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });
}

// Utility Functions
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.innerHTML = `
        <span class="flash-text">${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to flash messages container or create one
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto-hide after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, duration);
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// API Helper Functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Search functionality
function initSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        const debouncedSearch = debounce(function() {
            const searchTerm = this.value.trim();
            if (searchTerm.length >= 2) {
                performSearch(searchTerm);
            }
        }, 300);
        
        input.addEventListener('input', debouncedSearch);
    });
}

function performSearch(searchTerm) {
    // This would be implemented based on the specific search requirements
    console.log('Searching for:', searchTerm);
}

// Book actions
function initBookActions() {
    // Borrow book functionality
    document.addEventListener('click', async function(e) {
        if (e.target.classList.contains('borrow-btn') || e.target.closest('.borrow-btn')) {
            e.preventDefault();
            const button = e.target.closest('.borrow-btn');
            const bookId = button.dataset.bookId;
            
            if (bookId) {
                await borrowBook(bookId, button);
            }
        }
        
        // Return book functionality
        if (e.target.classList.contains('return-btn') || e.target.closest('.return-btn')) {
            e.preventDefault();
            const button = e.target.closest('.return-btn');
            const bookId = button.dataset.bookId;
            
            if (bookId) {
                await returnBook(bookId, button);
            }
        }
    });
}

async function borrowBook(bookId, button) {
    const originalText = button.innerHTML;
    
    try {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Borrowing...';
        
        const response = await apiRequest(`/borrow/${bookId}`, {
            method: 'POST'
        });
        
        showNotification(response.message, 'success');
        
        // Update button state
        button.innerHTML = '<i class="fas fa-check"></i> Borrowed';
        button.classList.remove('btn-primary');
        button.classList.add('btn-success');
        
        // Refresh page after a short delay
        setTimeout(() => {
            window.location.reload();
        }, 1500);
        
    } catch (error) {
        showNotification(error.message, 'error');
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

async function returnBook(bookId, button) {
    const originalText = button.innerHTML;
    
    try {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Returning...';
        
        const response = await apiRequest(`/return/${bookId}`, {
            method: 'POST'
        });
        
        showNotification(response.message, 'success');
        
        // Update button state
        button.innerHTML = '<i class="fas fa-check"></i> Returned';
        button.classList.remove('btn-warning');
        button.classList.add('btn-success');
        
        // Refresh page after a short delay
        setTimeout(() => {
            window.location.reload();
        }, 1500);
        
    } catch (error) {
        showNotification(error.message, 'error');
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

// Initialize book actions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initBookActions();
    initSearch();
});

// Admin functionality
function initAdminFeatures() {
    // Delete confirmation modals
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemName = this.dataset.itemName || 'item';
            const itemId = this.dataset.itemId;
            
            if (confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                // Proceed with deletion
                deleteItem(itemId, this);
            }
        });
    });
}

async function deleteItem(itemId, button) {
    const originalText = button.innerHTML;
    
    try {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
        
        const response = await apiRequest(`/admin/delete/${itemId}`, {
            method: 'POST'
        });
        
        showNotification(response.message, 'success');
        
        // Remove the item from the DOM
        const row = button.closest('tr') || button.closest('.item-card');
        if (row) {
            row.style.opacity = '0';
            setTimeout(() => {
                row.remove();
            }, 300);
        }
        
    } catch (error) {
        showNotification(error.message, 'error');
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

// Initialize admin features
document.addEventListener('DOMContentLoaded', function() {
    initAdminFeatures();
});

// Export functions for global use
window.showNotification = showNotification;
window.apiRequest = apiRequest;