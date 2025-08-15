// Main JavaScript functionality for the library management system

$(document).ready(function() {
    // Initialize tooltips and other components
    initializeComponents();
    
    // Handle form submissions
    setupFormHandlers();
});

function initializeComponents() {
    // Add loading states to buttons
    $('.btn').on('click', function() {
        var btn = $(this);
        if (!btn.hasClass('btn-disabled') && btn.attr('type') === 'submit') {
            btn.addClass('loading');
            setTimeout(function() {
                btn.removeClass('loading');
            }, 2000);
        }
    });
}

function setupFormHandlers() {
    // Add book form handler
    $('#addBookForm').on('submit', function(e) {
        e.preventDefault();
        
        var formData = $(this).serialize();
        
        $.ajax({
            url: '/add_book',
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    closeAddBookModal();
                    location.reload();
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function() {
                alert('An error occurred. Please try again.');
            }
        });
    });
}

// Modal functions
function showAddBookModal() {
    $('#addBookModal').show();
    $('#title').focus();
}

function closeAddBookModal() {
    $('#addBookModal').hide();
    $('#addBookForm')[0].reset();
}

// Close modal when clicking outside
$(window).on('click', function(e) {
    if (e.target.id === 'addBookModal') {
        closeAddBookModal();
    }
});

// Close modal with Escape key
$(document).on('keydown', function(e) {
    if (e.key === 'Escape') {
        closeAddBookModal();
    }
});

// Utility functions
function showNotification(message, type = 'info') {
    var notification = $(`
        <div class="notification notification-${type}">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `);
    
    $('body').append(notification);
    
    setTimeout(function() {
        notification.fadeOut(function() {
            notification.remove();
        });
    }, 5000);
    
    notification.find('.notification-close').on('click', function() {
        notification.fadeOut(function() {
            notification.remove();
        });
    });
}

// Format dates
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Confirm actions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}