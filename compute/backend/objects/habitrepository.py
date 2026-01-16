from db.sqlite import get_connection
from datetime import datetime
from utils.time import _timestamp, break_timestamp
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
                INSERT INTO habit_rules (user_id, job_id, habit_id, day, hour, minute, count, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (self.user_id, f"{self.user_id}_job_test", habit_id, rule.day, rule.hour, rule.minute, 1, rule.active)
            )
            
            
    def generate_rules(self):
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM habits WHERE user_id = ?
                """,
                (self.user_id,)
            ).fetchall()
            
            names = [r['name'] for r in rows]
            
            for name in names:
                rows = conn.execute(
                    """
                    SELECT * FROM habit_logs WHERE user_id = ? AND habit_name = ?
                    """,
                    (self.user_id,name,)
                ).fetchall()
                
                habit_data = break_timestamp(DataFrame(rows, columns=rows[0].keys()))
                for i in range(0, 7):
                    df = habit_data[habit_data['day_of_week'] == i]
                    try:
                        hour = int(df['hour'].mean())
                        minute = int(df['minute'].mean())
                    except:
                        hour = 0
                        minute = 0
                        
                    rule = Rule(i, hour, minute, True)
                
                    conn.execute(
                        """
                        INSERT INTO habit_rules (user_id, job_id, habit_id, day, hour, minute, count, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (self.user_id,f"{self.user_id}_{name}_{rule.day}_test",f"{self.user_id}_{name}_test", rule.day, rule.hour, rule.minute, 1, int(rule.active))
                    )
                
    
    def drop_all_rules(self):
        with get_connection() as conn:
            conn.execute(
                """
                DELETE FROM habit_rules
                """
            )
    def drop_dead_rules(self):
        with get_connection() as conn:
            conn.execute(
                """
                DELETE FROM habit_rules WHERE hour = 0 AND minute = 0
                """
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