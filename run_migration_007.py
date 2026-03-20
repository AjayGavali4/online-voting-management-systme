#!/usr/bin/env python
"""
Run Migration 007: Add candidate join date/time fields
"""

from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("Applying Migration 007: Adding candidate join date/time fields...")
            
            # Add candidate_join_start column
            try:
                db.session.execute(text("ALTER TABLE elections ADD COLUMN candidate_join_start DATETIME"))
                db.session.commit()
                print("  ✓ Added candidate_join_start column")
            except Exception as e:
                if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                    print("  ℹ candidate_join_start column already exists")
                else:
                    print(f"  ✗ Error: {e}")
            
            # Add candidate_join_end column
            try:
                db.session.execute(text("ALTER TABLE elections ADD COLUMN candidate_join_end DATETIME"))
                db.session.commit()
                print("  ✓ Added candidate_join_end column")
            except Exception as e:
                if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                    print("  ℹ candidate_join_end column already exists")
                else:
                    print(f"  ✗ Error: {e}")
            
            print("✅ Migration 007 applied successfully!")
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    run_migration()
