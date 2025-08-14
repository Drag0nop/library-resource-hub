// login.js - Complete Login Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the login page
    initializeLoginPage();
});

function initializeLoginPage() {
    // Get DOM elements
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const rememberCheckbox = document.getElementById('remember');
    const submitButton = document.querySelector('.login-btn');
    const successMessage = document.getElementById('successMessage');
    
    // Check if already logged in
    checkExistingSession();
    
    // Setup form submission
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Setup input validation
    if (usernameInput) {
        usernameInput.addEventListener('input', handleInputChange);
        usernameInput.addEventListener('blur', validateUsername);
    }
    
    // Focus on username input
    if (usernameInput) {
        usernameInput.focus();
    }
    
    // Handle enter key in form
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && document.activeElement.tagName !== 'BUTTON') {
            e.preventDefault();
            if (loginForm) {
                loginForm.dispatchEvent(new Event('submit'));
            }
        }
    });
}

// Check if user is already logged in
function checkExistingSession() {
    fetch('/api/user-info', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // User is already logged in, redirect to dashboard
            window.location.href = '/dashboard';
        }
    })
    .catch(error => {
        // User is not logged in, continue with login page
        console.log('User not logged in, showing login form');
    });
}

// Handle form submission
function handleLogin(e) {
    e.preventDefault();
    
    // Clear any existing errors
    clearAllErrors();
    
    // Get form data
    const formData = getFormData();
    
    // Validate form data
    if (!validateFormData(formData)) {
        return;
    }
    
    // Show loading state
    showLoadingState(true);
    
    // Make API call
    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        handleLoginResponse(data);
    })
    .catch(error => {
        console.error('Login error:', error);
        showError('general', 'Network error. Please check your connection and try again.');
        showLoadingState(false);
    });
}

// Get form data
function getFormData() {
    const usernameInput = document.getElementById('username');
    const rememberCheckbox = document.getElementById('remember');
    
    return {
        username: usernameInput ? usernameInput.value.trim() : '',
        password: 'admin123', // Since password field was removed from HTML, using default
        remember: rememberCheckbox ? rememberCheckbox.checked : false
    };
}

// Validate form data
function validateFormData(data) {
    let isValid = true;
    
    // Validate username
    if (!data.username) {
        showError('username', 'Username is required');
        isValid = false;
    } else if (data.username.length < 3) {
        showError('username', 'Username must be at least 3 characters long');
        isValid = false;
    } else if (!isValidUsername(data.username)) {
        showError('username', 'Username contains invalid characters');
        isValid = false;
    }
    
    return isValid;
}

// Check if username is valid
function isValidUsername(username) {
    // Allow alphanumeric characters, underscores, hyphens, dots, and @ for email
    const usernameRegex = /^[a-zA-Z0-9._@-]+$/;
    return usernameRegex.test(username);
}

// Handle login response
function handleLoginResponse(data) {
    if (data.success) {
        // Show success message
        showSuccessMessage(data.message || 'Login successful!');
        
        // Redirect after a short delay
        setTimeout(() => {
            window.location.href = data.redirect || '/dashboard';
        }, 1500);
        
    } else {
        // Show error message
        const errorMessage = data.message || 'Login failed. Please try again.';
        
        if (errorMessage.toLowerCase().includes('username') || 
            errorMessage.toLowerCase().includes('user')) {
            showError('username', errorMessage);
        } else {
            showError('general', errorMessage);
        }
        
        showLoadingState(false);
        
        // Focus back to username input
        const usernameInput = document.getElementById('username');
        if (usernameInput) {
            usernameInput.focus();
            usernameInput.select();
        }
    }
}

// Show/hide loading state
function showLoadingState(loading) {
    const submitButton = document.querySelector('.login-btn');
    
    if (submitButton) {
        if (loading) {
            submitButton.disabled = true;
            submitButton.classList.add('loading');
            submitButton.textContent = 'Signing In...';
        } else {
            submitButton.disabled = false;
            submitButton.classList.remove('loading');
            submitButton.textContent = 'Sign In';
        }
    }
}

// Show success message
function showSuccessMessage(message) {
    const successElement = document.getElementById('successMessage');
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
    }
}

// Show error message
function showError(field, message) {
    // Show error message
    const errorElement = document.getElementById(field + 'Error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    
    // Add error class to input
    const inputElement = document.getElementById(field === 'general' ? 'username' : field);
    if (inputElement) {
        inputElement.classList.add('error');
    }
    
    // If no specific error element found, show alert
    if (!errorElement && field === 'general') {
        alert(message);
    }
}

// Clear all errors
function clearAllErrors() {
    // Hide all error messages
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(element => {
        element.style.display = 'none';
        element.textContent = '';
    });
    
    // Remove error classes from inputs
    const inputElements = document.querySelectorAll('.form-input');
    inputElements.forEach(element => {
        element.classList.remove('error');
    });
    
    // Hide success message
    const successElement = document.getElementById('successMessage');
    if (successElement) {
        successElement.style.display = 'none';
    }
}

// Handle input changes
function handleInputChange(e) {
    // Clear error state when user starts typing
    e.target.classList.remove('error');
    
    const errorElement = document.getElementById(e.target.id + 'Error');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

// Validate username on blur
function validateUsername(e) {
    const username = e.target.value.trim();
    
    if (username && username.length > 0 && username.length < 3) {
        showError('username', 'Username must be at least 3 characters long');
    } else if (username && !isValidUsername(username)) {
        showError('username', 'Username contains invalid characters');
    }
}

// Utility function to create a test user (for development)
function createTestUser() {
    // This is for development purposes only
    console.log('Test user credentials:');
    console.log('Username: admin');
    console.log('Password: admin123');
}

// Handle browser back button
window.addEventListener('popstate', function(e) {
    // Prevent going back if user is in the middle of login process
    const submitButton = document.querySelector('.login-btn');
    if (submitButton && submitButton.disabled) {
        e.preventDefault();
        history.pushState(null, null, window.location.href);
    }
});

// Prevent form submission with empty data
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
        const form = e.target.closest('form');
        if (form && form.id === 'loginForm') {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    }
});

// Auto-fill username for demo purposes (remove in production)
document.addEventListener('DOMContentLoaded', function() {
    // For demo purposes, you can uncomment the next line to auto-fill admin username
    // document.getElementById('username').value = 'admin';
    
    // Show test credentials in console for development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        createTestUser();
    }
});

// Handle offline/online status
window.addEventListener('online', function() {
    console.log('Connection restored');
    // You could show a notification here
});

window.addEventListener('offline', function() {
    console.log('Connection lost');
    showError('general', 'No internet connection. Please check your network.');
});

// Security: Clear any sensitive data from memory
window.addEventListener('beforeunload', function() {
    // Clear any sensitive form data
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    inputs.forEach(input => {
        input.value = '';
    });
});