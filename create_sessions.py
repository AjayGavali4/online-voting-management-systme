"""
Direct session login for screenshot capture
This script creates session cookies that allow direct access to voter/candidate pages
"""

from app import app, db
from models import User, CandidateUser
from flask import session
from flask_login import login_user
import uuid

def create_voter_session():
    """Create a logged-in session for voter"""
    with app.app_context():
        with app.test_client() as client:
            with client.session_transaction() as sess:
                voter = User.query.filter_by(username='testvoter').first()
                if voter:
                    sess['_user_id'] = f'voter:{voter.id}'
                    sess['_fresh'] = True
                    sess['user_session_id'] = str(uuid.uuid4())
                    print(f"Voter session created for user ID: {voter.id}")
                    return sess
    return None

def create_candidate_session():
    """Create a logged-in session for candidate"""
    with app.app_context():
        with app.test_client() as client:
            with client.session_transaction() as sess:
                candidate = CandidateUser.query.filter_by(username='testcandidate').first()
                if candidate:
                    sess['_user_id'] = f'candidate:{candidate.id}'
                    sess['_fresh'] = True
                    sess['user_session_id'] = str(uuid.uuid4())
                    print(f"Candidate session created for user ID: {candidate.id}")
                    return sess
    return None

if __name__ == "__main__":
    create_voter_session()
    create_candidate_session()
