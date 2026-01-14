from flask import Blueprint, Response, request
from objects.user import User
from dataclasses import asdict

# from config import logger

# from services.users import get_user
# from models.user import User

habits_bp = Blueprint("habits", __name__)

@habits_bp.get("/<int:user_id>/habits")
def get_user_habits(user_id: int):
    user = User(user_id)
    return {
        "habits": [asdict(h) for h in user.get_habits()]
    }, 200
    
@habits_bp.get("/<int:user_id>/habits/logs")
def get_user_logs(user_id: int):
    user = User(user_id)
    return {
        "logs" : user.get_habit_logs().to_dict()
    }

@habits_bp.post("<int:user_id>/habits/log")
def post_user_log(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    state: str = request.args.get('state')
    self_reported: str = request.args.get('reported')
    user.log_habit(habit_name, state, self_reported)

@habits_bp.post("<int:user_id>/habits/add")
def post_user_add_habit(user_id: int):
    user = User(user_id)
    habit_name: str = request.args.get('name')
    is_device: bool = request.args.get('device', type=bool)
    user.add_habit(habit_name, is_device)


# @DeprecationWarning
# @habits_bp.get("/<int:user_id>/get-habits")
# def get_user_habits(user_id: int):
#     user: User = get_user(user_id)
#     logger.info(f"User {user_id} -> GET_USER_HABITS")
#     return {"habits": user.print_user_habits()}
# @DeprecationWarning
# @habits_bp.get("/<int:user_id>/get-habit/<habit_name>/rules")
# def get_user_habit_rules(user_id: int, habit_name: str):
#     user: User = get_user(user_id)
#     logger.info(f"User {user_id} -> GET_HABIT_{habit_name}_RULES")
#     return {"habits": user.print_habit_rules(habit_name)}
# @DeprecationWarning
# @habits_bp.get("/<int:user_id>/get-habit-rules")
# def get_user_rules(user_id: int):
#     user: User = get_user(user_id)
#     logger.info(f"User {user_id} -> GET_HABIT_ALL_RULES")
#     return {"habits": user.print_habit_rules(None)}
# @DeprecationWarning
# @habits_bp.get("/<int:user_id>")
# def update_user(user_id: int):
#     user: User = get_user(user_id)
#     user.update_user_habits()
#     logger.info(f"User {user_id} -> GET_UPDATE_USER")
#     return {"habits": "updated"}
# @DeprecationWarning
# @habits_bp.get("/<int:user_id>/summary")
# def get_user_summary(user_id: int):
#     logger.warn(f"User {user_id} -> GET_USER_SUMMARY")
#     return "Not implemented", 501
# @DeprecationWarning
# @habits_bp.get("/<int:user_id>/trends")
# def get_user_trends(user_id: int):
#     logger.warn(f"User {user_id} -> GET_USER_TRENDS")
#     return "Not implemented", 501
# @DeprecationWarning
# @habits_bp.get("/<int:user_id>/streak")
# def get_user_streak(user_id: int):
#     logger.warn(f"User {user_id} -> GET_USER_STREAKS")
#     return "Not implemented", 501
# @DeprecationWarning
# @habits_bp.post("/<int:user_id>/log-habit")
# def log_user_habit(user_id: int):
#     habit_name = request.args.get("habit")
#     if habit_name is None:
#         return {"error": "The habit name is required"}, 400
    
#     user: User = get_user(user_id)
#     user_habits = user._get_user_habits()
#     if habit_name not in user_habits:
#         logger.error(f"User {user_id} -> POST_LOG_HABIT ({habit_name})")
#         return {"error": "The habit requested does not exist"}, 400
    
#     user._log_user_habit(habit_name)
#     logger.info(f"User {user_id} -> POST_LOG_HABIT ({habit_name})")
#     return {"success": f"The habit requested ({habit_name}) was logged accordingly"}, 200
    
# @DeprecationWarning
# @habits_bp.post("/<int:user_id>/reschedule")
# def reschedule_user_jobs(user_id: int):
#     logger.warn(f"User {user_id} -> USER_RESCHEDULE")
#     return "Not implemented", 501
