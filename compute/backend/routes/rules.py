from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict

rules_bp = Blueprint("rules", __name__)

@rules_bp.post(f'/<int:user_id>/{rules_bp.name}/add')
def post_add_rule(user_id: int):
    return

@rules_bp.get(f'/<int:user_id>/{rules_bp.name}')
def get_rules(user_id: int):
    return

@rules_bp.post(f'/<int:user_id>/{rules_bp.name}/update')
def post_update_rule(user_id: int):
    return

@rules_bp.post(f'/<int:user_id>/{rules_bp.name}/delete')
def post_delete_rule(user_id: int):
    return