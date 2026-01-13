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
            job_id TEXT NOT NULL,
            mqtt_topic TEXT,
            name TEXT NOT NULL,
            is_device BOOLEAN DEFAULT 0,
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
        
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id TEXT NOT NULL,
            habit_id INTEGER NOT NULL,
            count INTEGER DEFAULT 0,
            unique(job_id)
            FOREIGN KEY(user_id) REFERENCES users(id)
            FOREIGN KEY(habit_id) REFERENCES habits(id)
        );
        """)