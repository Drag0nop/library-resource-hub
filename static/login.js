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
const usernameInput = document.getElementById('username');
const usernameError = document.getElementById('usernameError');
const passwordError = document.getElementById('passwordError');
const successMessage = document.getElementById('successMessage');

// Username validation
function validateUsername(username) {
    const usernameRegex = /^[a-zA-Z0-9_-]{3,}$/;
    return usernameRegex.test(username);
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
usernameInput.addEventListener('input', function() {
    if (this.value && !validateUsername(this.value)) {
        showError(usernameError, 'Username must be at least 3 characters and contain only letters, numbers, underscore, or hyphen');
    } else {
        hideError(usernameError);
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
loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    let isValid = true;

    hideError(usernameError);
    hideError(passwordError);

    // Validate username
    if (!username) {
        showError(usernameError, 'Username is required');
        isValid = false;
    } else if (!validateUsername(username)) {
        showError(usernameError, 'Username must be at least 3 characters and contain only letters, numbers, underscore, or hyphen');
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
        const loginBtn = document.querySelector('.login-btn');
        const originalText = loginBtn.textContent;
        
        loginBtn.textContent = 'Signing In...';
        loginBtn.style.opacity = '0.7';
        loginBtn.disabled = true;

        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    remember: document.getElementById('remember')?.checked || false
                })
            });

            const data = await response.json();

            if (data.success) {
                // Optional: show success animation before redirect
                successMessage.classList.add('show');
                setTimeout(() => {
                    window.location.href = data.redirect; // Go to /dashboard
                }, 800);
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert("An error occurred while logging in");
        } finally {
            loginBtn.textContent = originalText;
            loginBtn.style.opacity = '1';
            loginBtn.disabled = false;
        }
    }
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
