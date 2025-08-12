// Password visibility toggle
const passwordInput = document.getElementById('password');
const passwordToggle = document.getElementById('passwordToggle');

passwordToggle.addEventListener('click', function() {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    passwordToggle.textContent = type === 'password' ? '👁️' : '🙈';
});

// Form validation and submission
const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const emailError = document.getElementById('emailError');
const passwordError = document.getElementById('passwordError');
const successMessage = document.getElementById('successMessage');

// Email validation
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Password validation
function validatePassword(password) {
    return password.length >= 6;
}

// Show error message
function showError(element, message) {
    element.textContent = message;
    element.classList.add('show');
}

// Hide error message
function hideError(element) {
    element.classList.remove('show');
}

// Real-time validation
emailInput.addEventListener('input', function() {
    if (this.value && !validateEmail(this.value)) {
        showError(emailError, 'Please enter a valid email address');
    } else {
        hideError(emailError);
    }
});

passwordInput.addEventListener('input', function() {
    if (this.value && !validatePassword(this.value)) {
        showError(passwordError, 'Password must be at least 6 characters long');
    } else {
        hideError(passwordError);
    }
});

// Form submission
loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;
    let isValid = true;

    // Reset errors
    hideError(emailError);
    hideError(passwordError);

    // Validate email
    if (!email) {
        showError(emailError, 'Email is required');
        isValid = false;
    } else if (!validateEmail(email)) {
        showError(emailError, 'Please enter a valid email address');
        isValid = false;
    }

    // Validate password
    if (!password) {
        showError(passwordError, 'Password is required');
        isValid = false;
    } else if (!validatePassword(password)) {
        showError(passwordError, 'Password must be at least 6 characters long');
        isValid = false;
    }

    if (isValid) {
        // Simulate login process
        const loginBtn = document.querySelector('.login-btn');
        const originalText = loginBtn.textContent;
        
        loginBtn.textContent = 'Signing In...';
        loginBtn.style.opacity = '0.7';
        loginBtn.disabled = true;

        setTimeout(() => {
            successMessage.classList.add('show');
            loginBtn.textContent = originalText;
            loginBtn.style.opacity = '1';
            loginBtn.disabled = false;

            // In a real application, you would redirect here
            setTimeout(() => {
                alert('Login successful! In a real app, you would be redirected now.');
                successMessage.classList.remove('show');
            }, 2000);
        }, 1500);
    }
});

// Social login buttons
document.querySelector('.social-btn.google').addEventListener('click', function() {
    alert('Google login would be implemented here');
});

document.querySelector('.social-btn.apple').addEventListener('click', function() {
    alert('Apple login would be implemented here');
});

// Forgot password link
document.querySelector('.forgot-password').addEventListener('click', function(e) {
    e.preventDefault();
    alert('Forgot password functionality would be implemented here');
});

// Sign up link
document.querySelector('.signup-link a').addEventListener('click', function(e) {
    e.preventDefault();
    alert('Sign up page would be shown here');
});

// Add focus animations
const inputs = document.querySelectorAll('.form-input');
inputs.forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'scale(1.02)';
    });

    input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'scale(1)';
    });
});
// In your login form submission
fetch('/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: email,
        password: password,
        remember: remember
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        window.location.href = data.redirect;
    } else {
        // Show error message
    }
});