from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    if os.environ.get('FLASK_ENV') == 'development':
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        print("⚠️  WARNING: Using default secret key for development")
    else:
        raise ValueError("SECRET_KEY environment variable must be set for production")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///voting_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Your email address
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Your email password/app password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# CSRF Configuration for development
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for development
app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow HTTP in development

if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@app.before_request
def validate_session():
    """
    Validate user session for single-session enforcement.
    Only invalidate if THIS browser's session doesn't match the stored session.
    Also updates user activity timestamp for session timeout handling.
    """
    from flask_login import current_user, logout_user
    from flask import session
    
    if current_user.is_authenticated:
        # Skip validation for admins
        if hasattr(current_user, 'is_super_admin'):
            return
        
        # Check if user has session tracking attributes
        if hasattr(current_user, 'session_id') and hasattr(current_user, 'is_logged_in'):
            stored_session_id = current_user.session_id
            current_session_id = session.get('user_session_id')
            
            # Valid session - update activity timestamp
            if current_user.is_logged_in and stored_session_id and current_session_id == stored_session_id:
                # This is the valid active session - update last_activity
                from datetime import datetime
                if hasattr(current_user, 'last_activity'):
                    current_user.last_activity = datetime.utcnow()
                    db.session.commit()
                return
            
            # Invalid session scenarios - log out THIS browser only
            if current_user.is_logged_in and stored_session_id and current_session_id and current_session_id != stored_session_id:
                # This browser has an outdated session
                logout_user()
                session.clear()
                
                from flask import flash, redirect, url_for
                flash('You were logged out because this account was used to log in on another device.', 'warning')
                return redirect(url_for('index'))
            
            # If this browser has no session_id but user is logged in elsewhere
            elif current_user.is_logged_in and stored_session_id and not current_session_id:
                logout_user()
                session.clear()
                
                from flask import flash, redirect, url_for
                flash('Please log in to continue.', 'info')
                return redirect(url_for('index'))

# Initialize database
from models import db
db.init_app(app)

# Initialize Flask-Mail
mail = Mail(app)

# Add IST datetime filter
@app.template_filter('ist_datetime')
def ist_datetime_filter(dt, format='%Y-%m-%d %H:%M'):
    """Convert UTC datetime to IST and format it"""
    from utils import format_ist_datetime
    return format_ist_datetime(dt, format)

# Initialize Flask-Mail
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Import models after db initialization
from models import User, Admin, CandidateUser, CandidateJoinRequest, Election, Candidate, Vote, Document, AuditLog, OTP, AuthorizedLocation, LocationAuditLog

# Import blueprints
from routes.auth import auth_bp
from routes.voter import voter_bp
from routes.admin import admin_bp
from routes.election import election_bp
from routes.candidate import candidate_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(voter_bp, url_prefix='/voter')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(election_bp, url_prefix='/election')
app.register_blueprint(candidate_bp, url_prefix='/candidate')

@login_manager.user_loader
def load_user(user_id):
    """
    Load user by ID with type prefix.
    Format: 'type:id' where type is 'admin', 'candidate', or 'voter'
    """
    # Handle legacy format (just ID) by checking all tables
    if ':' not in str(user_id):
        # Legacy format - check all tables (admin first for backward compatibility)
        admin = Admin.query.get(int(user_id))
        if admin:
            return admin
        candidate_user = CandidateUser.query.get(int(user_id))
        if candidate_user:
            return candidate_user
        return User.query.get(int(user_id))
    
    # New format with type prefix
    try:
        user_type, uid = str(user_id).split(':', 1)
        uid = int(uid)
        
        if user_type == 'admin':
            return Admin.query.get(uid)
        elif user_type == 'candidate':
            return CandidateUser.query.get(uid)
        elif user_type == 'voter':
            return User.query.get(uid)
    except (ValueError, AttributeError):
        pass
    
    return None

