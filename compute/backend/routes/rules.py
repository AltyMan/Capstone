from flask import Blueprint, Response, request
from objects.user import User
from objects.rule import Rule
from dataclasses import asdict

"""
Rules Blueprint (Flask)

Provides HTTP endpoints for managing habit scheduling rules.

INTEGRATION NOTES FOR HABO (Flutter) FRONTEND
-----------------------------------------------
The current `/rules` routes use a `Rule` dataclass that matches Habo's basic
rule concept (day, hour, minute, active), but Habo does NOT currently have
an HTTP repository implementation for rules.

The mobile app's `HabitsManager` uses rules for notifications/reminders, but
these are currently stored only in SQLite via `HaboModel` and not exposed
through any HTTP API.

If you want to sync rules to the backend in the future:
  - The `objects.rule.Rule` dataclass structure is compatible with what Habo
    would need (day, hour, minute, active).
  - You would need to create an `HttpRuleRepository` in the Flutter app that
    mirrors the pattern used by `HttpHabitRepository`.
  - The routes here (`/<user_id>/rules/add`, `/<user_id>/rules`, etc.) could
    be used as-is, but you'd need to ensure rules are tied to habit IDs (not
    just habit names) for proper foreign key relationships.

NOTE: Habo's notification system uses rules internally, but the app does not
currently expose rule management through the UI in a way that would require
backend sync. Rules are typically auto-generated or managed locally.
"""

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