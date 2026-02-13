from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict

"""
Users Blueprint (Flask)

Provides a combined endpoint that returns all user data (habits, logs, rules).

INTEGRATION NOTES FOR HABO (Flutter) FRONTEND
-----------------------------------------------
The Habo mobile app does NOT currently use this endpoint. It fetches habits,
events, and categories separately through their respective repository interfaces.

If you want to optimize for bulk data loading in the future, you could:
  1. Extend this endpoint to also return events and categories in the response.
  2. Create an `HttpBackupRepository` that uses this endpoint (or a similar bulk
     export endpoint) for backup/restore operations.

For now, this endpoint remains useful for your existing IoT/device use case
but is not required for Habo integration.
"""

users_bp = Blueprint("users", __name__)

@users_bp.get(f'/<int:user_id>')
def get_user_info(user_id: int):
    user = User(user_id)
    
    habit_list = user.get_habits()
    
    log_list = user.get_habit_logs()
    
    rule_list = user.get_rules()
    
    return {
        "habits" : habit_list,
        "logs" : log_list.to_dict(),
        "rules" : rule_list
    }, 200