from db.sqlite import get_connection
from datetime import datetime
from utils.time import _timestamp
from objects.habit import Habit
from objects.rule import Rule
from typing import Optional
from pandas import DataFrame

class HabitRepository:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def add(self, habit_name: str, is_device: bool = False):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO habits (user_id, name, is_device) VALUES (?, ?, ?)",
                (self.user_id, habit_name, int(is_device))
            )

    def get_all(self) -> list[Habit]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM habits WHERE user_id = ?",
                (self.user_id,)
            ).fetchall()
           
        habits: list[Habit] = [] 
        for r in rows:
            h = Habit(
                habit_name = r['name'],
                is_device=bool(r['is_device']),
                assoc_mqtt_topic=r['mqtt_topic']
            )
            habits.append(h)
            
        return habits

    def log(self, habit_name: str, state: str, self_reported: bool):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO habit_logs (user_id, habit_name, timestamp, state, self_reported) VALUES (?, ?, ?, ?, ?)",
                (self.user_id, habit_name, _timestamp(), state, int(self_reported))
            )
    
    def get_logs(self, habit_name: Optional[str] = None):
        query = """
                SELECT * FROM habit_logs WHERE user_id = ?
                """
        params: tuple = (self.user_id,)
        
        if habit_name:
            query += " AND habit_name = ?"
            params = params + (habit_name,)
        
        with get_connection() as conn:
            rows = conn.execute(
                query,
                params
                ).fetchall()
            
            if not rows:
                return DataFrame()
            
            df = DataFrame(rows, columns=rows[0].keys())
            return df
        
    def add_rule(self, habit_id: int, rule: Rule):
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO habit_rules (user_id, job_id, habit_id, day, hour, minute, count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (self.user_id, f"{self.user_id}_job_test", habit_id, rule.day, rule.hour, rule.minute, 1)
            )
        
    def get_rules(self):
        with get_connection() as conn:
            conn.execute(
                """
                SELECT * FROM habit_rules WHERE user_id = ?
                """,
                (self.user_id,)
            )
        
    def upsert_rule(self):
        return
    
    def delete_rule(self):
        return