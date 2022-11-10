from flask_login import UserMixin
from typing import Dict, Optional
from utilities.userFunction import UserCRUD

users: Dict[str, "User"] = {}

class User(UserMixin):

    def __init__(self, id: str, name: str, email: str, password: str):
        self.id = id
        self.email = email
        self.password = password
        self.name = name

    def __str__(self) -> str:
        return f"<id: {self.id}, name: {self.name}, email: {self.email}>"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        return users.get(user_id)
    
    @staticmethod
    def updateUserData(email) -> Optional["User"]:
        return list(map_df_to_users(email))

def map_df_to_users(email):
    user_data = UserCRUD.get_user_by_email(email)
    for row in user_data.itertuples(index=True, name='Pandas'):
        id = row.id
        users[id] = User(
            id=id,
            name=row.name,
            email=row.email,
            password=row.password,
        )
    return users.values()
