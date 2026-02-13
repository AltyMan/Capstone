from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict
import pandas as pd

"""
Logs Blueprint (Flask)

Provides HTTP endpoints for managing habit log entries.

INTEGRATION NOTES FOR HABO (Flutter) FRONTEND
-----------------------------------------------
The current `/logs` routes are designed for a simpler log model (state strings,
self_reported flags) and do NOT match Habo's event system.

Habo uses a different concept called "Events" (see `mobile/Habo/lib/repositories/event_repository.dart`):
  - Events are tied to a specific habit ID and a specific date (DateTime).
  - Each event is a List containing:
    - [0]: DayType enum (clear, check, fail, skip, progress)
    - [1]: comment (string, optional)
    - [2]: progressValue (double, optional, only for numeric habits with DayType.progress)

The mobile app's `HttpEventRepository` expects routes under `/<user_id>/events`:
  - POST   /<user_id>/events/add          (JSON body: {habitId, date, eventData})
  - POST   /<user_id>/events/delete        (JSON body: {habitId, date})
  - GET    /<user_id>/events/habit/<habit_id>
  - GET    /<user_id>/events/habit/<habit_id>/map
  - POST   /<user_id>/events/habit/<habit_id>/clear
  - POST   /<user_id>/events/habit/<habit_id>/batch  (JSON body: {habitId, events: {date: eventData}})
  - POST   /<user_id>/events/clear-all

See `backend/HABO_API_SPECIFICATION.md` for the full event API specification.

TODO (backend): Decide whether to:
  1. Extend these `/logs` routes to also support Habo's event format, OR
  2. Create new `/events` routes specifically for Habo and keep `/logs` for your
     existing IoT/device logging use case.
"""

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
    
    if df is None:
        df = pd.DataFrame()
    
    return {
        "result" : df.to_dict(orient="records")
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