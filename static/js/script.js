// Application initialization and utility functions
'use strict';

// Global state
let currentUser = null;

// Helper function to safely get elements
function getElement(selector, parent = document) {
    return parent.querySelector(selector);
}

// Show error message
function showError(message) {
    const alertContainer = document.getElementById('alertContainer') || 
                         document.getElementById('loginAlert') ||
                         document.body;
    
    if (alertContainer) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
        
        // Remove any existing alerts first
        const existingAlerts = alertContainer.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Add the new alert
        alertContainer.prepend(alertDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    } else {
        alert(`Error: ${message}`);
    }
}

// Show success message
function showSuccess(message) {
    const alertContainer = document.getElementById('alertContainer') || 
                         document.getElementById('loginAlert') ||
                         document.body;
    
    if (alertContainer) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
        
        // Remove any existing alerts first
        const existingAlerts = alertContainer.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Add the new alert
        alertContainer.prepend(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    } else {
        alert(`Success: ${message}`);
    }
}

// Initialize login form
function initLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;
    
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    // Toggle password visibility
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-eye');
                icon.classList.toggle('fa-eye-slash');
            }
        });
    }
    
    // Form submission
    loginForm.addEventListener('submit', function(e) {
        const username = this.querySelector('input[name="username"]');
        const password = this.querySelector('input[name="password"]');
        const submitBtn = this.querySelector('button[type="submit"]');
        let isValid = true;
        
        // Reset previous errors
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        
        // Validate username
        if (!username.value.trim()) {
            username.classList.add('is-invalid');
            const error = document.createElement('div');
            error.className = 'error-message';
            error.textContent = 'Username is required';
            username.parentNode.insertBefore(error, username.nextSibling);
            isValid = false;
        }
        
        // Validate password
        if (!password.value) {
            password.classList.add('is-invalid');
            const error = document.createElement('div');
            error.className = 'error-message';
            error.textContent = 'Password is required';
            password.parentNode.insertBefore(error, password.nextSibling);
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
            return false;
        }
        
        // Show loading state
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Signing in...';
            
            // Revert button state if form submission fails
            setTimeout(() => {
                if (document.body.contains(submitBtn)) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }, 10000);
        }
        
        return true;
    });
}

// Initialize logout functionality
function initLogout() {
    document.addEventListener('click', function(e) {
        const logoutBtn = e.target.closest('[data-logout]');
        
        if (logoutBtn) {
            e.preventDefault();
            
            // Show loading state
            const originalText = logoutBtn.innerHTML;
            if (logoutBtn.querySelector) {
                const spinner = document.createElement('span');
                spinner.className = 'spinner-border spinner-border-sm me-1';
                spinner.setAttribute('role', 'status');
                spinner.setAttribute('aria-hidden', 'true');
                logoutBtn.innerHTML = '';
                logoutBtn.appendChild(spinner);
                logoutBtn.appendChild(document.createTextNode(' Logging out...'));
                logoutBtn.disabled = true;
            }
            
            // Perform logout
            fetch('/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    window.location.href = '/';
                }
            })
            .catch(error => {
                console.error('Logout error:', error);
                if (logoutBtn.querySelector) {
                    logoutBtn.innerHTML = originalText;
                    logoutBtn.disabled = false;
                }
                showError('Logout failed. Please try again.');
            });
        }
    });
}

// Initialize tab functionality
function initTabs() {
    const dashboardTabs = document.getElementById('dashboard-tabs');
    if (!dashboardTabs) return;
    
    const tabButtons = document.querySelectorAll('.nav-tabs .nav-link');
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const tabId = e.target.getAttribute('data-tab');
            if (tabId) {
                // Hide all tab content
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.style.display = 'none';
                });
                // Show selected tab content
                const selectedTab = document.getElementById(tabId);
                if (selectedTab) {
                    selectedTab.style.display = 'block';
                }
            }
        });
        
        // Click the first tab by default
        if (tabButtons.length > 0) {
            tabButtons[0].click();
        }
    });
}

// Initialize modal functionality
function initModals() {
    const closeBtn = document.querySelector('.close');
    const modal = document.querySelector('#successModal');

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
}

// Main initialization function
function init() {
    initLoginForm();
    initLogout();
    initTabs();
    initModals();
}

// Initialize the application when the DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
