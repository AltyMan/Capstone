from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict

logs_bp = Blueprint("logs", __name__)

@logs_bp.post(f'/<int:user_id>/{logs_bp.name}/add')
def post_add_log(user_id: int):
    return

@logs_bp.get(f'/<int:user_id>/{logs_bp.name}')
def get_logs(user_id: int):
    return

@logs_bp.post(f'/<int:user_id>/{logs_bp.name}/update')
def post_update_log(user_id: int):
    return

@logs_bp.post(f'/<int:user_id>/{logs_bp.name}/delete')
def post_delete_log(user_id: int):
    return

# @habits_bp.get("/<int:user_id>/habits/logs")
# def get_user_logs(user_id: int):
#     user = User(user_id)
#     return {
#         "logs" : user.get_habit_logs().to_dict()
#     }

# @habits_bp.post("/<int:user_id>/habits/log")
# def post_user_log(user_id: int):
#     user = User(user_id)
#     habit_name: str = request.args.get('name')
#     state: str = request.args.get('state')
#     self_reported: str = request.args.get('reported')
#     user.log_habit(habit_name, state, self_reported)