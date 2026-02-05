from flask import Blueprint, Response, request
from objects.user import User
from objects.rule import Rule
from dataclasses import asdict

rules_bp = Blueprint("rules", __name__)

@rules_bp.post(f'/<int:user_id>/{rules_bp.name}/add')
def post_add_rule(user_id: int):
    user = User(user_id)
    
    habit_name: str = request.args.get('habit')
    day: int = request.args.get('day', type=int)
    hour: int = request.args.get('hour', type=int)
    minute: int = request.args.get('minute', type=int)
    active: bool = request.args.get('active', type=bool)
    
    user.add_rule(habit_name, Rule(day, hour, minute, active))
    
    return {
        "result" : f"Successfully added rule ({day}:{hour}:{minute}:{active}) to habit {habit_name}"
    }, 200

@rules_bp.get(f'/<int:user_id>/{rules_bp.name}')
def get_rules(user_id: int):
    user = User(user_id)
    
    rule_list = user.get_rules()
    
    return {
        "result" : rule_list
    }, 200

@rules_bp.post(f'/<int:user_id>/{rules_bp.name}/update')
def post_update_rule(user_id: int):
    user = User(user_id)
    
    habit_name: str = request.args.get('habit')
    
    user.update_rule(habit_name)
    
    return {
        "result" : f"Successfully started updating habit rules for habit {habit_name}"
    }

@rules_bp.post(f'/<int:user_id>/{rules_bp.name}/delete')
def post_delete_rule(user_id: int):
    user = User(user_id)
    
    habit_name: str = request.args.get('habit')
    
    user.delete_rule(f"{user.id}_{habit_name}_test")
    
    return {
        "result" : f"Successfully deleted all habit rules associated with habit {habit_name}"
    }