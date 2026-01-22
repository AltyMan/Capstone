from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict

habits_bp = Blueprint("habits", __name__)

@habits_bp.post(f'/<int:user_id>/{habits_bp.name}/add')
def post_add_habit(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    is_device: bool = request.args.get('device', type=bool)
    
    if is_device is None:
        is_device = False
    
    user.add_habit(habit_name, is_device)
    
    return {
        "response":
            f"successfully added Habit {habit_name}"
    }, 200

@habits_bp.get(f'/<int:user_id>/{habits_bp.name}')
def get_habits(user_id: int):
    user = User(user_id)
    return {
        "habits":
            [
                asdict(h) for h in user.get_habits()
            ]
    }, 200

@habits_bp.post(f'/<int:user_id>/{habits_bp.name}/update')
def post_update_habit(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    field: str = request.args.get('field')
    value: str = request.args.get('value')
    
    user.update_habit(field, value, habit_name)
    
    return {
        "response":
            f"Successfully updated Habit {habit_name} ({field}:{value})"
    }, 200

@habits_bp.post(f'/<int:user_id>/{habits_bp.name}/delete')
def post_delete_habit(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    
    user.delete_habit(habit_name)
    
    return {
        "response":
            f"Successfully deleted Habit {habit_name}"
    }, 200
