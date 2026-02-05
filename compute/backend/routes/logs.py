from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict
import pandas as pd

logs_bp = Blueprint("logs", __name__)

@logs_bp.post(f'/<int:user_id>/{logs_bp.name}/add')
def post_add_log(user_id: int):
    user = User(user_id)
    
    habit_name: str = request.args.get('name')
    state: str = request.args.get('state')
    self_reported: bool = request.args.get('reported', type=bool)
    
    user.log_habit(habit_name, state, self_reported)
    
    return {
        "result" : f"Successfully logged habit {habit_name} ({state}:{self_reported})"
    }, 200

@logs_bp.get(f'/<int:user_id>/{logs_bp.name}')
def get_logs(user_id: int):
    user = User(user_id)
    
    habit_name: str = request.args.get('name')
    
    df: pd.DataFrame = user.get_habit_logs(habit_name)
    
    return {
        df.to_json(orient="records")
    }, 200

@logs_bp.post(f'/<int:user_id>/{logs_bp.name}/update')
def post_update_log(user_id: int):
    user = User(user_id)
    
    id: int = request.args.get('id', type=int)
    field: str = request.args.get('field')
    value: str = request.args.get('value')
    
    # TODO: need to verify field value change in type, could break here.
    
    user.update_log(id, field, value)
    
    return {
        "result" : f"Successfully updated log {id} {field} -> {value}"
    }, 200

@logs_bp.post(f'/<int:user_id>/{logs_bp.name}/delete')
def post_delete_log(user_id: int):
    user = User(user_id)
    
    id: int = request.args.get('id', type=int)
    
    user.delete_log(id)
    
    return {
        "result" : f"Successfully deleted log {id}"
    }, 200