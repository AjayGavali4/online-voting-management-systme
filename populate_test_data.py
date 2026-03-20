"""
Test Data Population Script
Populates the database with sample data for testing:
- Elections
- Voters (Users)
- Candidates
- Authorized Locations
- Documents
- Profile Photos
"""

import os
import base64
import uuid
import hashlib
from datetime import datetime, timedelta
from app import app, db
from models import Admin, User, CandidateUser, Election, Candidate, Document, AuthorizedLocation
from werkzeug.security import generate_password_hash


def get_sample_profile_photo():
    """Get a base64 encoded sample profile photo"""
    # Check if user provided a profile photo in uploads folder
    profile_photo_path = os.path.join(os.path.dirname(__file__), 'uploads', 'profile_photos', 'sample_profile.jpg')
    
    if os.path.exists(profile_photo_path):
        with open(profile_photo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    # Return a small placeholder image (1x1 transparent PNG) if no image available
    # This is a minimal PNG placeholder
    placeholder = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    return placeholder


def create_profile_photos_directory():
    """Create profile photos directory if it doesn't exist"""
    profile_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'profile_photos')
    os.makedirs(profile_dir, exist_ok=True)
    return profile_dir


def create_test_documents_directory():
    """Create test documents directory if it doesn't exist"""
    docs_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'documents')
    os.makedirs(docs_dir, exist_ok=True)
    return docs_dir


