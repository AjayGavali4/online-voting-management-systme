"""
Approve Candidate Script
Approves a candidate user by email address
"""

from app import app, db
from models import CandidateUser
import sys

def approve_candidate(email):
    """Approve a candidate user by email"""
    with app.app_context():
        print(f"🔍 Looking for candidate with email: {email}")
        print("=" * 60)
        
        # Find the candidate user
        candidate = CandidateUser.query.filter_by(email=email).first()
        
        if not candidate:
            print(f"❌ No candidate found with email: {email}")
            print("\n📋 Available candidates:")
            all_candidates = CandidateUser.query.all()
            if all_candidates:
                for c in all_candidates:
                    print(f"   - {c.full_name} ({c.email}) - Status: {c.verification_status}")
            else:
                print("   No candidates registered yet.")
            return False
        
        # Check current status
        print(f"\n📋 Candidate Details:")
        print(f"   Name: {candidate.full_name}")
        print(f"   Username: {candidate.username}")
        print(f"   Email: {candidate.email}")
        print(f"   Phone: {candidate.phone_number or 'N/A'}")
        print(f"   Current Status: {candidate.verification_status}")
        print(f"   Is Verified: {candidate.is_verified}")
        
        if candidate.verification_status == 'approved' and candidate.is_verified:
            print(f"\n✅ Candidate is already approved!")
            return True
        
        # Approve the candidate
        print(f"\n✏️  Approving candidate...")
        candidate.verification_status = 'approved'
        candidate.is_verified = True
        candidate.verification_notes = 'Approved by admin via script'
        
        db.session.commit()
        
        print(f"✅ Candidate approved successfully!")
        print(f"\n📋 Updated Details:")
        print(f"   Status: {candidate.verification_status}")
        print(f"   Is Verified: {candidate.is_verified}")
        print(f"   Notes: {candidate.verification_notes}")
        
        return True

if __name__ == '__main__':
    email = 'ajaygavali469@gmail.com'
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    print(f"\n🎯 Candidate Approval Tool")
    print("=" * 60)
    
    success = approve_candidate(email)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Candidate can now login and participate in elections!")
    else:
        print("\n" + "=" * 60)
        print("❌ Approval failed. Please check the email address.")
