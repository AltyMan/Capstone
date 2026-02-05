import sqlite3
from pathlib import Path
import pandas as pd
from typing import NamedTuple

DB_PATH: Path = Path("db/habits.db")

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # conn.execute("PRAGMA foreign_keys = ON;") 
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