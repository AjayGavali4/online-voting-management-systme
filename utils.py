from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for, flash, request
from flask_login import current_user
import pyotp
import qrcode
from io import BytesIO
import base64
import hashlib
import os
import random
import string
from datetime import datetime, timedelta
import pytz
import math

# Timezone configuration
UTC = pytz.UTC
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current time in IST, converted to naive UTC for database comparison"""
    ist_now = datetime.now(IST)
    # Return as naive UTC for consistent database storage
    return ist_now.astimezone(UTC).replace(tzinfo=None)

def utc_to_ist(utc_datetime):
    """Convert UTC datetime to IST"""
    if utc_datetime is None:
        return None
    if utc_datetime.tzinfo is None:
        # If datetime is naive, assume it's UTC
        utc_datetime = UTC.localize(utc_datetime)
    return utc_datetime.astimezone(IST)

def ist_to_utc(ist_datetime):
    """Convert IST datetime to UTC for database storage"""
    if ist_datetime is None:
        return None
    if ist_datetime.tzinfo is None:
        # If datetime is naive, assume it's IST
        ist_datetime = IST.localize(ist_datetime)
    return ist_datetime.astimezone(UTC).replace(tzinfo=None)

def format_ist_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """Format datetime in IST"""
    if dt is None:
        return 'N/A'
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime(format_str) + ' IST'

def hash_password(password):
    """Hash a password using Werkzeug's security module"""
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)

def generate_2fa_secret():
    """Generate a secret for 2FA"""
    return pyotp.random_base32()