@app.context_processor
def inject_user_type():
    """Make user type functions available in all templates"""
    from utils import format_ist_datetime, utc_to_ist
    from flask_login import current_user
    
    def is_admin(user):
        if user and user.is_authenticated:
            return hasattr(user, 'is_super_admin') and user.is_super_admin
        return False
    
    def is_candidate(user):
        if user and user.is_authenticated:
            return hasattr(user, 'candidate_entries')
        return False
    
    def is_voter(user):
        if user and user.is_authenticated:
            return not hasattr(user, 'is_super_admin') and not hasattr(user, 'candidate_entries')
        return False
    
    pending_candidate_requests_count = 0
    if current_user.is_authenticated and is_candidate(current_user):
        pending_candidate_requests_count = CandidateJoinRequest.query.filter_by(
            candidate_user_id=current_user.id,
            status='pending'
        ).count()

    return dict(
        is_admin=is_admin, 
        is_candidate=is_candidate, 
        is_voter=is_voter,
        format_ist_datetime=format_ist_datetime,
        utc_to_ist=utc_to_ist,
        pending_candidate_requests_count=pending_candidate_requests_count
    )

@app.template_filter('ist_datetime')
def ist_datetime_filter(utc_dt):
    """Convert UTC datetime to IST for template display"""
    if utc_dt is None:
        return 'N/A'
    
    from utils import utc_to_ist
    ist_dt = utc_to_ist(utc_dt)
    if ist_dt:
        return ist_dt.strftime('%Y-%m-%d %H:%M IST')
    return 'N/A'

@app.template_filter('ist_datetime_short')
def ist_datetime_short_filter(utc_dt):
    """Convert UTC datetime to IST for template display (short format)"""
    if utc_dt is None:
        return 'N/A'
    
    from utils import utc_to_ist
    ist_dt = utc_to_ist(utc_dt)
    if ist_dt:
        return ist_dt.strftime('%b %d, %Y %H:%M')
    return 'N/A'

@app.template_filter('ist_date')
def ist_date_filter(utc_dt):
    """Convert UTC datetime to IST date for template display"""
    if utc_dt is None:
        return 'N/A'
    
    from utils import utc_to_ist
    ist_dt = utc_to_ist(utc_dt)
    if ist_dt:
        return ist_dt.strftime('%Y-%m-%d')
    return 'N/A'

@app.template_filter('ist_time')
def ist_time_filter(utc_dt):
    """Convert UTC datetime to IST time for template display"""
    if utc_dt is None:
        return 'N/A'
    
    from utils import utc_to_ist
    ist_dt = utc_to_ist(utc_dt)
    if ist_dt:
        return ist_dt.strftime('%H:%M IST')
    return 'N/A'

@app.route('/')
def index():
    """Landing page with role selection"""
    from flask import render_template
    return render_template('landing.html')

# ===== TEMPORARY TEST LOGIN ROUTES (Development Only) =====
@app.route('/test-login/voter')
def test_login_voter():
    """Direct voter login without OTP - FOR TESTING ONLY"""
    if os.environ.get('FLASK_ENV') != 'development':
        return "Not available", 403
    from flask_login import login_user
    from models import User
    voter = User.query.filter_by(username='testvoter').first()
    if voter:
        login_user(voter)
        voter.is_logged_in = True
        db.session.commit()
        return redirect(url_for('voter.dashboard'))
    return "Test voter not found", 404

@app.route('/test-login/candidate')
def test_login_candidate():
    """Direct candidate login without OTP - FOR TESTING ONLY"""
    if os.environ.get('FLASK_ENV') != 'development':
        return "Not available", 403
    from flask_login import login_user
    from models import CandidateUser
    candidate = CandidateUser.query.filter_by(username='testcandidate').first()
    if candidate:
        login_user(candidate)
        candidate.is_logged_in = True
        db.session.commit()
        return redirect(url_for('candidate.dashboard'))
    return "Test candidate not found", 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            default_admin = Admin(
                username='admin',
                email='admin@voting.com',
                password_hash=generate_password_hash('admin123'),
                full_name='System Administrator',
                is_super_admin=True
            )
            db.session.add(default_admin)
            db.session.commit()
            print("Default admin created: username='admin', password='admin123'")
    
    # Use environment variable for debug mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5001))  # Use port 5001 instead of 5000
    app.run(debug=debug_mode, port=port)
