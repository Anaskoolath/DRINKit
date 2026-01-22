// Credentials validation
const VALID_USERNAME = 'anashere'
const VALID_PASSWORD = '1323';

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    const signInBtn = document.getElementById('sign-in-btn');
    
    if (signInBtn) {
        signInBtn.addEventListener('click', function() {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const errorDiv = document.getElementById('error-message');
            
            console.log('Button clicked!');
            console.log('Username:', username);
            console.log('Password:', password);
            
            // Validate credentials
            if (username === VALID_USERNAME && password === VALID_PASSWORD) {
                console.log('Login successful!');
                // Success - redirect to about page
                errorDiv.style.display = 'none';
                setTimeout(() => {
                    window.location.href = "{% url 'home' %}";
                }, 500);
            } else {
                console.log('Login failed!');
                // Error - show error message
                errorDiv.textContent = '❌ Invalid username or password. Please try again.';
                errorDiv.style.display = 'block';
                
                // Add shake animation
                errorDiv.classList.add('shake');
                setTimeout(() => {
                    errorDiv.classList.remove('shake');
                }, 500);
                
                // Clear password field
                document.getElementById('password').value = '';
            }
        });
    } else {
        console.error('Sign in button not found!');
    }
});