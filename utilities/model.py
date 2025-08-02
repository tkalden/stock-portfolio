from typing import Dict, Optional

from flask_login import UserMixin

from utilities.userFunction import UserCRUD

UserCRUD = UserCRUD()

class User(UserMixin):

    def __init__(self, name: str, email: str, password: str, user_id: str = None, is_admin: bool = False):
        self.email = email
        self.password = password
        self.name = name
        self.id = user_id or email  # Flask-Login requires an id attribute
        self.is_admin = is_admin

    def __str__(self) -> str:
        return f"<name: {self.name}, email: {self.email}, admin: {self.is_admin}>"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def get(identifier: str) -> Optional["User"]:
        """Get user by email or user_id - returns User object or None"""
        return User.updateUserData(identifier)
    
    @staticmethod
    def updateUserData(identifier: str) -> Optional["User"]:
        """Update user data from storage - returns User object or None"""
        return map_df_to_users(identifier)

def map_df_to_users(identifier: str) -> Optional[User]:
    """Map user data from storage to User object"""
    # Try to get user by email first
    user_data = UserCRUD.get_user_by_email(identifier)
    
    # If not found by email, try to get by user_id (if identifier looks like a UUID)
    if user_data is None and len(identifier) == 36 and '-' in identifier:
        # This might be a UUID, try to find user by ID
        user_data = UserCRUD.get_user_by_id(identifier)
    
    if user_data is None:
        return None
    
    try:
        # Check if user is admin (simple check for now)
        is_admin = user_data.email == 'admin@stocknity.com'
        
        return User(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            user_id=user_data.id,
            is_admin=is_admin
        )
    except AttributeError as e:
        # Handle case where user_data doesn't have expected attributes
        print(f"Error creating User object: {e}")
        return None
