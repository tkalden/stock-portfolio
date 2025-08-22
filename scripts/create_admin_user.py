#!/usr/bin/env python3
"""
Script to create an admin user for testing
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utilities.userFunction import UserCRUD
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create an admin user"""
    user_crud = UserCRUD()
    
    admin_email = "admin@stocknity.com"
    admin_name = "Admin User"
    admin_password = "Admin123!"  # You can change this password
    
    # Check if admin user already exists
    existing_user = user_crud.get_user_by_email(admin_email)
    if existing_user:
        print(f"Admin user {admin_email} already exists!")
        return False
    
    # Create admin user
    hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
    success = user_crud.save_user_data(admin_email, admin_name, hashed_password)
    
    if success:
        print(f"✅ Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print(f"Name: {admin_name}")
        print("\nYou can now log in with these credentials to access admin features.")
        return True
    else:
        print("❌ Failed to create admin user")
        return False

if __name__ == "__main__":
    print("Creating admin user...")
    create_admin_user() 