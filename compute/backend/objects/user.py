import pandas as pd
from datetime import datetime
from typing import Optional
from objects.habit import Habit
from objects.rule import Rule
from objects.habitrepository import HabitRepository
from db.sqlite import get_connection

# CRUD Operations

class User:
    
    @staticmethod
    def create() -> "User":
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users DEFAULT VALUES;"
            )
            user_id = cursor.lastrowid
        return User(user_id)
        
    def __init__(self, user_id: int):
        self.id = user_id
        self.repo = HabitRepository(user_id)
    
    def add_habit(self, habit_name: str, is_device: bool = False):
        self.repo.add(habit_name, is_device)
    
    def get_habits(self) -> list[Habit]:
        return self.repo.get_all()
    
    def update_habit(self, field: str, value: str, habit_name: str):
        self.repo.update_habit(field, value, habit_name)
    
    def delete_habit(self, habit_name: str):
        self.repo.delete_habit(habit_name)
            
    def log_habit(self, habit_name: str, state: str = "NaV", self_reported: bool = True):
        self.repo.log(habit_name, state, self_reported)
    
    def get_habit_logs(self, habit_name: Optional[str] = None):
        return self.repo.get_logs(habit_name)

    
    def add_rule(self, habit_id: int, rule: Rule):
        self.repo.add_rule(habit_id, rule)