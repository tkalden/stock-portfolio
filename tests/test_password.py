#!/usr/bin/env python3

from werkzeug.security import check_password_hash

def test_password():
    """Test different passwords against the stored hash"""
    
    # The stored password hash from Redis
    stored_hash = "sha256$TM4YDEL2qVslOKc9$4c182a4e607061452b693d1a1ac90c0e218600013e252148654d780f9be7e58b"
    
    # Common passwords to test
    test_passwords = [
        "hello@23",
        "hello123",
        "password",
        "test",
        "123456",
        "admin",
        "hello",
        "test123",
        "password123",
        "hello@123",
        "hello@2023",
        "test@123",
        "test@2023",
        "stocknity",
        "stocknity123",
        "stocknity@123",
        "stocknity@2023"
    ]
    
    print("Testing passwords against the stored hash...")
    print(f"Stored hash: {stored_hash}")
    print("-" * 50)
    
    for password in test_passwords:
        try:
            is_valid = check_password_hash(stored_hash, password)
            if is_valid:
                print(f"✓ MATCH FOUND! Password is: '{password}'")
                return password
            else:
                print(f"✗ '{password}' - No match")
        except Exception as e:
            print(f"✗ '{password}' - Error: {e}")
    
    print("-" * 50)
    print("No matching password found in the test list.")
    return None

if __name__ == "__main__":
    result = test_password()
    if result:
        print(f"\nThe correct password is: {result}")
    else:
        print("\nThe password was not found in the test list.")
        print("You may need to try different passwords or check how the user was created.") 