import csv
import random
import sqlite3
from pathlib import Path
from init_db import init_db
from sqlite import get_connection

DB_PATH = "db/habits.db"
CSV_PATH = "compute/backend/data/habit_data.csv"

NUM_USERS = 5  # change as needed


get_conn = get_connection


def create_users(conn, n):
    user_ids = []
    for _ in range(n):
        cur = conn.execute("INSERT INTO users DEFAULT VALUES;")
        user_ids.append(cur.lastrowid)
    return user_ids


def get_or_create_habit(conn, user_id, habit_name, is_device):
    row = conn.execute(
        """
        SELECT id FROM habits
        WHERE user_id = ? AND name = ?
        """,
        (user_id, habit_name),
    ).fetchone()

    if row:
        return row["id"]

    mqtt_topic = f"{user_id}/provider/{habit_name}"

    cur = conn.execute(
        """
        INSERT INTO habits (user_id, mqtt_topic, name, is_device)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, mqtt_topic, habit_name, int(is_device)),
    )
    return cur.lastrowid


def main():
    conn = get_conn()

    print("Creating users...")
    user_ids = create_users(conn, NUM_USERS)

    print("Seeding habit logs...")
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            user_id = random.choice(user_ids)

            habit_name = row["habit"]
            timestamp = row["timestamp"]
            state = row["state"]
            is_device = row["is_device"].lower() == "true"
            self_reported = row["self_reported"].lower() == "true"

            # ensure habit exists
            get_or_create_habit(
                conn,
                user_id=user_id,
                habit_name=habit_name,
                is_device=is_device,
            )

            # insert log
            conn.execute(
                """
                INSERT INTO habit_logs (
                    user_id, habit_name, timestamp, state, self_reported
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    habit_name,
                    timestamp,
                    state,
                    int(self_reported),
                ),
            )

    conn.commit()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    init_db()
    main()
