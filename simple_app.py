from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'dev-key-for-testing'  # Change in production

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple User class
class User(UserMixin):
    def __init__(self, user_id, username, role='user'):
        self.id = user_id
        self.username = username
        self.role = role

# In-memory user database (for testing)
users_db = {
    'admin': {'password': generate_password_hash('admin123'), 'id': 1, 'role': 'admin'},
    'user': {'password': generate_password_hash('user123'), 'id': 2, 'role': 'user'}
}

@login_manager.user_loader
def load_user(user_id):
    for username, user in users_db.items():
        if str(user['id']) == str(user_id):
            return User(user_id=user['id'], username=username, role=user['role'])
    return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return f'''
            <h1>Welcome, {current_user.username}!</h1>
            <p>Role: {current_user.role}</p>
            <a href="{url_for('dashboard')}">Go to Dashboard</a> | 
            <a href="{url_for('logout')}">Logout</a>
            <script>
                // Test the check-auth endpoint
                fetch('/api/check-auth')
                    .then(response => response.json())
                    .then(data => console.log('Auth check:', data))
                    .catch(err => console.error('Auth check failed:', err));
            </script>
        '''
    return f'''
        <h1>Welcome to Simple App</h1>
        <a href="{url_for('login')}">Login</a>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = users_db.get(username)
        if user_data and check_password_hash(user_data['password'], password or ''):
            user = User(user_id=user_data['id'], username=username, role=user_data['role'])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password", 401
    
    return '''
        <h1>Login</h1>
        <form method="post">
            <div>
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div>
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        <p>Try with admin/admin123 or user/user123</p>
    '''

@app.route('/dashboard')
@login_required
def dashboard():
    return f'''
        <h1>Dashboard</h1>
        <p>Welcome, {current_user.username}!</p>
        <p>Your role is: {current_user.role}</p>
        <a href="{url_for('index')}">Home</a> | 
        <a href="{url_for('logout')}">Logout</a>
    '''

@app.route('/api/check-auth')
def check_auth():
    print("Auth check called")
    if current_user.is_authenticated:
        return {'authenticated': True, 'username': current_user.username, 'role': current_user.role}
    return {'authenticated': False}

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
