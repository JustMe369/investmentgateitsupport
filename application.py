from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, current_app, Response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm
import sqlite3
import os
import csv
import io
from datetime import datetime, timedelta
from functools import wraps
import re
from flask_mail import Mail, Message

app = Flask(__name__)

# Generate a secure secret key if it doesn't exist
secret_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret_key.txt')
if not os.path.exists(secret_key_file):
    with open(secret_key_file, 'w') as f:
        f.write(os.urandom(24).hex())

with open(secret_key_file, 'r') as f:
    app.secret_key = f.read().encode()

# Configure session to work with secure cookies
app.config.update(
    # Session settings
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_REFRESH_EACH_REQUEST=True,
    
    # Flask-Login settings
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_DURATION=timedelta(days=30),
    REMEMBER_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    REMEMBER_COOKIE_SAMESITE='Lax',
    
    # CSRF Protection
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_TIME_LIMIT=3600
)

# Add datetimeformat filter
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if not value:
        return ""
    
    # If it's already a datetime object
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    
    # If it's a string, try to parse it
    if isinstance(value, str):
        try:
            # Try ISO format first
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime(format)
        except (ValueError, AttributeError):
            try:
                # Try SQLite's datetime format
                from dateutil import parser
                dt = parser.parse(value)
                return dt.strftime(format)
            except:
                return value  # Return as is if parsing fails
    
    return str(value)  # Fallback to string representation

# Add now() function to Jinja2 environment
app.jinja_env.globals['now'] = datetime.now

app.jinja_env.filters['datetimeformat'] = datetimeformat

def nl2br(value):
    """Converts newlines in text to HTML line breaks"""
    if value is None:
        return ''
    return value.replace('\n', '<br>')

app.jinja_env.filters['nl2br'] = nl2br

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Configure SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'basic'  # Changed from 'strong' to 'basic' to prevent redirect loops
login_manager.refresh_view = 'login'  # The view to redirect to when the user needs to re-authenticate
login_manager.needs_refresh_message = (u"Session timed out, please re-login")
login_manager.needs_refresh_message_category = "info"

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if not user:
        return None
    return User(user['id'], user['username'], user['role'])

