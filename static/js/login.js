// Function to show alert message
function showAlert(message, type = 'danger') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.getElementById('alertContainer');
    if (container) {
        // Clear existing alerts
        container.innerHTML = '';
        container.appendChild(alertDiv);
        
        // Auto-remove alert after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const usernameInput = document.getElementById('username');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Reset validation
            this.classList.remove('was-validated');
            
            // Validate form
            if (!this.checkValidity()) {
                e.stopPropagation();
                this.classList.add('was-validated');
                return;
            }
            
            const username = usernameInput.value.trim();
            
            // Disable button and show loading state
            if (loginBtn) {
                loginBtn.disabled = true;
                loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Continuing...';
            }
            
            try {
                // Submit the form directly to let the server handle the redirect
                loginForm.submit();
            } catch (error) {
                console.error('Login error:', error);
                showAlert('An error occurred. Please try again later.');
            } finally {
                // Re-enable button
                if (loginBtn) {
                    loginBtn.disabled = false;
                    loginBtn.innerHTML = '<i class="bi bi-box-arrow-in-right me-2"></i>Continue';
                }
            }
        });
    }
    
    // Handle Enter key to submit form
    if (usernameInput) {
        usernameInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                loginForm.dispatchEvent(new Event('submit'));
            }
        });
    }
    
    // Focus on username field when page loads
    if (usernameInput) {
        usernameInput.focus();
    }
});