def populate_test_data():
    """Main function to populate all test data"""
    with app.app_context():
        print("=" * 60)
        print("🔧 POPULATING TEST DATA")
        print("=" * 60)
        
        # Create directories
        create_profile_photos_directory()
        create_test_documents_directory()
        
        # Get sample profile photo
        profile_photo_base64 = get_sample_profile_photo()
        
        # Check for existing admin
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            print("⚠️  No admin found. Please run init_db.py first.")
            return
        
        print(f"\n📋 Using admin: {admin.username} (ID: {admin.id})")
        
        # ============================================
        # CREATE TEST VOTERS
        # ============================================
        print("\n👥 CREATING TEST VOTERS...")
        
        test_voters = [
            {
                'username': 'voter1',
                'email': 'voter1@example.com',
                'password': 'voter123',
                'full_name': 'Rajesh Kumar',
                'date_of_birth': datetime(1990, 5, 15).date(),
                'phone_number': '+91 9876543210',
                'address': '123 MG Road, Mumbai, Maharashtra 400001',
                'is_verified': True,
                'verification_status': 'approved'
            },
            {
                'username': 'voter2',
                'email': 'voter2@example.com',
                'password': 'voter123',
                'full_name': 'Priya Sharma',
                'date_of_birth': datetime(1995, 8, 22).date(),
                'phone_number': '+91 9876543211',
                'address': '456 Park Street, Kolkata, West Bengal 700016',
                'is_verified': True,
                'verification_status': 'approved'
            },
            {
                'username': 'voter3',
                'email': 'voter3@example.com',
                'password': 'voter123',
                'full_name': 'Amit Patel',
                'date_of_birth': datetime(1988, 3, 10).date(),
                'phone_number': '+91 9876543212',
                'address': '789 Gandhi Nagar, Ahmedabad, Gujarat 380001',
                'is_verified': True,
                'verification_status': 'approved'
            },
            {
                'username': 'voter4',
                'email': 'voter4@example.com',
                'password': 'voter123',
                'full_name': 'Anjali Singh',
                'date_of_birth': datetime(1992, 11, 5).date(),
                'phone_number': '+91 9876543213',
                'address': '101 Civil Lines, Jaipur, Rajasthan 302001',
                'is_verified': False,
                'verification_status': 'pending'
            },
            {
                'username': 'voter5',
                'email': 'voter5@example.com',
                'password': 'voter123',
                'full_name': 'Suresh Reddy',
                'date_of_birth': datetime(1985, 7, 20).date(),
                'phone_number': '+91 9876543214',
                'address': '202 Banjara Hills, Hyderabad, Telangana 500034',
                'is_verified': True,
                'verification_status': 'approved'
            }
        ]
        
        created_voters = []
        for voter_data in test_voters:
            existing = User.query.filter_by(username=voter_data['username']).first()
            if existing:
                print(f"  ℹ️  Voter '{voter_data['username']}' already exists (ID: {existing.id})")
                created_voters.append(existing)
                continue
            
            voter = User(
                username=voter_data['username'],
                email=voter_data['email'],
                password_hash=generate_password_hash(voter_data['password']),
                full_name=voter_data['full_name'],
                date_of_birth=voter_data['date_of_birth'],
                phone_number=voter_data['phone_number'],
                address=voter_data['address'],
                profile_photo=profile_photo_base64,
                is_verified=voter_data['is_verified'],
                verification_status=voter_data['verification_status']
            )
            db.session.add(voter)
            db.session.flush()
            created_voters.append(voter)
            print(f"  ✅ Created voter: {voter.username} (ID: {voter.id})")
        
        db.session.commit()
        
        # ============================================
        # CREATE TEST CANDIDATE USERS
        # ============================================
        print("\n🎯 CREATING TEST CANDIDATE USERS...")
        
        test_candidate_users = [
            {
                'username': 'candidate1',
                'email': 'candidate1@example.com',
                'password': 'candidate123',
                'full_name': 'Dr. Arun Joshi',
                'phone_number': '+91 9876543220',
                'bio': 'Experienced leader with 15 years of public service. Committed to transparency and development.',
                'is_verified': True,
                'verification_status': 'approved'
            },
            {
                'username': 'candidate2',
                'email': 'candidate2@example.com',
                'password': 'candidate123',
                'full_name': 'Smt. Lakshmi Devi',
                'phone_number': '+91 9876543221',
                'bio': 'Social activist and former teacher. Fighting for education and women empowerment.',
                'is_verified': True,
                'verification_status': 'approved'
            },
            {
                'username': 'candidate3',
                'email': 'candidate3@example.com',
                'password': 'candidate123',
                'full_name': 'Mr. Vikram Singh',
                'phone_number': '+91 9876543222',
                'bio': 'Young entrepreneur focused on job creation and technological advancement.',
                'is_verified': True,
                'verification_status': 'approved'
            },
            {
                'username': 'candidate4',
                'email': 'candidate4@example.com',
                'password': 'candidate123',
                'full_name': 'Dr. Meera Nair',
                'phone_number': '+91 9876543223',
                'bio': 'Renowned doctor and healthcare advocate. Dedicated to improving public health.',
                'is_verified': True,
                'verification_status': 'approved'
            },
            {
                'username': 'candidate5',
                'email': 'candidate5@example.com',
                'password': 'candidate123',
                'full_name': 'Shri. Ramesh Gupta',
                'phone_number': '+91 9876543224',
                'bio': 'Agricultural expert working for farmer welfare and rural development.',
                'is_verified': False,
                'verification_status': 'pending'
            }
        ]
        
        created_candidate_users = []
        for cand_data in test_candidate_users:
            existing = CandidateUser.query.filter_by(username=cand_data['username']).first()
            if existing:
                print(f"  ℹ️  Candidate user '{cand_data['username']}' already exists (ID: {existing.id})")
                created_candidate_users.append(existing)
                continue
            
            candidate_user = CandidateUser(
                username=cand_data['username'],
                email=cand_data['email'],
                password_hash=generate_password_hash(cand_data['password']),
                full_name=cand_data['full_name'],
                phone_number=cand_data['phone_number'],
                bio=cand_data['bio'],
                profile_photo=profile_photo_base64,
                is_verified=cand_data['is_verified'],
                verification_status=cand_data['verification_status']
            )
            db.session.add(candidate_user)
            db.session.flush()
            created_candidate_users.append(candidate_user)
            print(f"  ✅ Created candidate user: {candidate_user.username} (ID: {candidate_user.id})")
        
        db.session.commit()
        
        # ============================================
        # CREATE TEST ELECTIONS
        # ============================================
        print("\n🗳️  CREATING TEST ELECTIONS...")
        
        now = datetime.utcnow()
        
        test_elections = [
            {
                'title': 'Student Council Election 2026',
                'description': 'Annual student council election for selecting the president, vice president, and council members. All registered students are eligible to vote.',
                'start_date': now - timedelta(days=2),
                'end_date': now + timedelta(days=5),
                'is_active': True
            },
            {
                'title': 'Best Teacher Award 2026',
                'description': 'Vote for your favorite teacher of the year. Students and faculty can participate in this election.',
                'start_date': now - timedelta(days=1),
                'end_date': now + timedelta(days=10),
                'is_active': True
            },
            {
                'title': 'Department Head Selection',
                'description': 'Election for selecting the new department head for the Computer Science department.',
                'start_date': now + timedelta(days=5),
                'end_date': now + timedelta(days=15),
                'is_active': True
            },
            {
                'title': 'Cultural Committee Election',
                'description': 'Select members for the cultural committee who will organize events throughout the year.',
                'start_date': now - timedelta(days=30),
                'end_date': now - timedelta(days=10),
                'is_active': False
            },
            {
                'title': 'Sports Captain Election 2026',
                'description': 'Vote for the sports captain who will lead the college sports team in inter-college competitions.',
                'start_date': now + timedelta(days=1),
                'end_date': now + timedelta(days=7),
                'is_active': True
            }
        ]
        
        created_elections = []
        for election_data in test_elections:
            existing = Election.query.filter_by(title=election_data['title']).first()
            if existing:
                print(f"  ℹ️  Election '{election_data['title']}' already exists (ID: {existing.id})")
                created_elections.append(existing)
                continue
            
            election = Election(
                title=election_data['title'],
                description=election_data['description'],
                start_date=election_data['start_date'],
                end_date=election_data['end_date'],
                is_active=election_data['is_active'],
                created_by=admin.id
            )
            db.session.add(election)
            db.session.flush()
            created_elections.append(election)
            print(f"  ✅ Created election: {election.title} (ID: {election.id})")
        
        db.session.commit()
        
        # ============================================
        # CREATE TEST CANDIDATES FOR ELECTIONS
        # ============================================
        print("\n👤 CREATING TEST CANDIDATES FOR ELECTIONS...")
        
        # Define which candidate users participate in which elections
        candidate_assignments = [
            # Student Council Election - 3 candidates
            {'election_idx': 0, 'candidate_user_idx': 0, 'name': 'Dr. Arun Joshi', 'description': 'Running for President - Platform: Transparency and Student Welfare'},
            {'election_idx': 0, 'candidate_user_idx': 1, 'name': 'Smt. Lakshmi Devi', 'description': 'Running for President - Platform: Education and Equal Opportunities'},
            {'election_idx': 0, 'candidate_user_idx': 2, 'name': 'Mr. Vikram Singh', 'description': 'Running for President - Platform: Innovation and Technology'},
            
            # Best Teacher Award - 2 candidates
            {'election_idx': 1, 'candidate_user_idx': 3, 'name': 'Dr. Meera Nair', 'description': 'Professor of Biology - Known for innovative teaching methods'},
            {'election_idx': 1, 'candidate_user_idx': 0, 'name': 'Dr. Arun Joshi', 'description': 'Professor of Mathematics - Dedicated mentor and researcher'},
            
            # Department Head Selection - 2 candidates
            {'election_idx': 2, 'candidate_user_idx': 2, 'name': 'Mr. Vikram Singh', 'description': 'Senior Faculty - Focus on industry collaboration'},
            {'election_idx': 2, 'candidate_user_idx': 3, 'name': 'Dr. Meera Nair', 'description': 'Research Head - Focus on academic excellence'},
            
            # Cultural Committee - 3 candidates (past election)
            {'election_idx': 3, 'candidate_user_idx': 1, 'name': 'Smt. Lakshmi Devi', 'description': 'Coordinator - Traditional arts and culture'},
            {'election_idx': 3, 'candidate_user_idx': 2, 'name': 'Mr. Vikram Singh', 'description': 'Coordinator - Modern events and tech fests'},
            {'election_idx': 3, 'candidate_user_idx': 4, 'name': 'Shri. Ramesh Gupta', 'description': 'Coordinator - Regional cultural programs'},
            
            # Sports Captain Election - 2 candidates
            {'election_idx': 4, 'candidate_user_idx': 2, 'name': 'Mr. Vikram Singh', 'description': 'Former basketball champion - Focus on team sports'},
            {'election_idx': 4, 'candidate_user_idx': 0, 'name': 'Dr. Arun Joshi', 'description': 'Athletic coordinator - Focus on fitness and wellness'},
        ]
        
        for assignment in candidate_assignments:
            election = created_elections[assignment['election_idx']]
            candidate_user = created_candidate_users[assignment['candidate_user_idx']] if assignment['candidate_user_idx'] < len(created_candidate_users) else None
            
            # Check if candidate already exists for this election
            existing = Candidate.query.filter_by(
                election_id=election.id,
                name=assignment['name']
            ).first()
            
            if existing:
                print(f"  ℹ️  Candidate '{assignment['name']}' already exists in '{election.title}'")
                continue
            
            candidate = Candidate(
                name=assignment['name'],
                description=assignment['description'],
                election_id=election.id,
                candidate_user_id=candidate_user.id if candidate_user else None
            )
            db.session.add(candidate)
            print(f"  ✅ Added '{assignment['name']}' to '{election.title}'")
        
        db.session.commit()
        
        # ============================================
        # CREATE TEST AUTHORIZED LOCATIONS
        # ============================================
        print("\n📍 CREATING TEST AUTHORIZED LOCATIONS...")
        
        # Sample locations for elections (Indian cities GPS coordinates)
        test_locations = [
            # Locations for Student Council Election
            {'election_idx': 0, 'lat': 19.0760, 'lng': 72.8777, 'radius': 500, 'name': 'Mumbai - College Campus'},
            {'election_idx': 0, 'lat': 19.0728, 'lng': 72.8826, 'radius': 300, 'name': 'Mumbai - Library Building'},
            
            # Locations for Best Teacher Award
            {'election_idx': 1, 'lat': 28.6139, 'lng': 77.2090, 'radius': 400, 'name': 'Delhi - Main Auditorium'},
            {'election_idx': 1, 'lat': 28.6100, 'lng': 77.2300, 'radius': 350, 'name': 'Delhi - Convention Center'},
            
            # Locations for Department Head Selection
            {'election_idx': 2, 'lat': 12.9716, 'lng': 77.5946, 'radius': 250, 'name': 'Bangalore - CS Department'},
            
            # Locations for Cultural Committee
            {'election_idx': 3, 'lat': 22.5726, 'lng': 88.3639, 'radius': 600, 'name': 'Kolkata - Cultural Hall'},
            
            # Locations for Sports Captain Election
            {'election_idx': 4, 'lat': 23.0225, 'lng': 72.5714, 'radius': 450, 'name': 'Ahmedabad - Sports Complex'},
            {'election_idx': 4, 'lat': 23.0300, 'lng': 72.5800, 'radius': 300, 'name': 'Ahmedabad - Stadium'},
        ]
        
        for loc_data in test_locations:
            election = created_elections[loc_data['election_idx']]
            
            # Check if similar location exists
            existing = AuthorizedLocation.query.filter_by(
                election_id=election.id,
                latitude=loc_data['lat'],
                longitude=loc_data['lng']
            ).first()
            
            if existing:
                print(f"  ℹ️  Location at ({loc_data['lat']}, {loc_data['lng']}) already exists for '{election.title}'")
                continue
            
            location = AuthorizedLocation(
                id=str(uuid.uuid4()),
                election_id=election.id,
                latitude=loc_data['lat'],
                longitude=loc_data['lng'],
                radius=loc_data['radius'],
                created_by=admin.id
            )
            db.session.add(location)
            print(f"  ✅ Added location: {loc_data['name']} for '{election.title}'")
        
        db.session.commit()
        
        # ============================================
        # CREATE TEST DOCUMENTS
        # ============================================
        print("\n📄 CREATING TEST DOCUMENTS...")
        
        docs_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'documents')
        
        # Create sample document files
        sample_documents = [
            {'filename': 'aadhar_voter1.txt', 'content': 'Sample Aadhar Card - Voter 1\nAadhar No: 1234-5678-9012'},
            {'filename': 'passport_voter2.txt', 'content': 'Sample Passport - Voter 2\nPassport No: A1234567'},
            {'filename': 'license_voter3.txt', 'content': 'Sample Driving License - Voter 3\nLicense No: MH01-2020-0012345'},
            {'filename': 'pancard_candidate1.txt', 'content': 'Sample PAN Card - Candidate 1\nPAN No: ABCDE1234F'},
            {'filename': 'aadhar_candidate2.txt', 'content': 'Sample Aadhar Card - Candidate 2\nAadhar No: 9876-5432-1098'},
        ]
        
        # Create sample files on disk
        for doc in sample_documents:
            file_path = os.path.join(docs_dir, doc['filename'])
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(doc['content'])
        
        # Document assignments
        document_data = [
            {'voter_idx': 0, 'candidate_idx': None, 'type': 'aadhar', 'file': 'aadhar_voter1.txt', 'status': 'approved'},
            {'voter_idx': 1, 'candidate_idx': None, 'type': 'passport', 'file': 'passport_voter2.txt', 'status': 'approved'},
            {'voter_idx': 2, 'candidate_idx': None, 'type': 'license', 'file': 'license_voter3.txt', 'status': 'pending'},
            {'voter_idx': None, 'candidate_idx': 0, 'type': 'pancard', 'file': 'pancard_candidate1.txt', 'status': 'approved'},
            {'voter_idx': None, 'candidate_idx': 1, 'type': 'aadhar', 'file': 'aadhar_candidate2.txt', 'status': 'approved'},
        ]
        
        for doc_data in document_data:
            file_path = os.path.join(docs_dir, doc_data['file'])
            
            if not os.path.exists(file_path):
                print(f"  ⚠️  File not found: {file_path}")
                continue
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Check if document already exists
            existing = Document.query.filter_by(file_hash=file_hash).first()
            if existing:
                print(f"  ℹ️  Document '{doc_data['file']}' already exists")
                continue
            
            user_id = created_voters[doc_data['voter_idx']].id if doc_data['voter_idx'] is not None else None
            candidate_id = created_candidate_users[doc_data['candidate_idx']].id if doc_data['candidate_idx'] is not None else None
            
            document = Document(
                user_id=user_id,
                candidate_id=candidate_id,
                document_type=doc_data['type'],
                file_path=file_path,
                file_hash=file_hash,
                file_size=os.path.getsize(file_path),
                mime_type='text/plain',
                status=doc_data['status'],
                reviewed_by=admin.id if doc_data['status'] != 'pending' else None,
                reviewed_at=datetime.utcnow() if doc_data['status'] != 'pending' else None
            )
            db.session.add(document)
            owner_name = created_voters[doc_data['voter_idx']].full_name if user_id else created_candidate_users[doc_data['candidate_idx']].full_name
            print(f"  ✅ Created document: {doc_data['type']} for {owner_name}")
        
        db.session.commit()
        
        # ============================================
        # SUMMARY
        # ============================================
        print("\n" + "=" * 60)
        print("✅ TEST DATA POPULATION COMPLETE!")
        print("=" * 60)
        
        print("\n📊 DATABASE SUMMARY:")
        print(f"  👥 Voters: {User.query.count()}")
        print(f"  🎯 Candidate Users: {CandidateUser.query.count()}")
        print(f"  🗳️  Elections: {Election.query.count()}")
        print(f"  👤 Candidates (in elections): {Candidate.query.count()}")
        print(f"  📍 Authorized Locations: {AuthorizedLocation.query.count()}")
        print(f"  📄 Documents: {Document.query.count()}")
        
        print("\n🔐 TEST CREDENTIALS:")
        print("  VOTERS:")
        for v in test_voters[:3]:
            print(f"    - Username: {v['username']}, Password: {v['password']}")
        print("  CANDIDATES:")
        for c in test_candidate_users[:3]:
            print(f"    - Username: {c['username']}, Password: {c['password']}")
        print("  ADMIN:")
        print(f"    - Username: admin, Password: admin123")
        
        print("\n✅ All test data has been created successfully!")


if __name__ == '__main__':
    populate_test_data()
