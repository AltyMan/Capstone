from flask import Blueprint, Response, request
from objects.user import User
from objects.habit import Habit
from dataclasses import asdict

"""
Habits Blueprint (Flask)

Provides HTTP endpoints for managing user habits through a simple REST-style API.

This module exposes a Flask `Blueprint` that wraps the `User` service layer and
allows clients to create, list, update, and delete habits associated with a
specific user. All routes are scoped by `user_id`.

Routes
------
POST   /<user_id>/habits/add
    Add a new habit.

GET    /<user_id>/habits
    Retrieve all habits for the user.

POST   /<user_id>/habits/update
    Update a specific habit field.

POST   /<user_id>/habits/delete
    Delete a habit.

Query Parameters
----------------
name : str
    Habit name.
device : bool, optional
    Whether the habit is associated with a device.
field : str
    Column name to update (for updates).
value : str
    New value for the field.

Notes
-----
- Delegates business logic to the `User` class.
- Returns JSON responses only.
- Uses query parameters instead of request bodies for simplicity.
"""


habits_bp = Blueprint("habits", __name__)


@habits_bp.post(f'/<int:user_id>/{habits_bp.name}/add')
def post_add_habit(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    is_device: bool = request.args.get('device', type=bool)

    if is_device is None:
        is_device = False

    user.add_habit(habit_name, is_device)

    # NOTE (Habo): Right now the mobile client only checks for a 200 status
    # code here and then re-fetches the full list of habits. If you want to
    # optimize this later, you can return the created habit (asdict) so the
    # client can grab the id without an extra GET.
    return {
        "response": asdict(Habit(habit_name=habit_name, is_device=is_device))
    }, 200

@habits_bp.get(f'/<int:user_id>/{habits_bp.name}')
def get_habits(user_id: int):
    user = User(user_id)

    # NOTE (Habo): Any new fields you add to `objects.Habit` (or whatever
    # DTO you decide to expose) will automatically show up in the JSON here
    # because we use `asdict`. The Flutter side currently ignores unknown
    # keys, so extending the schema is backwards compatible.
    return {
        "habits": [
            asdict(h) for h in user.get_habits()
        ]
    }, 200


@habits_bp.post(f'/<int:user_id>/{habits_bp.name}/update')
def post_update_habit(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    field: str = request.args.get('field')
    value: str = request.args.get('value')

    # TODO (Habo): This generic "field/value" update is currently only used
    # by the mobile app to toggle the `is_device` flag. If you add support
    # for more Habo fields, consider validating the field name against an
    # allowed list or replacing this with a typed update endpoint that
    # accepts structured JSON instead of arbitrary column names.
    user.update_habit(field, value, habit_name)

    return {
        "response":
            f"Successfully updated Habit {habit_name} ({field}:{value})"
    }, 200
    
    
"""
- POST /<user_id>/habits/update?name=&field=&value=
      Used right now to toggle the ``is_device`` flag only. The Habo app
      will need a richer update story (e.g. updating title, cue, reward,
      numeric targets, etc.) if you choose to expose all of Habo's fields.

      TODO (backend/frontend): In the future, you may want to add a JSON-body
      endpoint such as:

          PUT /<user_id>/habits/<habit_id>

      that accepts a full Habo-style payload and updates all relevant columns
      in one go instead of field-by-field query params.
"""
@habits_bp.put(f'/<int:user_id>/{habits_bp.name}/<habit_id>')
def put_update_habit(user_id: int, habit_id: str):
    user = User(user_id)
    
    return 200

"""
- POST /<user_id>/habits/delete?name=
      Currently deletes by name. The mobile code compensates by resolving
      id → name first, but an id-based delete endpoint would be more robust.

      TODO (backend): Add a route such as:

          POST /<user_id>/habits/delete/<habit_id>

      and have it delete by primary key instead of name.
"""
@habits_bp.post(f'/<int:user_id>/{habits_bp.name}/delete')
def post_delete_habit(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')

    # NOTE (Habo): The mobile app currently resolves habit id → name on the
    # client side and then calls this route. If you later add a delete-by-id
    # endpoint, you can keep this one for backwards compatibility.
    user.delete_habit(habit_name)

    return {
        "response":
            f"Successfully deleted Habit {habit_name}"
    }, 200
