"""
Database Reset Script
Deletes all data from the database and recreates tables with default admin
"""

from app import app, db
from models import Admin, User, CandidateUser, Election, Candidate, Vote, Document, AuditLog, OTP, AuthorizedLocation, LocationAuditLog
from werkzeug.security import generate_password_hash
import os

def reset_database():
    """Delete all data and reset database to initial state"""
    with app.app_context():
        print("🗑️  Resetting database...")
        print("=" * 60)
        
        # Option 1: Drop and recreate all tables (cleanest method)
        print("\n1. Dropping all tables...")
        db.drop_all()
        print("   ✅ All tables dropped")
        
        print("\n2. Creating fresh tables...")
        db.create_all()
        print("   ✅ All tables created")
        
        # Create default admin
        print("\n3. Creating default admin user...")
        default_admin = Admin(
            username='admin',
            email='ajayrgavali@gmail.com',
            password_hash=generate_password_hash('admin123'),
            full_name='System Administrator',
            is_super_admin=True,
            two_factor_enabled=False
        )
        db.session.add(default_admin)
        db.session.commit()
        print("   ✅ Default admin created")
        print("      Username: admin")
        print("      Password: admin123")
        print("      Email: ajayrgavali@gmail.com")
        
        # Verify tables
        print("\n4. Verifying database structure...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        for table in sorted(tables):
            # Count records in each table
            result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"   ✅ {table}: {count} records")
        
        print("\n" + "=" * 60)
        print("✅ Database reset complete!")
        print(f"   Total tables: {len(tables)}")
        print(f"   Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\n🎉 Database is now clean and ready to use!")

if __name__ == '__main__':
    confirm = input("\n⚠️  WARNING: This will DELETE ALL DATA from the database!\n   Type 'YES' to confirm: ")
    if confirm == 'YES':
        reset_database()
    else:
        print("❌ Database reset cancelled.")
