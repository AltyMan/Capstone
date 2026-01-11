import sqlite3
from pathlib import Path

DB_PATH: Path = Path("db/habits.db")

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
