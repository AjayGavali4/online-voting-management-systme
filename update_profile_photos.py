"""
Update Profile Photos Script
Updates all test users and candidates with a specific profile photo
"""

import os
import base64
from app import app, db
from models import User, CandidateUser


def update_profile_photos(image_path):
    """Update all users and candidates with the specified profile photo"""
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        print("Please provide a valid image path.")
        return False
    
    # Read and encode the image
    print(f"📷 Loading image from: {image_path}")
    with open(image_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    print(f"   Image size: {len(image_data)} bytes")
    print(f"   Base64 length: {len(image_base64)} characters")
    
    with app.app_context():
        # Update all voters
        voters = User.query.all()
        print(f"\n👥 Updating {len(voters)} voter(s)...")
        for voter in voters:
            voter.profile_photo = image_base64
            print(f"   ✅ Updated: {voter.username} ({voter.full_name})")
        
        # Update all candidate users
        candidates = CandidateUser.query.all()
        print(f"\n🎯 Updating {len(candidates)} candidate(s)...")
        for candidate in candidates:
            candidate.profile_photo = image_base64
            print(f"   ✅ Updated: {candidate.username} ({candidate.full_name})")
        
        db.session.commit()
        print("\n✅ All profile photos updated successfully!")
        
        # Also copy to uploads/profile_photos for reference
        profile_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'profile_photos')
        os.makedirs(profile_dir, exist_ok=True)
        
        dest_path = os.path.join(profile_dir, 'sample_profile.jpg')
        with open(dest_path, 'wb') as f:
            f.write(image_data)
        print(f"📁 Saved copy to: {dest_path}")
        
    return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        image_file = sys.argv[1]
    else:
        # Default path - user should update this
        image_file = os.path.join(os.path.dirname(__file__), 'profile_photo.jpg')
        
        if not os.path.exists(image_file):
            print("=" * 60)
            print("PROFILE PHOTO UPDATE SCRIPT")
            print("=" * 60)
            print("\nUsage: python update_profile_photos.py <path_to_image>")
            print("\nExample:")
            print("  python update_profile_photos.py C:\\Users\\YourName\\photo.jpg")
            print("\nOr save your photo as 'profile_photo.jpg' in the project folder")
            print("and run: python update_profile_photos.py")
            print("=" * 60)
            sys.exit(1)
    
    update_profile_photos(image_file)
