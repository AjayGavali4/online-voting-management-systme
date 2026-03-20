from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import hashlib
import os
import pytz

# Timezone configuration
UTC = pytz.UTC
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current time in IST, but return as naive UTC for database comparison"""
    ist_now = datetime.now(IST)
    return ist_now.astimezone(UTC).replace(tzinfo=None)

# db will be initialized in app.py
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    profile_photo = db.Column(db.Text)  # Base64 encoded image or file path
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    verification_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    last_login = db.Column(db.DateTime)
    is_logged_in = db.Column(db.Boolean, default=False, nullable=False)  # For single session enforcement
    session_id = db.Column(db.String(255))  # Track session for cleanup
    last_activity = db.Column(db.DateTime)  # Track last activity for session timeout
    
    # Relationships
    documents = db.relationship('Document', backref='user', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_created_at_ist(self):
        """Get creation time in IST"""
        if self.created_at:
            if self.created_at.tzinfo is None:
                utc_dt = UTC.localize(self.created_at)
            else:
                utc_dt = self.created_at
            return utc_dt.astimezone(IST)
        return None
    
    def get_last_login_ist(self):
        """Get last login time in IST"""
        if self.last_login:
            if self.last_login.tzinfo is None:
                utc_dt = UTC.localize(self.last_login)
            else:
                utc_dt = self.last_login
            return utc_dt.astimezone(IST)
        return None
    
    def get_id(self):
        """Return user ID with type prefix for Flask-Login"""
        return f'voter:{self.id}'

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))  # For 2FA
    two_factor_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Admin {self.username}>'
    
    def get_created_at_ist(self):
        """Get creation time in IST"""
        if self.created_at:
            if self.created_at.tzinfo is None:
                utc_dt = UTC.localize(self.created_at)
            else:
                utc_dt = self.created_at
            return utc_dt.astimezone(IST)
        return None
    
    def get_last_login_ist(self):
        """Get last login time in IST"""
        if self.last_login:
            if self.last_login.tzinfo is None:
                utc_dt = UTC.localize(self.last_login)
            else:
                utc_dt = self.last_login
            return utc_dt.astimezone(IST)
        return None
    
    def get_id(self):
        """Return user ID with type prefix for Flask-Login"""
        return f'admin:{self.id}'

class CandidateUser(UserMixin, db.Model):
    __tablename__ = 'candidate_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20))
    bio = db.Column(db.Text)
    profile_photo = db.Column(db.Text)  # Base64 encoded image or file path
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    verification_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    last_login = db.Column(db.DateTime)
    is_logged_in = db.Column(db.Boolean, default=False, nullable=False)  # For single session enforcement
    session_id = db.Column(db.String(255))  # Track session for cleanup
    last_activity = db.Column(db.DateTime)  # Track last activity for session timeout
    
    # Relationship to Candidate entities (candidates in elections)
    candidate_entries = db.relationship('Candidate', backref='candidate_user', lazy=True)
    
    def __repr__(self):
        return f'<CandidateUser {self.username}>'
    
    def get_id(self):
        """Return user ID with type prefix for Flask-Login"""
        return f'candidate:{self.id}'


class CandidateJoinRequest(db.Model):
    __tablename__ = 'candidate_join_requests'

    id = db.Column(db.Integer, primary_key=True)
    candidate_user_id = db.Column(db.Integer, db.ForeignKey('candidate_users.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    campaign_description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    requested_at = db.Column(db.DateTime, default=get_ist_now, nullable=False)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    review_notes = db.Column(db.Text)

    candidate_user = db.relationship('CandidateUser', backref='join_requests')
    election = db.relationship('Election', backref='candidate_join_requests')
    reviewer = db.relationship('Admin', backref='reviewed_join_requests')

    __table_args__ = (
        db.UniqueConstraint('candidate_user_id', 'election_id', name='uq_candidate_join_request_per_election'),
    )

    def __repr__(self):
        return f'<CandidateJoinRequest candidate={self.candidate_user_id} election={self.election_id} status={self.status}>'

class Election(db.Model):
    __tablename__ = 'elections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    candidate_join_start = db.Column(db.DateTime)  # When candidates can start joining
    candidate_join_end = db.Column(db.DateTime)  # When candidate join period ends
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    
    # Relationships
    candidates = db.relationship('Candidate', backref='election', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='election', lazy=True)
    
    def __repr__(self):
        return f'<Election {self.title}>'
    
    def is_open(self):
        now = get_ist_now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    def get_total_votes(self):
        return Vote.query.filter_by(election_id=self.id).count()
    
    def get_results(self):
        results = {}
        for candidate in self.candidates:
            vote_count = Vote.query.filter_by(
                election_id=self.id,
                candidate_id=candidate.id
            ).count()
            results[candidate] = vote_count
        return results
    
    def get_start_date_ist(self):
        """Get start date in IST"""
        if self.start_date:
            if self.start_date.tzinfo is None:
                utc_dt = UTC.localize(self.start_date)
            else:
                utc_dt = self.start_date
            return utc_dt.astimezone(IST)
        return None
    
    def get_end_date_ist(self):
        """Get end date in IST"""
        if self.end_date:
            if self.end_date.tzinfo is None:
                utc_dt = UTC.localize(self.end_date)
            else:
                utc_dt = self.end_date
            return utc_dt.astimezone(IST)
        return None
    
    def get_created_at_ist(self):
        """Get creation time in IST"""
        if self.created_at:
            if self.created_at.tzinfo is None:
                utc_dt = UTC.localize(self.created_at)
            else:
                utc_dt = self.created_at
            return utc_dt.astimezone(IST)
        return None

class Candidate(db.Model):
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    candidate_user_id = db.Column(db.Integer, db.ForeignKey('candidate_users.id'), nullable=True)  # Link to CandidateUser
    created_at = db.Column(db.DateTime, default=get_ist_now)
    
    # Relationships
    votes = db.relationship('Vote', backref='candidate', lazy=True)
    
    def __repr__(self):
        return f'<Candidate {self.name}>'
    
    def get_vote_count(self):
        return Vote.query.filter_by(candidate_id=self.id).count()

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    vote_hash = db.Column(db.String(64), unique=True, nullable=False)  # For duplicate detection
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    is_fraudulent = db.Column(db.Boolean, default=False)
    fraud_reason = db.Column(db.Text)
    cast_at = db.Column(db.DateTime, default=get_ist_now)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'election_id', name='unique_user_election_vote'),)
    
    def __repr__(self):
        return f'<Vote {self.id}>'
    
    def get_cast_at_ist(self):
        """Get vote cast time in IST"""
        if self.cast_at:
            if self.cast_at.tzinfo is None:
                utc_dt = UTC.localize(self.cast_at)
            else:
                utc_dt = self.cast_at
            return utc_dt.astimezone(IST)
        return None
    
    @staticmethod
    def generate_vote_hash(user_id, election_id, candidate_id, timestamp):
        """Generate a hash for duplicate detection"""
        data = f"{user_id}_{election_id}_{candidate_id}_{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For voters
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_users.id'), nullable=True)  # For candidates
    document_type = db.Column(db.String(50), nullable=False)  # aadhar, passport, license, etc.
    file_path = db.Column(db.String(500), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)  # For duplicate detection
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    reviewed_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=get_ist_now)
    
    # Relationships
    candidate_user = db.relationship('CandidateUser', backref='documents', lazy=True)
    
    # Constraint: at least one of user_id or candidate_id must be set
    __table_args__ = (
        db.CheckConstraint('(user_id IS NOT NULL) OR (candidate_id IS NOT NULL)', name='check_owner'),
    )
    
    def __repr__(self):
        return f'<Document {self.id}>'
    
    @staticmethod
    def calculate_file_hash(file_path):
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(20), nullable=False)  # admin, voter, candidate
    user_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))  # election, candidate, vote, document, user
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=get_ist_now)
    
    def __repr__(self):
        return f'<AuditLog {self.action} at {self.timestamp}>'

class OTP(db.Model):
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20))
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # login, registration, password_reset
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    ip_address = db.Column(db.String(45))
    
    def __repr__(self):
        return f'<OTP {self.email} - {self.purpose}>'
    
    def is_valid(self):
        """Check if OTP is still valid"""
        # Get current time in IST and convert to UTC for comparison
        ist_now = datetime.now(IST)
        utc_now = ist_now.astimezone(UTC).replace(tzinfo=None)
        
        # Check if OTP is not used and not expired
        return not self.is_used and utc_now < self.expires_at
    
    def get_created_at_ist(self):
        """Get creation time in IST"""
        if self.created_at:
            if self.created_at.tzinfo is None:
                utc_dt = UTC.localize(self.created_at)
            else:
                utc_dt = self.created_at
            return utc_dt.astimezone(IST)
        return None
    
    def get_expires_at_ist(self):
        """Get expiry time in IST"""
        if self.expires_at:
            if self.expires_at.tzinfo is None:
                utc_dt = UTC.localize(self.expires_at)
            else:
                utc_dt = self.expires_at
            return utc_dt.astimezone(IST)
        return None


class AuthorizedLocation(db.Model):
    """
    Model for authorized voting locations with GPS coordinates.
    Validates: Requirements 1.2, 1.3, 1.4, 1.5
    """
    __tablename__ = 'authorized_locations'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id', ondelete='CASCADE'), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)  # -90 to 90 degrees
    longitude = db.Column(db.Numeric(11, 8), nullable=False)  # -180 to 180 degrees
    radius = db.Column(db.Numeric(8, 2), nullable=False)  # 0 to 10000 meters
    created_at = db.Column(db.DateTime, default=get_ist_now, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    
    # Relationships
    election_rel = db.relationship('Election', backref='authorized_locations', lazy=True)
    admin_rel = db.relationship('Admin', backref='created_locations', lazy=True)
    
    # Database constraints for coordinate validation
    __table_args__ = (
        db.CheckConstraint('latitude >= -90 AND latitude <= 90', name='check_latitude_range'),
        db.CheckConstraint('longitude >= -180 AND longitude <= 180', name='check_longitude_range'),
        db.CheckConstraint('radius > 0 AND radius <= 10000', name='check_radius_range'),
    )
    
    def __repr__(self):
        return f'<AuthorizedLocation {self.id} for Election {self.election_id}>'
    
    def get_created_at_ist(self):
        """Get creation time in IST"""
        if self.created_at:
            if self.created_at.tzinfo is None:
                utc_dt = UTC.localize(self.created_at)
            else:
                utc_dt = self.created_at
            return utc_dt.astimezone(IST)
        return None
    
    @staticmethod
    def validate_coordinates(latitude, longitude, radius):
        """
        Validate GPS coordinates and radius.
        Returns: (is_valid, error_message)
        """
        if not (-90 <= latitude <= 90):
            return False, "Latitude must be between -90 and 90 degrees."
        if not (-180 <= longitude <= 180):
            return False, "Longitude must be between -180 and 180 degrees."
        if not (0 < radius <= 10000):
            return False, "Radius must be between 0 and 10000 meters."
        return True, None


class LocationAuditLog(db.Model):
    """
    Model for location validation audit logs with encrypted GPS coordinates.
    Validates: Requirements 7.2, 8.4
    """
    __tablename__ = 'location_audit_logs'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    latitude_encrypted = db.Column(db.LargeBinary, nullable=False)  # Encrypted latitude
    longitude_encrypted = db.Column(db.LargeBinary, nullable=False)  # Encrypted longitude
    validation_success = db.Column(db.Boolean, nullable=False)
    nearest_distance = db.Column(db.Numeric(10, 2), nullable=False)  # Distance in meters
    timestamp = db.Column(db.DateTime, default=get_ist_now, nullable=False)
    ip_address_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash of IP
    
    # Relationships
    voter_rel = db.relationship('User', backref='location_audit_logs', lazy=True)
    election_rel = db.relationship('Election', backref='location_audit_logs', lazy=True)
    
    def __repr__(self):
        return f'<LocationAuditLog {self.id} for Voter {self.voter_id}>'
    
    def get_timestamp_ist(self):
        """Get timestamp in IST"""
        if self.timestamp:
            if self.timestamp.tzinfo is None:
                utc_dt = UTC.localize(self.timestamp)
            else:
                utc_dt = self.timestamp
            return utc_dt.astimezone(IST)
        return None
    
    @staticmethod
    def hash_ip_address(ip_address):
        """Hash IP address using SHA-256"""
        return hashlib.sha256(ip_address.encode()).hexdigest()

