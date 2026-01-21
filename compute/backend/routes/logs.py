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