def role_required(role_required=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return app.login_manager.unauthorized()
                
            # Admin has access to everything
            if current_user.role == 'admin':
                return fn(*args, **kwargs)
                
            # Special handling for open tickets role
            if current_user.role == 'opentickets':
                # Only allow access to view_ticket and tickets routes
                if fn.__name__ not in ['view_ticket', 'tickets']:
                    flash('You only have permission to view open tickets.', 'danger')
                    return redirect(url_for('tickets'))
                return fn(*args, **kwargs)
                
            # Normal role check for other roles
            if role_required and current_user.role != role_required:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
                
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/simple-login')
def simple_login():
    return render_template('login_simple.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("\n=== Login Route Started ===")
    
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        print("User already authenticated, redirecting to dashboard")
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    next_page = request.args.get('next', '')
    
    # Security: Only allow relative URLs
    if next_page and not next_page.startswith('/'):
        next_page = ''
    
    if request.method == 'POST':
        print("\n=== POST Request Received ===")
        print(f"Form data: {request.form}")
        
        if form.validate():
            print("Form validation passed")
            username = form.username.data.strip()
            password = form.password.data
            
            try:
                conn = get_db_connection()
                user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                
                if user and check_password_hash(user['password'], password):
                    print(f"User found: {user['username']} (ID: {user['id']})")
                    user_obj = User(user['id'], user['username'], user['role'])
                    
                    # Log in the user
                    login_user(user_obj, remember=form.remember_me.data)
                    session.permanent = True
                    
                    print("Login successful, redirecting to dashboard")
                    return redirect(next_page or url_for('dashboard'))
                else:
                    print("Invalid username or password")
                    flash('Invalid username or password', 'danger')
                    
            except Exception as e:
                print(f"Login error: {str(e)}")
                flash('An error occurred during login. Please try again.', 'danger')
                
            finally:
                if 'conn' in locals() and conn:
                    conn.close()
        else:
            print(f"Form validation failed: {form.errors}")
            flash('Please correct the errors in the form.', 'danger')
    
    return render_template('login.html', form=form, next=next_page)

@app.route('/minimal-dashboard')
@login_required
def minimal_dashboard():
    """A minimal dashboard for testing purposes"""
    stats = {
        'open_tickets': 0,
        'in_progress_tickets': 0,
        'resolved_tickets': 0,
        'total_equipment': 0
    }
    recent_tickets = []
    
    try:
        conn = get_db_connection()
        
        # Get ticket counts
        stats['open_tickets'] = conn.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'Open'").fetchone()['count'] or 0
        stats['in_progress_tickets'] = conn.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'In Progress'").fetchone()['count'] or 0
        stats['resolved_tickets'] = conn.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'Resolved'").fetchone()['count'] or 0
        
        # Get recent tickets
        recent_tickets = conn.execute('''
            SELECT id, title, status, created_at 
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 5
        ''').fetchall() or []
        
        # Get equipment count
        stats['total_equipment'] = conn.execute("SELECT COUNT(*) as count FROM equipment").fetchone()['count'] or 0
        
        conn.close()
        
    except Exception as e:
        print(f"Error in minimal_dashboard: {e}")
        if 'conn' in locals():
            conn.close()
    
    return render_template('minimal_dashboard.html', 
                         stats=stats,
                         recent_tickets=recent_tickets)

@app.route('/dashboard')
def dashboard():
    # Debug session and authentication status
    print("\n=== Dashboard Route ===")
    print(f"Session ID: {session.get('_id')}")
    print(f"User authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        print(f"Current user: {current_user.username} (ID: {current_user.id}, Role: {current_user.role})")
    else:
        print("No authenticated user, redirecting to login")
        return redirect(url_for('login'))
    
    print("User is authenticated, proceeding with dashboard...")
    
    conn = None
    try:
        conn = get_db_connection()
        
        # Initialize stats with default values
        stats = {
            'open_tickets': 0,
            'in_progress_tickets': 0,
            'resolved_tickets': 0,
            'closed_tickets': 0,
            'total_tickets': 0,
            'total_users': 0,
            'total_equipment': 0
        }
        
        recent_tickets = []
        
        # Check if tables exist
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("Existing tables:", tables)  # Debug log
        
        # Get ticket counts with error handling for missing tables
        if 'tickets' in tables:
            try:
                stats['open_tickets'] = conn.execute(
                    "SELECT COUNT(*) as count FROM tickets WHERE status = 'Open'"
                ).fetchone()['count'] or 0
                stats['in_progress_tickets'] = conn.execute(
                    "SELECT COUNT(*) as count FROM tickets WHERE status = 'In Progress'"
                ).fetchone()['count'] or 0
                stats['resolved_tickets'] = conn.execute(
                    "SELECT COUNT(*) as count FROM tickets WHERE status = 'Resolved'"
                ).fetchone()['count'] or 0
                stats['closed_tickets'] = conn.execute(
                    "SELECT COUNT(*) as count FROM tickets WHERE status = 'Closed'"
                ).fetchone()['count'] or 0
                stats['total_tickets'] = conn.execute(
                    "SELECT COUNT(*) as count FROM tickets"
                ).fetchone()['count'] or 0
            except Exception as e:
                print(f"Error getting ticket stats: {e}")
                
        # Get user count
        if 'users' in tables:
            try:
                stats['total_users'] = conn.execute(
                    "SELECT COUNT(*) as count FROM users"
                ).fetchone()['count'] or 0
            except Exception as e:
                print(f"Error getting user count: {e}")
        
        # Get equipment count
        if 'equipment' in tables:
            try:
                stats['total_equipment'] = conn.execute(
                    "SELECT COUNT(*) as count FROM equipment"
                ).fetchone()['count'] or 0
            except Exception as e:
                print(f"Error getting equipment count: {e}")
        
        # Get recent tickets (simplified for now)
        if 'tickets' in tables:
            try:
                recent_tickets = conn.execute('''
                    SELECT * FROM tickets 
                    ORDER BY created_at DESC 
                    LIMIT 5
                ''').fetchall()
            except Exception as e:
                print(f"Error getting recent tickets: {e}")
        
        # Prepare the stats dictionary with all required values
        stats = {
            'total_tickets': stats['total_tickets'],
            'open_tickets': stats['open_tickets'],
            'in_progress_tickets': stats['in_progress_tickets'],
            'resolved_tickets': stats['resolved_tickets'],
            'closed_tickets': stats['closed_tickets'],
            'total_users': stats['total_users'],
            'total_equipment': stats['total_equipment']
        }
        
        # Initialize default values
        users = []
        statuses = []
        priorities = []
        current_filters = {
            'status': '',
            'priority': '',
            'assigned_to': '',
            'sort_by': 'created_at',
            'sort_order': 'desc'
        }
        
        # Get users if table exists
        if 'users' in tables:
            try:
                users = conn.execute('SELECT id, username FROM users').fetchall()
            except Exception as e:
                print(f"Error fetching users: {e}")
        
        # Get statuses and priorities if tickets table exists
        if 'tickets' in tables:
            try:
                statuses = conn.execute("SELECT DISTINCT status FROM tickets").fetchall()
                priorities = conn.execute("SELECT DISTINCT priority FROM tickets").fetchall()
            except Exception as e:
                print(f"Error fetching ticket data: {e}")
        
        # Prepare template context
        context = {
            'stats': stats,
            'recent_tickets': recent_tickets or [],
            'current_filters': current_filters,
            'users': users,
            'statuses': statuses,
            'priorities': priorities
        }
        
        return render_template('dashboard.html', **context)
                               
    except Exception as e:
        print(f"Error in dashboard route: {e}")
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('index'))
    finally:
        if conn:
            conn.close()

@app.route('/dashboard/opentickets')
@login_required
@role_required('opentickets')
def open_tickets_dashboard():
    try:
        conn = get_db_connection()
        
        # Get user's location if available
        user_location = None
        if current_user.location_id:
            user_location = conn.execute(
                'SELECT * FROM locations WHERE id = ?', 
                (current_user.location_id,)
            ).fetchone()
        
        # Get ticket statistics
        stats = {}
        
        # Total open tickets
        stats['open_tickets'] = conn.execute(
            'SELECT COUNT(*) as count FROM tickets WHERE status = "Open"'
        ).fetchone()['count']
        
        # Tickets assigned to current user
        stats['assigned_tickets'] = conn.execute(
            'SELECT COUNT(*) as count FROM tickets WHERE assigned_to = ? AND status = "Open"',
            (current_user.id,)
        ).fetchone()['count']
        
        # High priority tickets
        stats['high_priority'] = conn.execute(
            'SELECT COUNT(*) as count FROM tickets WHERE priority = "High" AND status = "Open"'
        ).fetchone()['count']
        
        # Tickets for user's location
        if current_user.location_id:
            stats['location_tickets'] = conn.execute(
                'SELECT COUNT(*) as count FROM tickets WHERE location_id = ? AND status = "Open"',
                (current_user.location_id,)
            ).fetchone()['count']
        else:
            stats['location_tickets'] = 0
        
        # Get recent open tickets
        recent_tickets = conn.execute('''
            SELECT t.*, u1.username as created_by_username, u2.username as assigned_to_username
            FROM tickets t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.assigned_to = u2.id
            WHERE t.status = 'Open'
            ORDER BY t.priority DESC, t.created_at DESC
            LIMIT 5
        ''').fetchall()
        
        conn.close()
        
        # Check for partial request (AJAX)
        if request.args.get('partial') == '1':
            tickets_html = render_template('partials/dashboard_opentickets_tickets.html', tickets=recent_tickets)
            return jsonify({
                'stats': stats,
                'tickets_html': tickets_html
            })
        
        return render_template('dashboard_opentickets.html',
                            open_tickets_count=stats['open_tickets'],
                            assigned_tickets_count=stats['assigned_tickets'],
                            high_priority_count=stats['high_priority'],
                            location_tickets_count=stats['location_tickets'],
                            recent_tickets=recent_tickets,
                            user_location=user_location,
                            stats=stats)
                            
    except Exception as e:
        print(f"Error in open_tickets_dashboard: {e}")
        if request.args.get('partial') == '1':
            return jsonify({'error': 'Failed to update dashboard'}), 500
        flash('An error occurred while loading the dashboard', 'error')
        return redirect(url_for('index'))

@app.route('/tickets')
@login_required
def tickets():
    # Check if this is a partial request (for auto-refresh)
    is_partial = request.args.get('partial') == '1'
    
    # Check if user has permission to view all tickets
    is_admin = current_user.role == 'admin'
    
    # Pagination settings
    per_page = 10
    page = request.args.get('page', 1, type=int)
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    assigned_to_filter = request.args.get('assigned_to', '')
    search_term = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Initialize current_filters with default values
    current_filters = {
        'status': status_filter,
        'priority': priority_filter,
        'assigned_to': assigned_to_filter,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'search': search_term
    }
    
    conn = get_db_connection()
    
    # Get all possible values for filters
    statuses = [row['status'] for row in conn.execute("SELECT DISTINCT status FROM tickets").fetchall()]
    priorities = [row['priority'] for row in conn.execute("SELECT DISTINCT priority FROM tickets").fetchall()]
    users = [dict(row) for row in conn.execute("SELECT id, username FROM users").fetchall()]
    
    # Base query for counting
    count_query = 'SELECT COUNT(*) as count FROM tickets t'
    
    # Base query for getting tickets
    base_query = '''
        SELECT t.*, u1.username as created_by_username, u2.username as assigned_to_username
        FROM tickets t
        LEFT JOIN users u1 ON t.created_by = u1.id
        LEFT JOIN users u2 ON t.assigned_to = u2.id
    '''
    
    # Initialize where clauses and parameters
    where_clause = []
    query_params = []
    
    # For 'opentickets' role, only show open tickets
    # Admins can see all tickets regardless of status
    if current_user.role == 'opentickets':
        where_clause.append("t.status = 'Open'")
    
    # Handle search and filters
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    assigned_to_filter = request.args.get('assigned_to', '')
    search_term = request.args.get('search', '').strip()
    
    # Apply status filter
    if status_filter:
        where_clause.append("t.status = ?")
        query_params.append(status_filter)
    
    # Apply priority filter
    if priority_filter:
        where_clause.append("t.priority = ?")
        query_params.append(priority_filter)
    
    # Apply assigned_to filter
    if assigned_to_filter:
        where_clause.append("t.assigned_to = ?")
        query_params.append(int(assigned_to_filter))
        
    # Add search functionality
    if search_term:
        search_param = f"%{search_term}%"
        where_clause.append("(t.title LIKE ? OR t.description LIKE ?)")
        query_params.extend([search_param, search_param])
    
    # Build WHERE clause if we have any conditions
    where_clause_str = ''
    if where_clause:
        where_clause_str = ' WHERE ' + ' AND '.join(where_clause)
    
    # Get total count with filters applied
    count_result = conn.execute(count_query + where_clause_str, query_params).fetchone()
    total_tickets = count_result['count'] if count_result else 0
    total_pages = (total_tickets + per_page - 1) // per_page if total_tickets > 0 else 1
    
    # Validate page number
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate offset for pagination
    offset = (page - 1) * per_page
    
    # Add pagination to query
    order_limit = ' ORDER BY t.created_at DESC LIMIT ? OFFSET ?'
    query = base_query + where_clause_str + order_limit
    
    # Execute the query with all parameters
    tickets = conn.execute(query, query_params + [per_page, offset]).fetchall()
    
    # Convert Row objects to dict for JSON serialization if needed
    tickets_data = [dict(ticket) for ticket in tickets]
    
    conn.close()
    
    # For Open Tickets view with opentickets role
    if current_user.role == 'opentickets' and not is_partial:
        return render_template('open_tickets.html', 
                            tickets=tickets_data,
                            current_page=page,
                            total_pages=total_pages or 1,
                            total_tickets=total_tickets)
    
    # For partial requests (AJAX)
    if is_partial:
        if current_user.role == 'opentickets':
            return render_template('partials/open_tickets_list.html', 
                                tickets=tickets_data,
                                current_page=page,
                                total_pages=total_pages or 1)
        else:
            return render_template('partials/tickets_list.html', 
                                tickets=tickets_data,
                                current_page=page,
                                total_pages=total_pages or 1)
    
    # Prepare context for template
    context = {
        'tickets': tickets_data,
        'current_page': page,
        'total_pages': total_pages or 1,
        'total_tickets': total_tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'assigned_to_filter': assigned_to_filter,
        'current_filters': {
            'status': status_filter,
            'priority': priority_filter,
            'assigned_to': assigned_to_filter,
            'sort_by': sort_by,
            'sort_order': sort_order
        },
        'statuses': statuses,
        'priorities': priorities,
        'users': users,
        'search_term': search_term,
        'sort_by': sort_by,
        'sort_order': sort_order
    }
    
    # Regular tickets view for other roles
    return render_template('tickets.html', **context)

# ... (rest of the code remains the same)
from datetime import datetime, timedelta

@app.route('/export-tickets')
@login_required
def export_tickets():
    try:
        # Get filter parameters from query string
        status_filter = request.args.get('status', '')
        priority_filter = request.args.get('priority', '')
        assigned_to_filter = request.args.get('assigned_to', '')
        search_term = request.args.get('search', '').strip()
        
        conn = get_db_connection()
        
        # Base query for getting tickets
        query = '''
            SELECT t.id, t.title, t.description, t.status, t.priority, 
                   t.created_at, t.updated_at, t.due_date,
                   u1.username as created_by, u2.username as assigned_to
            FROM tickets t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.assigned_to = u2.id
        '''
        
        # Initialize where clauses and parameters
        where_clause = []
        query_params = []
        
        # Apply filters
        if status_filter:
            where_clause.append("t.status = ?")
            query_params.append(status_filter)
            
        if priority_filter:
            where_clause.append("t.priority = ?")
            query_params.append(priority_filter)
            
        if assigned_to_filter:
            where_clause.append("t.assigned_to = ?")
            query_params.append(int(assigned_to_filter))
            
        if search_term:
            search_param = f"%{search_term}%"
            where_clause.append("(t.title LIKE ? OR t.description LIKE ?)")
            query_params.extend([search_param, search_param])
        
        # For 'opentickets' role, only show open tickets
        if current_user.role == 'opentickets':
            where_clause.append("t.status = 'Open'")
        
        # Build WHERE clause if we have any conditions
        if where_clause:
            query += ' WHERE ' + ' AND '.join(where_clause)
        
        # Execute the query
        tickets = conn.execute(query, query_params).fetchall()
        conn.close()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Title', 'Description', 'Status', 'Priority',
            'Created At', 'Updated At', 'Due Date', 'Created By', 'Assigned To'
        ])
        
        # Write data
        for ticket in tickets:
            writer.writerow([
                ticket['id'],
                ticket['title'],
                ticket['description'] or '',
                ticket['status'],
                ticket['priority'],
                ticket['created_at'],
                ticket['updated_at'],
                ticket['due_date'] or '',
                ticket['created_by'] or '',
                ticket['assigned_to'] or ''
            ])
        
        # Prepare response
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=tickets_export_{timestamp}.csv"}
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exporting tickets: {str(e)}")
        flash('An error occurred while exporting tickets', 'error')
        return redirect(url_for('tickets'))

