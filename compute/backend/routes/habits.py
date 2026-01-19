from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict

# from config import logger

# from services.users import get_user
# from models.user import User

habits_bp = Blueprint("habits", __name__)

@habits_bp.get("/<int:user_id>/habits")
def get_user_habits(user_id: int):
    user = User(user_id)
    return {
        "habits": [asdict(h) for h in user.get_habits()]
    }, 200
    
@habits_bp.get("/<int:user_id>/habits/logs")
def get_user_logs(user_id: int):
    user = User(user_id)
    return {
        "logs" : user.get_habit_logs().to_dict()
    }

@habits_bp.post("/<int:user_id>/habits/log")
def post_user_log(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    state: str = request.args.get('state')
    self_reported: str = request.args.get('reported')
    user.log_habit(habit_name, state, self_reported)

@habits_bp.post("/<int:user_id>/habits/add")
def post_user_add_habit(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    is_device: bool = request.args.get('device', type=bool)
    user.add_habit(habit_name, is_device)