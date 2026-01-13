import sqlite3
from pathlib import Path
import pandas as pd
from typing import NamedTuple
from utils.time import break_timestamp

DB_PATH: Path = Path("db/habits.db")

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def reset_habit_tables(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM habit_logs;")
    conn.execute("DELETE FROM habits;")
    conn.execute("DELETE FROM users;")
    conn.execute("""
        DELETE FROM sqlite_sequence
        WHERE name IN ('users', 'habits', 'habit_logs');
    """)
    conn.commit()

    
def add_user() -> int:
    with get_connection() as conn:
        cursor: sqlite3.Cursor = conn.execute(
            """
            INSERT INTO users DEFAULT VALUES;
            """
        )
        
        return cursor.lastrowid

def add_habit(user_id: int) -> int:
    with get_connection() as conn:
        cursor: sqlite3.Cursor = conn.execute(
                    """
                    INSERT INTO habits (user_id, job_id, mqtt_topic, name, is_device)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        user_id,
                        "Not Implemented",
                        "Not Implemented",
                        "Not Implemented",
                        0
                )
        )
        return 1
    
class HabitQueryResult(NamedTuple):
    user_id: int
    habit_name: str
    data: pd.DataFrame
        
def query_habit(user_id: int, habit_name: str) -> HabitQueryResult:
    with get_connection() as conn:
        cursor: sqlite3.Cursor = conn.execute(
            """
            SELECT timestamp, state, self_reported FROM habit_logs WHERE user_id = (?) AND habit_name = (?);
            """,
            (
                user_id,
                habit_name,
            )
        )
        
        rows = cursor.fetchall()
        if not rows:
            return HabitQueryResult(
        user_id=user_id,
        habit_name=habit_name,
        data=pd.DataFrame()
    )
        
        df = pd.DataFrame(data=rows, columns=rows[0].keys())
        df = break_timestamp(df)
        df = df[['day_of_week', 'hour', 'minute', 'state', 'self_reported']]
        
        return HabitQueryResult(
            user_id=user_id,
            habit_name=habit_name,
            data=df
        )