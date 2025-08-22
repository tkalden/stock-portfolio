#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash, check_password_hash
from utilities.redis_data import redis_manager
from utilities.userFunction import UserCRUD
from utilities.model import User

def test_login():
    """Test the login functionality step by step"""
    
    print("=== Testing Login Functionality ===")
    
    # Test 1: Check if Redis is available
    print("\n1. Checking Redis availability...")
    if redis_manager.available:
        print("✓ Redis is available")
    else:
        print("✗ Redis is not available")
        return
    
    # Test 2: Check if user exists in Redis
    print("\n2. Checking if user exists in Redis...")
    email = "test@stocknity.com"
    user_data = redis_manager.get_user_by_email(email)
    if user_data:
        print(f"✓ User found: {user_data}")
    else:
        print("✗ User not found in Redis")
        return
    
    # Test 3: Test UserCRUD.get_user_by_email
    print("\n3. Testing UserCRUD.get_user_by_email...")
    user_crud = UserCRUD()
    user_obj = user_crud.get_user_by_email(email)
    if user_obj:
        print(f"✓ UserCRUD returned user object: {user_obj}")
        print(f"  - Email: {user_obj.email}")
        print(f"  - Name: {user_obj.name}")
        print(f"  - Password: {user_obj.password[:20]}...")
        print(f"  - ID: {user_obj.id}")
    else:
        print("✗ UserCRUD.get_user_by_email returned None")
        return
    
    # Test 4: Test User.get (static method)
    print("\n4. Testing User.get (static method)...")
    try:
        user = User.get(email)
        if user:
            print(f"✓ User.get returned user object: {user}")
            print(f"  - Email: {user.email}")
            print(f"  - Name: {user.name}")
            print(f"  - Password: {user.password[:20]}...")
            print(f"  - ID: {user.id}")
        else:
            print("✗ User.get returned None")
            return
    except Exception as e:
        print(f"✗ User.get threw exception: {e}")
        return
    
    # Test 5: Test password verification
    print("\n5. Testing password verification...")
    password = "hello@23"
    try:
        is_valid = check_password_hash(user.password, password)
        print(f"✓ Password verification result: {is_valid}")
        if is_valid:
            print("✓ Password is correct!")
        else:
            print("✗ Password is incorrect")
    except Exception as e:
        print(f"✗ Password verification threw exception: {e}")
        return
    
    # Test 6: Test with wrong password
    print("\n6. Testing with wrong password...")
    wrong_password = "wrongpassword"
    try:
        is_valid = check_password_hash(user.password, wrong_password)
        print(f"✓ Wrong password verification result: {is_valid}")
        if not is_valid:
            print("✓ Correctly rejected wrong password")
        else:
            print("✗ Incorrectly accepted wrong password")
    except Exception as e:
        print(f"✗ Wrong password verification threw exception: {e}")

if __name__ == "__main__":
    test_login() 