from db.sqlite import get_connection

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        );

        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            is_device BOOLEAN DEFAULT 0,
            UNIQUE(user_id, name),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            habit_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            state TEXT,
            self_reported BOOLEAN,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
