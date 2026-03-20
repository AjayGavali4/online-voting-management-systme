"""
Database Initialization Script
Creates all database tables and default admin user
"""

from app import app, db
from models import Admin, User, CandidateUser, Election, Candidate, Vote, Document, AuditLog, OTP, AuthorizedLocation, LocationAuditLog
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with all tables and default admin"""
    with app.app_context():
        print("🔧 Initializing database...")
        
        # Create all tables
        print("  - Creating database tables...")
        db.create_all()
        print("  ✅ All tables created successfully")
        
        # Check if default admin exists
        existing_admin = Admin.query.filter_by(username='admin').first()
        
        if not existing_admin:
            print("  - Creating default admin user...")
            default_admin = Admin(
                username='admin',
                email='admin@voting.com',
                password_hash=generate_password_hash('admin123'),
                full_name='System Administrator',
                is_super_admin=True,
                two_factor_enabled=False
            )
            db.session.add(default_admin)
            db.session.commit()
            print("  ✅ Default admin created")
            print("     Username: admin")
            print("     Password: admin123")
            print("     Email: admin@voting.com")
        else:
            print("  ℹ️  Default admin already exists")
        
        # Verify tables
        print("\n📊 Database Tables:")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        for table in sorted(tables):
            print(f"  ✅ {table}")
        
        print(f"\n✅ Database initialization complete!")
        print(f"   Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"   Total tables: {len(tables)}")

if __name__ == '__main__':
    init_database()
