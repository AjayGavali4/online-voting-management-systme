# Online Voting Management System

A comprehensive web-based voting management system built with Flask, featuring secure authentication, document verification, GPS-based location validation, and real-time election management.

## Features

### Core Functionality
- **Multi-role System**: Admin, Voter, and Candidate roles with distinct dashboards
- **Secure Authentication**: Password-based and OTP-based login with 2FA support
- **Document Verification**: Upload and verify identity documents
- **GPS Location Validation**: Ensure voters are in authorized locations
- **Real-time Elections**: Create, manage, and monitor elections
- **Audit Logging**: Comprehensive audit trails for all actions
- **QR Code Generation**: Generate QR codes for election access

### Security Features
- CSRF protection
- Password hashing with Werkzeug
- OTP verification via email
- Two-factor authentication for admins
- GPS coordinate encryption
- Session management

## Project Structure

```
├── app.py                      # Main application entry point
├── models.py                   # Database models
├── utils.py                    # Utility functions
├── init_db.py                  # Database initialization
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── run.bat                    # Windows startup script
│
├── routes/                     # Application routes
│   ├── admin.py               # Admin routes
│   ├── auth.py                # Authentication routes
│   ├── candidate.py           # Candidate routes
│   ├── election.py            # Election routes
│   └── voter.py               # Voter routes
│
├── templates/                  # HTML templates
│   ├── admin/                 # Admin templates
│   ├── auth/                  # Authentication templates
│   ├── candidate/             # Candidate templates
│   ├── voter/                 # Voter templates
│   └── layouts/               # Base layouts
│
├── static/                     # Static assets
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── images/                # Images
│
├── validation/                 # Validation modules
│   ├── alert_manager.py       # Alert management
│   ├── base.py                # Base validators
│   ├── enhanced_validators.py # Enhanced validation
│   ├── location_audit_logger.py # Location audit logging
│   ├── location_manager.py    # Location management
│   ├── location_validator.py  # Location validation
│   └── qr_code_generator.py   # QR code generation
│
├── migrations/                 # Database migrations
│   ├── 001_add_gps_location_tables.py
│   ├── 002_add_candidate_id_to_documents.py
│   └── 003_add_verification_to_candidates.py
│
├── instance/                   # Instance-specific files
│   └── voting_system.db       # SQLite database
│
└── uploads/                    # Uploaded files
    └── documents/             # User documents
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd voting-system
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and fill in your configuration:
# - SECRET_KEY: Generate with: python -c "import secrets; print(secrets.token_hex(32))"
# - MAIL_USERNAME: Your email address
# - MAIL_PASSWORD: Your email app password (for Gmail, use App Password)
```

5. Initialize the database:
```bash
python init_db.py
```

6. Run the application:
```bash
# Option 1: Direct Python
python app.py

# Option 2: Windows batch file
run.bat
```

The application will be available at `http://127.0.0.1:5000`

### Default Admin Credentials
- Username: `admin`
- Password: `admin123`

**Important**: Change the default admin password immediately after first login!

## Configuration

### Email Configuration (for OTP)

#### Gmail Setup:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to Google Account Settings → Security → 2-Step Verification → App Passwords
   - Generate a new app password for "Mail"
3. Use the app password in `.env` file

#### Environment Variables:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/voting_system.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Usage

### Admin Functions
- Create and manage elections
- Verify voter documents
- Manage candidates
- View audit logs
- Configure authorized locations
- Generate QR codes for elections

### Voter Functions
- Register and verify identity
- Upload documents
- View available elections
- Cast votes
- View voting history
- Check verification status

### Candidate Functions
- Register as a candidate
- Join elections
- View election statistics
- Manage profile

## Database Migrations

Run migrations to update the database schema:
```bash
python migrations/001_add_gps_location_tables.py
python migrations/002_add_candidate_id_to_documents.py
python migrations/003_add_verification_to_candidates.py
```

## Security Considerations

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Change default admin password** - Immediately after setup
3. **Use strong SECRET_KEY** - Generate cryptographically secure key
4. **Enable HTTPS in production** - Use SSL/TLS certificates
5. **Regular backups** - Backup database regularly
6. **Update dependencies** - Keep packages up to date

## Technologies Used

- **Backend**: Flask 3.0.0
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login, PyOTP
- **Email**: Flask-Mail
- **Forms**: Flask-WTF
- **Security**: Werkzeug, Cryptography
- **QR Codes**: qrcode, Pillow
- **Timezone**: pytz

## Troubleshooting

### Common Issues

**Issue: "No module named 'flask'"**
```bash
# Activate virtual environment and install dependencies
.venv\Scripts\activate
pip install -r requirements.txt
```

**Issue: "SECRET_KEY not set"**
```bash
# Create .env file from template
copy .env.example .env
# Edit .env and add SECRET_KEY
```

**Issue: "Email not sending"**
- For Gmail: Enable 2FA and create App Password
- Use the App Password in MAIL_PASSWORD field
- Check MAIL_SERVER and MAIL_PORT settings

**Issue: "Database locked"**
- Close any other instances of the application
- Restart the application

## Support

For issues and questions, please open an issue in the repository.

## License

[Add your license information here]