def generate_2fa_qr_code(secret, username):
    """Generate QR code for 2FA setup"""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=username,
        issuer_name='Voting Management System'
    )
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def verify_2fa_token(secret, token):
    """Verify a 2FA token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        # Check if user is admin (has is_super_admin attribute)
        if not hasattr(current_user, 'is_super_admin'):
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def candidate_required(f):
    """Decorator to require candidate authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        # Check if user is candidate (has candidate_entries attribute from CandidateUser)
        if not hasattr(current_user, 'candidate_entries'):
            flash('Access denied. Candidate privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def voter_required(f):
    """Decorator to require voter authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        # Check if user is voter (has is_verified attribute from User model, not admin or candidate)
        if hasattr(current_user, 'is_super_admin'):
            flash('This page is for voters only.', 'info')
            return redirect(url_for('admin.dashboard'))
        if hasattr(current_user, 'candidate_entries'):
            flash('This page is for voters only.', 'info')
            return redirect(url_for('candidate.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def verified_voter_required(f):
    """Decorator to require verified voter"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        # Check if user is voter (has is_verified attribute from User model, not admin or candidate)
        if hasattr(current_user, 'is_super_admin'):
            flash('This page is for voters only.', 'info')
            return redirect(url_for('admin.dashboard'))
        if hasattr(current_user, 'candidate_entries'):
            flash('This page is for voters only.', 'info')
            return redirect(url_for('candidate.dashboard'))
        if not current_user.is_verified:
            flash('Your account must be verified before you can vote.', 'warning')
            return redirect(url_for('voter.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def log_audit(user_type, user_id, action, resource_type=None, resource_id=None, details=None):
    """Log an audit event"""
    from models import AuditLog, db
    from flask import request
    
    try:
        audit = AuditLog(
            user_type=user_type,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        # Don't fail the main operation if audit logging fails
        db.session.rollback()
        print(f"Audit logging failed: {e}")

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def save_uploaded_file(file, upload_folder):
    """Save uploaded file and return path and hash"""
    if file and allowed_file(file.filename):
        filename = f"{hashlib.md5(file.read()).hexdigest()}_{file.filename}"
        file.seek(0)  # Reset file pointer
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Calculate file hash
        file_hash = calculate_file_hash(file_path)
        
        return file_path, file_hash, file.content_length, file.content_type
    return None, None, None, None

def generate_otp(length=6):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def get_email_delivery_error_message():
    """Return a user-facing email configuration or delivery error message."""
    from flask import current_app

    missing_settings = [
        setting for setting in ('MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD')
        if not current_app.config.get(setting)
    ]
    if missing_settings:
        return (
            "OTP email is not configured. Add MAIL_USERNAME and MAIL_PASSWORD in .env "
            "and use a Gmail App Password instead of your normal Gmail password."
        )

    if not (current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')):
        return "OTP email is not configured. Set MAIL_DEFAULT_SENDER or MAIL_USERNAME in .env."

    return None

def send_otp_email(email, otp_code, purpose='login'):
    """Send OTP via email with improved error handling."""
    from flask import current_app
    from flask_mail import Message
    import smtplib
    
    # Get mail instance from current app
    mail = current_app.extensions.get('mail')
    
    subject_map = {
        'login': 'Your Login OTP - Voting System',
        'registration': 'Email Verification OTP - Voting System',
        'password_reset': 'Password Reset OTP - Voting System',
        'password_change': 'Password Change OTP - Voting System'
    }
    
    subject = subject_map.get(purpose, 'Your OTP Code - Voting System')
    
    # Create HTML email template
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .otp-code {{ background: #fff; border: 2px solid #667eea; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
            .otp-number {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗳️ Voting System</h1>
                <p>Secure Authentication</p>
            </div>
            <div class="content">
                <h2>Your OTP Code</h2>
                <p>Hello,</p>
                <p>You have requested an OTP for <strong>{purpose}</strong>. Please use the code below to complete your authentication:</p>
                
                <div class="otp-code">
                    <p style="margin: 0; color: #666;">Your OTP Code:</p>
                    <div class="otp-number">{otp_code}</div>
                    <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Valid for 10 minutes</p>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong>
                    <ul style="margin: 10px 0;">
                        <li>This code will expire in 10 minutes</li>
                        <li>Do not share this code with anyone</li>
                        <li>If you didn't request this code, please ignore this email</li>
                    </ul>
                </div>
                
                <p>If you have any questions or concerns, please contact our support team.</p>
                
                <div class="footer">
                    <p>© 2025 Voting System - Secure & Transparent Elections</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    text_body = f"""
    Voting System - OTP Verification
    
    Your OTP code for {purpose} is: {otp_code}
    
    This code will expire in 10 minutes.
    
    Security Notice:
    - Do not share this code with anyone
    - If you didn't request this code, please ignore this message
    
    © 2025 Voting System
    """
    
    try:
        config_error = get_email_delivery_error_message()
        if config_error:
            # Fallback to console output for development
            print(f"\n{'='*60}")
            print(f"EMAIL WOULD BE SENT TO: {email}")
            print(f"SUBJECT: {subject}")
            print(f"OTP CODE: {otp_code}")
            print(f"PURPOSE: {purpose}")
            print(f"{'='*60}\n")
            print(f"WARNING: {config_error}")
            return False
        
        # Check if mail instance is available
        if not mail:
            print("ERROR: Flask-Mail not initialized properly")
            print(f"\n{'='*60}")
            print(f"EMAIL FALLBACK - WOULD BE SENT TO: {email}")
            print(f"OTP CODE: {otp_code}")
            print(f"{'='*60}\n")
            return False
        
        # Send actual email
        msg = Message(
            subject=subject,
            recipients=[email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME'),
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        print(f"OTP email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR: Gmail Authentication Error: {str(e)}")
        print("Gmail Setup Issues:")
        print("   1. Make sure 2-Factor Authentication is enabled on your Gmail")
        print("   2. Use App Password, NOT your regular Gmail password")
        print("   3. Generate a new App Password: https://myaccount.google.com/apppasswords")
        print("   4. Update .env with MAIL_USERNAME, MAIL_PASSWORD, and MAIL_DEFAULT_SENDER")
        
        # Fallback to console output
        print(f"\n{'='*60}")
        print(f"EMAIL FALLBACK - WOULD BE SENT TO: {email}")
        print(f"OTP CODE: {otp_code}")
        print(f"{'='*60}\n")
        return False
        
    except smtplib.SMTPException as e:
        print(f"ERROR: SMTP Error: {str(e)}")
        print("Check your email server settings")
        
        # Fallback to console output
        print(f"\n{'='*60}")
        print(f"EMAIL FALLBACK - WOULD BE SENT TO: {email}")
        print(f"OTP CODE: {otp_code}")
        print(f"{'='*60}\n")
        return False
        
    except Exception as e:
        print(f"ERROR: Failed to send OTP email to {email}: {str(e)}")
        
        # Fallback to console output
        print(f"\n{'='*60}")
        print(f"EMAIL FALLBACK - WOULD BE SENT TO: {email}")
        print(f"OTP CODE: {otp_code}")
        print(f"{'='*60}\n")
        return False

def send_otp_sms(phone_number, otp_code, purpose='login'):
    """Send OTP via SMS (simulated for development)"""
    # In production, use Twilio, AWS SNS, or similar
    message = f"Your OTP code for {purpose} is: {otp_code}. Valid for 10 minutes."
    
    # In development, print to console
    print(f"\n{'='*50}")
    print(f"SMS TO: {phone_number}")
    print(f"MESSAGE: {message}")
    print(f"{'='*50}\n")
    
    # In production, uncomment and configure:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # client.messages.create(body=message, from_=twilio_number, to=phone_number)
    
    return True

def create_otp(email, phone_number=None, purpose='login', expires_minutes=10):
    """Create and store an OTP"""
    from models import OTP, db
    from flask import request, has_request_context
    
    # Generate new OTP
    otp_code = generate_otp()
    
    # Get current time in IST and convert to UTC for database storage
    ist_now = datetime.now(IST)
    utc_now = ist_now.astimezone(UTC).replace(tzinfo=None)
    
    # Calculate expiration time in IST, then convert to UTC
    ist_expires = ist_now + timedelta(minutes=expires_minutes)
    utc_expires = ist_expires.astimezone(UTC).replace(tzinfo=None)
    
    # Get IP address if in request context
    ip_address = None
    if has_request_context():
        ip_address = request.remote_addr
    
    otp = OTP(
        email=email,
        phone_number=phone_number,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=utc_expires,
        created_at=utc_now,
        ip_address=ip_address
    )
    
    db.session.add(otp)
    db.session.commit()
    
    # Send OTP via email
    email_sent = send_otp_email(email, otp_code, purpose)
    
    # Send OTP via SMS if phone number provided
    if phone_number:
        send_otp_sms(phone_number, otp_code, purpose)
    
    # Return OTP object and success status (don't return the actual code)
    return otp, email_sent

def verify_otp(email, otp_code, purpose='login'):
    """Verify an OTP code"""
    from models import OTP, db
    
    otp = OTP.query.filter_by(
        email=email,
        otp_code=otp_code,
        purpose=purpose,
        is_used=False
    ).order_by(OTP.created_at.desc()).first()
    
    if not otp:
        return False, "Invalid OTP code."
    
    if not otp.is_valid():
        return False, "OTP has expired or already used."
    
    # Mark OTP as used
    otp.is_used = True
    db.session.commit()
    
    return True, "OTP verified successfully."



def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    
    Uses the Haversine formula to calculate the distance between
    two GPS coordinate pairs on Earth's surface.
    
    Args:
        lat1 (float): Latitude of first point in degrees
        lon1 (float): Longitude of first point in degrees
        lat2 (float): Latitude of second point in degrees
        lon2 (float): Longitude of second point in degrees
    
    Returns:
        float: Distance in meters
    
    Validates: Requirements 5.1
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r
