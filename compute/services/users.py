from flask import abort
from models.user import User

USERS: dict[int, User] = {}

def get_user(user_id: int) -> User:
    user = USERS.get(user_id)
    if not user:
        abort(404, f"User {user_id} not found")
    return user