@app.route('/tickets/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    conn = get_db_connection()
    
    # Get the ticket details with location and user information
    ticket = conn.execute('''
        SELECT t.*, 
               u1.username as created_by_username, 
               u2.username as assigned_to_username,
               u1.email as created_by_email,
               u2.email as assigned_to_email,
               l.id as location_id,
               l.name as location_name,
               l.address as location_address
        FROM tickets t
        LEFT JOIN users u1 ON t.created_by = u1.id
        LEFT JOIN users u2 ON t.assigned_to = u2.id
        LEFT JOIN locations l ON t.location_id = l.id
        WHERE t.id = ?
    ''', (ticket_id,)).fetchone()
    
    if ticket is None:
        conn.close()
        flash('Ticket not found', 'danger')
        return redirect(url_for('tickets'))
    
    # Convert ticket to dict and parse datetime fields
    ticket_dict = dict(ticket)
    for field in ['created_at', 'updated_at']:
        if field in ticket_dict and ticket_dict[field]:
            if isinstance(ticket_dict[field], str):
                try:
                    ticket_dict[field] = datetime.fromisoformat(ticket_dict[field].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # If parsing fails, keep the original value
                    pass
    
    # Add location information to the ticket dict if it exists
    if ticket_dict.get('location_id'):
        ticket_dict['location'] = {
            'id': ticket_dict.pop('location_id'),
            'name': ticket_dict.pop('location_name', ''),
            'address': ticket_dict.pop('location_address', '')
        }
    
    # Get ticket comments with user info
    comments = []
    raw_comments = conn.execute('''
        SELECT c.*, u.username, u.full_name,
               u.id as user_id, u.email as user_email
        FROM ticket_comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.ticket_id = ?
        ORDER BY c.created_at ASC
    ''', (ticket_id,)).fetchall()
    
    # Process comments to ensure proper datetime objects and structure
    for comment in raw_comments:
        comment_dict = dict(comment)
        if 'created_at' in comment_dict and comment_dict['created_at']:
            if isinstance(comment_dict['created_at'], str):
                try:
                    comment_dict['created_at'] = datetime.fromisoformat(comment_dict['created_at'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # If parsing fails, keep the original value
                    pass
        
        # Ensure user object is properly structured for the template
        comment_dict['user'] = {
            'id': comment_dict.pop('user_id'),
            'username': comment_dict.pop('username'),
            'full_name': comment_dict.pop('full_name'),
            'email': comment_dict.pop('user_email', '')
        }
        comments.append(comment_dict)
    
    # Get all users for assignment dropdown
    users = conn.execute('SELECT id, username, full_name FROM users ORDER BY username').fetchall()
    
    conn.close()
    
    return render_template('ticket.html', 
                         ticket=ticket_dict, 
                         comments=comments,
                         users=users,
                         statuses=['Open', 'In Progress', 'Resolved', 'Closed'],
                         priorities=['Low', 'Medium', 'High', 'Critical'])

@app.route('/tickets/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_ticket():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'Medium')
        location_id = request.form.get('location_id')
        
        if not title or not description:
            flash('Title and description are required', 'danger')
            return redirect(url_for('create_ticket'))
            
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO tickets (title, description, status, priority, created_by, location_id)
            VALUES (?, ?, 'Open', ?, ?, ?)
        ''', (title, description, priority, current_user.id, location_id))
        conn.commit()
        conn.close()
        
        flash('Ticket created successfully!', 'success')
        return redirect(url_for('tickets'))
    
    # For GET request, load locations and equipment to display in the form
    conn = get_db_connection()
    locations = conn.execute('SELECT id, name, address FROM locations ORDER BY name').fetchall()
    equipment_list = conn.execute('''
        SELECT e.id, e.device_type, e.model, e.serial_number, l.name as location_name 
        FROM equipment e 
        LEFT JOIN locations l ON e.location_id = l.id 
        ORDER BY e.device_type, e.model
    ''').fetchall()
    conn.close()
    
    return render_template('create_ticket.html', 
                         locations=locations, 
                         equipment_list=equipment_list)

@app.route('/tickets/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_ticket(ticket_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        priority = request.form.get('priority')
        
        if not title or not description:
            flash('Title and description are required', 'danger')
            return redirect(url_for('edit_ticket', ticket_id=ticket_id))
            
        conn.execute('''
            UPDATE tickets 
            SET title = ?, description = ?, status = ?, priority = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, description, status, priority, ticket_id))
        conn.commit()
        conn.close()
        
        flash('Ticket updated successfully!', 'success')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    # GET request - load the ticket data
    ticket = conn.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    if not ticket:
        conn.close()
        flash('Ticket not found', 'danger')
        return redirect(url_for('tickets'))
    
    conn.close()
    return render_template('edit_ticket.html', ticket=ticket)

@app.route('/tickets/<int:ticket_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_ticket(ticket_id):
    conn = get_db_connection()
    try:
        # Delete related comments first due to foreign key constraint
        conn.execute('DELETE FROM ticket_comments WHERE ticket_id = ?', (ticket_id,))
        # Delete the ticket
        conn.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        conn.commit()
        flash('Ticket deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error deleting ticket', 'danger')
        app.logger.error(f'Error deleting ticket {ticket_id}: {str(e)}')
    finally:
        conn.close()
    return redirect(url_for('tickets'))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # Log the user out
    logout_user()
    
    # Clear the session completely
    session.clear()
    
    # If it's an AJAX request, return a success response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'redirect': url_for('login')})
    
    # Otherwise, redirect to the login page
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle profile update
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        
        # Handle password change if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        conn = get_db_connection()
        try:
            if current_password and new_password:
                # Verify current password
                user = conn.execute('SELECT password FROM users WHERE id = ?', (current_user.id,)).fetchone()
                if user and check_password_hash(user['password'], current_password):
                    # Update password
                    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
                    conn.execute('UPDATE users SET password = ? WHERE id = ?', 
                                (hashed_password, current_user.id))
                    flash('Password updated successfully!', 'success')
                else:
                    flash('Current password is incorrect', 'danger')
            
            # Update profile info
            conn.execute('''
                UPDATE users 
                SET full_name = ?, email = ?
                WHERE id = ?
            ''', (full_name, email, current_user.id))
            
            conn.commit()
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            conn.rollback()
            flash('An error occurred while updating your profile', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('profile'))
    
    # For GET request, just show the profile page
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    conn.close()
    
    return render_template('profile.html', user=user)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/equipment')
@login_required
def equipment():
    # Get filter parameters
    device_type = request.args.get('device_type', '')
    status = request.args.get('status', '')
    location_id = request.args.get('location_id', '')
    
    # Pagination settings
    per_page = 10
    page = request.args.get('page', 1, type=int)
    
    conn = get_db_connection()
    
    # Build the base query
    base_query = 'FROM equipment e LEFT JOIN locations l ON e.location_id = l.id'
    conditions = []
    params = []
    
    # Add filter conditions
    if device_type:
        conditions.append('e.device_type = ?')
        params.append(device_type)
    if status:
        conditions.append('e.status = ?')
        params.append(status.lower())  # Ensure status is lowercase
    if location_id and location_id.isdigit():
        conditions.append('e.location_id = ?')
        params.append(int(location_id))
    
    # Build WHERE clause if there are any conditions
    where_clause = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
    
    # Get total count for pagination with filters applied
    count_query = 'SELECT COUNT(*) as count ' + base_query + where_clause
    total_equipment = conn.execute(count_query, params).fetchone()['count']
    total_pages = (total_equipment + per_page - 1) // per_page if total_equipment > 0 else 1
    
    # Validate page number
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get paginated and filtered equipment list
    query = f'''
        SELECT e.*, l.name as location_name 
        {base_query}
        {where_clause}
        ORDER BY e.id DESC
        LIMIT ? OFFSET ?
    '''
    
    # Execute the query with all parameters
    equipment_list = conn.execute(query, params + [per_page, offset]).fetchall()
    
    # Get filter options for the form
    device_types = conn.execute('SELECT DISTINCT device_type FROM equipment ORDER BY device_type').fetchall()
    statuses = conn.execute('SELECT DISTINCT status FROM equipment ORDER BY status').fetchall()
    locations = conn.execute('SELECT id, name FROM locations ORDER BY name').fetchall()
    
    conn.close()
    
    # Current filters for the template
    current_filters = {
        'device_type': device_type,
        'status': status,
        'location_id': location_id
    }
    
    return render_template('equipment.html', 
                         equipment_list=equipment_list,
                         current_page=page,
                         total_pages=total_pages,
                         total_equipment=total_equipment,
                         device_types=device_types,
                         statuses=statuses,
                         locations=locations,
                         current_filters=current_filters)

@app.route('/equipment/<int:equipment_id>/maintenance', methods=['POST'])
@login_required
def add_maintenance(equipment_id):
    if request.method == 'POST':
        conn = None
        try:
            # Validate form data
            maintenance_type = request.form.get('maintenance_type')
            description = request.form.get('description', '').strip()
            date_performed = request.form.get('date_performed')
            
            if not all([maintenance_type, date_performed]):
                flash('Please fill in all required fields', 'danger')
                return redirect(url_for('view_equipment', equipment_id=equipment_id))
                
            conn = get_db_connection()
            
            # Verify equipment exists
            equipment = conn.execute('SELECT id FROM equipment WHERE id = ?', (equipment_id,)).fetchone()
            if not equipment:
                flash('Equipment not found', 'danger')
                return redirect(url_for('equipment'))
            
            # Insert maintenance record
            conn.execute('''
                INSERT INTO maintenance 
                (equipment_id, maintenance_type, description, date_performed, performed_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                equipment_id,
                maintenance_type,
                description,
                date_performed,
                current_user.id
            ))
            
            # Update equipment status if changed
            if 'update_status' in request.form and request.form['update_status'] == 'yes':
                conn.execute('''
                    UPDATE equipment 
                    SET status = 'In Use', 
                        updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (equipment_id,))
            
            conn.commit()
            flash('Maintenance record added successfully', 'success')
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            current_app.logger.error(f"Database error in add_maintenance: {str(e)}")
            flash('A database error occurred while adding the maintenance record', 'danger')
        except Exception as e:
            if conn:
                conn.rollback()
            current_app.logger.error(f"Error in add_maintenance: {str(e)}")
            flash('An error occurred while adding the maintenance record', 'danger')
        finally:
            if conn:
                conn.close()
    
    return redirect(url_for('view_equipment', equipment_id=equipment_id))

@app.route('/equipment/<int:equipment_id>')
@login_required
def view_equipment(equipment_id):
    conn = get_db_connection()
    
    # Get equipment details
    equipment = conn.execute('''
        SELECT e.*, l.name as location_name 
        FROM equipment e 
        LEFT JOIN locations l ON e.location_id = l.id
        WHERE e.id = ?
    ''', (equipment_id,)).fetchone()
    
    if not equipment:
        conn.close()
        flash('Equipment not found', 'danger')
        return redirect(url_for('equipment'))
    
    # Get maintenance history
    maintenance = conn.execute('''
        SELECT m.*, u.username as performed_by_username
        FROM maintenance m
        LEFT JOIN users u ON m.performed_by = u.id
        WHERE m.equipment_id = ?
        ORDER BY m.date_performed DESC
    ''', (equipment_id,)).fetchall()
    
    conn.close()
    
    return render_template('view_equipment.html',
                         equipment=dict(equipment),
                         maintenance=maintenance)

@app.route('/equipment/<int:equipment_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_equipment(equipment_id):
    conn = get_db_connection()
    try:
        # Check if equipment exists
        equipment = conn.execute('SELECT * FROM equipment WHERE id = ?', (equipment_id,)).fetchone()
        if not equipment:
            flash('Equipment not found', 'danger')
            return redirect(url_for('equipment'))
        
        # Delete maintenance records first (due to foreign key constraint)
        conn.execute('DELETE FROM maintenance WHERE equipment_id = ?', (equipment_id,))
        
        # Update any tickets that reference this equipment to set equipment_id to NULL
        conn.execute('UPDATE tickets SET equipment_id = NULL WHERE equipment_id = ?', (equipment_id,))
        
        # Now delete the equipment
        conn.execute('DELETE FROM equipment WHERE id = ?', (equipment_id,))
        
        conn.commit()
        flash('Equipment deleted successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting equipment: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('equipment'))

@app.route('/locations')
@login_required
def locations():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    conn = get_db_connection()
    
    # Get total count for pagination
    total = conn.execute('SELECT COUNT(*) as count FROM locations').fetchone()['count']
    
    # Get paginated locations
    locations = conn.execute('''
        SELECT l.*, COUNT(e.id) as equipment_count 
        FROM locations l 
        LEFT JOIN equipment e ON l.id = e.location_id 
        GROUP BY l.id
        ORDER BY l.name
        LIMIT ? OFFSET ?
    ''', (per_page, (page - 1) * per_page)).fetchall()
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    conn.close()
    
    return render_template(
        'locations.html',
        locations=locations,
        current_page=page,
        per_page=per_page,
        total_pages=total_pages,
        total=total,
        pages=((total - 1) // per_page) + 1
    )

@app.route('/locations/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_location():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact_person = request.form.get('contact_person')
        contact_phone = request.form.get('contact_phone')
        anydesk_id = request.form.get('anydesk_id')
        
        if not all([name, address, contact_person, contact_phone]):
            flash('Name, address, contact person, and phone are required', 'danger')
            return redirect(url_for('add_location'))
            
        conn = get_db_connection()
        try:
            conn.execute(
                '''INSERT INTO locations 
                   (name, address, contact_person, contact_phone, anydesk_id)
                   VALUES (?, ?, ?, ?, ?)''',
                (name, address, contact_person, contact_phone, anydesk_id or None)
            )
            conn.commit()
            flash('Location added successfully', 'success')
            return redirect(url_for('locations'))
        except sqlite3.IntegrityError:
            flash('A location with this name already exists', 'danger')
        finally:
            conn.close()
    
    return render_template('add_location.html')

@app.route('/locations/<int:location_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_location(location_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact_person = request.form.get('contact_person')
        contact_phone = request.form.get('contact_phone')
        anydesk_id = request.form.get('anydesk_id')
        
        if not all([name, address, contact_person, contact_phone]):
            flash('Name, address, contact person, and phone are required', 'danger')
            return redirect(url_for('edit_location', location_id=location_id))
            
        try:
            conn.execute('''
                UPDATE locations 
                SET name = ?, address = ?, contact_person = ?, 
                    contact_phone = ?, anydesk_id = ?
                WHERE id = ?
            ''', (name, address, contact_person, contact_phone, anydesk_id or None, location_id))
            
            conn.commit()
            flash('Location updated successfully', 'success')
            return redirect(url_for('view_location', location_id=location_id))
            
        except sqlite3.IntegrityError:
            flash('A location with this name already exists', 'danger')
            return redirect(url_for('edit_location', location_id=location_id))
    
    # GET request - show edit form
    location = conn.execute('SELECT * FROM locations WHERE id = ?', (location_id,)).fetchone()
    
    # Get equipment count for the location
    equipment_count = conn.execute('SELECT COUNT(*) as count FROM equipment WHERE location_id = ?', (location_id,)).fetchone()['count']
    
    # Get active tickets count for the location
    active_tickets = conn.execute('''
        SELECT COUNT(*) as count 
        FROM tickets 
        WHERE location_id = ? AND status IN ('Open', 'In Progress')
    ''', (location_id,)).fetchone()['count']
    
    conn.close()
    
    if not location:
        flash('Location not found', 'danger')
        return redirect(url_for('locations'))
    
    location_dict = dict(location)
    location_dict['equipment_count'] = equipment_count
    
    return render_template('edit_location.html', 
                         location=location_dict,
                         active_tickets_count=active_tickets)

@app.route('/locations/<int:location_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_location(location_id):
    conn = get_db_connection()
    
    try:
        # Check if there are any equipment or tickets associated with this location
        equipment_count = conn.execute('SELECT COUNT(*) as count FROM equipment WHERE location_id = ?', (location_id,)).fetchone()['count']
        tickets_count = conn.execute('SELECT COUNT(*) as count FROM tickets WHERE location_id = ?', (location_id,)).fetchone()['count']
        
        if equipment_count > 0 or tickets_count > 0:
            # Instead of deleting, we'll just unlink the location from equipment and tickets
            if equipment_count > 0:
                conn.execute('UPDATE equipment SET location_id = NULL WHERE location_id = ?', (location_id,))
            if tickets_count > 0:
                conn.execute('UPDATE tickets SET location_id = NULL WHERE location_id = ?', (location_id,))
            
            flash(f'Location was unlinked from {equipment_count} equipment and {tickets_count} tickets', 'warning')
        
        # Now delete the location
        conn.execute('DELETE FROM locations WHERE id = ?', (location_id,))
        conn.commit()
        
        flash('Location deleted successfully', 'success')
        return redirect(url_for('locations'))
        
    except Exception as e:
        conn.rollback()
        flash('An error occurred while deleting the location', 'danger')
        return redirect(url_for('view_location', location_id=location_id))
    finally:
        conn.close()

@app.route('/users')
@login_required
@role_required('admin')
def users():
    conn = get_db_connection()
    users_list = conn.execute('SELECT * FROM users ORDER BY username').fetchall()
    conn.close()
    return render_template('users.html', users=users_list)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        role = request.form.get('role', 'user')
        
        if not all([username, password, full_name, email]):
            flash('All fields are required', 'danger')
            return redirect(url_for('add_user'))
            
        conn = get_db_connection()
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            conn.execute(
                'INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)',
                (username, hashed_password, full_name, email, role)
            )
            conn.commit()
            flash('User added successfully', 'success')
            return redirect(url_for('users'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
        finally:
            conn.close()
    
    return render_template('add_user.html')

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user is None:
        conn.close()
        flash('User not found', 'danger')
        return redirect(url_for('users'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        role = request.form.get('role')
        
        try:
            if password:
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                conn.execute(
                    'UPDATE users SET username=?, password=?, full_name=?, email=?, role=? WHERE id=?',
                    (username, hashed_password, full_name, email, role, user_id)
                )
            else:
                conn.execute(
                    'UPDATE users SET username=?, full_name=?, email=?, role=? WHERE id=?',
                    (username, full_name, email, role, user_id)
                )
            conn.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('users'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
        
    conn.close()
    return render_template('edit_user.html', user=user)

@app.route('/equipment/<int:equipment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_equipment(equipment_id):
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            
            # Update equipment
            conn.execute('''
                UPDATE equipment SET
                    device_type = ?,
                    model = ?,
                    serial_number = ?,
                    status = ?,
                    location = ?,
                    assigned_to = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                request.form['device_type'],
                request.form['model'],
                request.form.get('serial_number', ''),
                request.form['status'],
                request.form.get('location', ''),
                request.form.get('assigned_to') or None,
                request.form.get('notes', ''),
                equipment_id
            ))
            
            conn.commit()
            conn.close()
            
            flash('Equipment updated successfully!', 'success')
            return redirect(url_for('view_equipment', equipment_id=equipment_id))
            
        except Exception as e:
            print(f"Error updating equipment: {e}")
            flash('An error occurred while updating the equipment. Please try again.', 'danger')
            if 'conn' in locals():
                conn.close()
            
    # GET request - show edit form
    try:
        conn = get_db_connection()
        equipment = conn.execute('SELECT * FROM equipment WHERE id = ?', (equipment_id,)).fetchone()
        users = conn.execute('SELECT id, username FROM users ORDER BY username').fetchall()
        conn.close()
        
        if not equipment:
            flash('Equipment not found.', 'danger')
            return redirect(url_for('equipment'))
            
        return render_template('edit_equipment.html', 
                            equipment=dict(equipment), 
                            users=users)
        
    except Exception as e:
        print(f"Error loading equipment for editing: {e}")
        flash('An error occurred while loading the equipment for editing.', 'danger')
        if 'conn' in locals():
            conn.close()
        return redirect(url_for('equipment'))

@app.route('/equipment/add', methods=['GET', 'POST'])
@login_required
def add_equipment():
    if request.method == 'POST':
        device_type = request.form.get('device_type')
        model = request.form.get('model')
        serial_number = request.form.get('serial_number')
        location_id = request.form.get('location_id')
        ip_address = request.form.get('ip_address')
        status = request.form.get('status', 'Active')
        
        if not all([device_type, model, serial_number]):
            flash('Device type, model, and serial number are required', 'danger')
            return redirect(url_for('add_equipment'))
            
        conn = get_db_connection()
        try:
            conn.execute(
                '''INSERT INTO equipment 
                   (device_type, model, serial_number, location_id, ip_address, status)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (device_type, model, serial_number, location_id or None, ip_address or None, status)
            )
            conn.commit()
            flash('Equipment added successfully', 'success')
            return redirect(url_for('equipment'))
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: equipment.serial_number' in str(e):
                flash('A device with this serial number already exists', 'danger')
            else:
                flash('An error occurred while adding the equipment', 'danger')
        finally:
            conn.close()
    
    # Get locations for dropdown
    conn = get_db_connection()
    locations = conn.execute('SELECT id, name FROM locations ORDER BY name').fetchall()
    conn.close()
    
    return render_template('add_equipment.html', locations=locations)

@app.route('/location/<int:location_id>')
@login_required
def view_location(location_id):
    # Pagination settings
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    conn = get_db_connection()
    
    # Get location details
    location = conn.execute('SELECT * FROM locations WHERE id = ?', (location_id,)).fetchone()
    if not location:
        flash('Location not found', 'danger')
        return redirect(url_for('locations'))
    
    # Get total equipment count for pagination
    total_equipment = conn.execute('''
        SELECT COUNT(*) as count 
        FROM equipment 
        WHERE location_id = ?
    ''', (location_id,)).fetchone()['count']
    
    # Calculate total pages
    total_pages = (total_equipment + per_page - 1) // per_page
    
    # Get paginated equipment at this location
    offset = (page - 1) * per_page
    equipment = conn.execute('''
        SELECT * FROM equipment 
        WHERE location_id = ? 
        ORDER BY device_type, model
        LIMIT ? OFFSET ?
    ''', (location_id, per_page, offset)).fetchall()
    
    # Get recent tickets for this location
    recent_tickets = conn.execute('''
        SELECT t.*, u.username as assigned_to_username
        FROM tickets t
        LEFT JOIN users u ON t.assigned_to = u.id
        WHERE t.location_id = ? 
        ORDER BY t.created_at DESC
        LIMIT 5
    ''', (location_id,)).fetchall()
    
    # Get active tickets count
    active_tickets_count = conn.execute('''
        SELECT COUNT(*) as count 
        FROM tickets 
        WHERE location_id = ? AND status NOT IN ('Resolved', 'Closed')
    ''', (location_id,)).fetchone()['count']
    
    # Get recent activity (you might want to implement an activity log table)
    recent_activity = []
    
    conn.close()
    
    # Debug output
    print(f"Rendering template with: page={page}, per_page={per_page}, total_equipment={total_equipment}, total_pages={total_pages}")
    
    return render_template(
        'view_location.html',
        location=dict(location),
        equipment=equipment,
        active_tickets_count=active_tickets_count,
        recent_activity=recent_activity,
        recent_tickets=recent_tickets,
        page=page,
        per_page=per_page,
        total_equipment=total_equipment,
        total_pages=total_pages
    )

def get_db_connection():
    # Get a database connection with a timeout
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout = 5000')  # 5 second timeout
    return conn

@app.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    content = request.form.get('content')
    if not content or not content.strip():
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    conn = None
    try:
        # Debug: Log input data
        current_app.logger.info(f"Adding comment to ticket {ticket_id} by user {current_user.id}")
        
        conn = get_db_connection()
        
        # Verify ticket exists
        ticket = conn.execute('SELECT id, title FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
        if not ticket:
            current_app.logger.error(f"Ticket {ticket_id} not found")
            flash('Ticket not found', 'danger')
            return redirect(url_for('tickets'))
        
        # Debug: Log ticket found
        current_app.logger.info(f"Found ticket: {ticket['title']}")
        
        # Insert comment
        conn.execute(
            'INSERT INTO ticket_comments (ticket_id, user_id, content, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
            (ticket_id, current_user.id, content.strip())
        )
        
        # Update ticket's updated_at timestamp
        conn.execute(
            'UPDATE tickets SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (ticket_id,)
        )
        
        conn.commit()
        current_app.logger.info("Comment added successfully")
        flash('Comment added successfully', 'success')
        
    except sqlite3.Error as e:
        error_msg = f"Database error in add_comment: {str(e)}"
        current_app.logger.error(error_msg, exc_info=True)
        if conn:
            conn.rollback()
        flash('A database error occurred while adding your comment. Please try again.', 'danger')
    except Exception as e:
        error_msg = f"Unexpected error in add_comment: {str(e)}"
        current_app.logger.error(error_msg, exc_info=True)
        if conn:
            conn.rollback()
        flash('An unexpected error occurred. Please try again.', 'danger')
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                current_app.logger.error(f"Error closing connection: {str(e)}")
    
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/tickets/<int:ticket_id>/status', methods=['POST'])
@login_required
def update_ticket_status(ticket_id):
    status = request.form.get('status')
    if not status:
        flash('Status is required', 'danger')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (status, ticket_id)
        )
        conn.commit()
        flash('Ticket status updated', 'success')
    except Exception as e:
        conn.rollback()
        flash('Failed to update ticket status', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/tickets/<int:ticket_id>/assign', methods=['POST'])
@login_required
def assign_ticket(ticket_id):
    assigned_to = request.form.get('assigned_to')
    
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE tickets SET assigned_to = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (assigned_to or None, ticket_id)
        )
        conn.commit()
        flash('Ticket assignment updated', 'success')
    except Exception as e:
        conn.rollback()
        flash('Failed to update ticket assignment', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('view_ticket', ticket_id=ticket_id))
    conn = get_db_connection()
    users_list = conn.execute('SELECT * FROM users ORDER BY username').fetchall()
    conn.close()
    return render_template('users.html', users=users_list)

def init_database():
    conn = None
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Create access_requests table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            location TEXT NOT NULL,
            message TEXT,
            requested_at TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            processed_at TIMESTAMP,
            processed_by INTEGER,
            notes TEXT,
            FOREIGN KEY (processed_by) REFERENCES users(id)
        )
        ''')
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                priority TEXT NOT NULL DEFAULT 'Medium',
                created_by INTEGER,
                assigned_to INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id),
                FOREIGN KEY (assigned_to) REFERENCES users (id)
            )
        ''')
        
        # Add any other missing tables or columns here
        conn.commit()
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
    finally:
        if conn:
            conn.close()

mail = Mail()

app.config['MAIL_SERVER'] = 'smtp.office365.com'  # Outlook SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ahbahaa@investmentgate.net'  # Your email
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'ahbahaa@investmentgate.net'

mail.init_app(app)

@app.route('/request-access', methods=['POST'])
def request_access():
    if request.method == 'POST':
        try:
            # Get form data
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            location = request.form.get('location')
            message = request.form.get('message', '')
            
            # Validate required fields
            if not all([full_name, email, location]):
                return jsonify({'success': False, 'message': 'All fields are required'}), 400
            
            # Create email message
            subject = f"New Access Request from {full_name}"
            body = f"""
            New access request received:
            
            Name: {full_name}
            Email: {email}
            Location: {location}
            
            Additional Information:
            {message}
            """
            
            # Send email
            msg = Message(
                subject=subject,
                recipients=['ahbahaa@investmentgate.net'],
                body=body,
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            
            return jsonify({
                'success': True,
                'message': 'Your request has been submitted successfully! We will contact you soon.'
            })
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred while processing your request. Please try again later.'
            }), 500
    
    return jsonify({'success': False, 'message': 'Invalid request method'}), 405

if __name__ == '__main__':
    # Initialize database if needed
    init_database()
    
    # Create required directories
    os.makedirs('static/uploads', exist_ok=True)
    
    # Run the application
    app.run(debug=True)
