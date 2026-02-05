from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict

users_bp = Blueprint("users", __name__)

@users_bp.get(f'/<int:user_id>')
def get_user_info(user_id: int):
    user = User(user_id)
    
    habit_list = user.get_habits()
    
    log_list = user.get_habit_logs()
    
    rule_list = user.get_rules()
    
    return {
        "habits" : habit_list,
        "logs" : log_list.to_json(),
        "rules" : rule_list
    }, 200