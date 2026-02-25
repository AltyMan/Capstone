from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from zoneinfo import ZoneInfo

from db.sqlite import get_connection
from utils.singleton import _SingletonWrapper
from utils.decorators import test_only


@test_only
def test_job_func(user_id: int, habit_id: int):
    print(f"Triggering habit {habit_id} for user {user_id}")


@_SingletonWrapper.singleton
class HabitScheduler:

    def __init__(self):
        # Use proper timezone (handles DST correctly)
        self.scheduler = BackgroundScheduler(timezone=ZoneInfo("America/Toronto"))

    # ------------------------
    # Core lifecycle
    # ------------------------

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

    # ------------------------
    # Internal helpers
    # ------------------------

    def _build_job_id(self, user_id: int, habit_id: int) -> str:
        return f"{user_id}:{habit_id}"

    def _build_trigger(self, day: str, hour: int, minute: int) -> CronTrigger:
        return CronTrigger(
            day_of_week=day,
            hour=hour,
            minute=minute,
            timezone=self.scheduler.timezone
        )

    # ------------------------
    # Public API
    # ------------------------

    def schedule_habit(self, user_id: int, habit_id: int | str):
        """
        Schedule a habit based on DB rule.
        """

        with get_connection() as conn:
            row = conn.execute("""
                SELECT day, hour, minute
                FROM habit_rules
                WHERE user_id = ?
                AND habit_id = ?
            """, (user_id, habit_id)).fetchone()

            if not row:
                raise ValueError("Habit rule not found")

        job_id = self._build_job_id(user_id, habit_id)

        trigger = self._build_trigger(
            day=row["day"],
            hour=row["hour"],
            minute=row["minute"]
        )
        
        print(f"Day: {row['day']}, Hour: {row['hour']}, Minute: {row['minute']}")

        self.scheduler.add_job(
            func=test_job_func,
            trigger=trigger,
            id=job_id,
            args=[user_id, habit_id],
            replace_existing=True,
        )

        with get_connection() as conn:
            conn.execute("""
                UPDATE habit_rules
                SET job_id = ?, active = 1
                WHERE user_id = ?
                AND habit_id = ?
            """, (job_id, user_id, habit_id))
            conn.commit()

    def reschedule_habit(self, user_id: int, habit_id: int):
        """
        Remove and recreate job from DB rule.
        """
        self.pause_habit(user_id, habit_id)
        self.schedule_habit(user_id, habit_id)

    def pause_habit(self, user_id: int, habit_id: int):
        job_id = self._build_job_id(user_id, habit_id)

        job = self.scheduler.get_job(job_id)
        if job:
            job.remove()

        with get_connection() as conn:
            conn.execute("""
                UPDATE habit_rules
                SET active = 0
                WHERE user_id = ?
                AND habit_id = ?
            """, (user_id, habit_id))
            conn.commit()

    def activate_habit(self, user_id: int, habit_id: int):
        self.schedule_habit(user_id, habit_id)

    def restore_jobs(self):
        """
        Rebuild all active jobs from DB.
        Call this once at startup.
        """

        with get_connection() as conn:
            rows = conn.execute("""
                SELECT user_id, habit_id, day, hour, minute
                FROM habit_rules
                WHERE active = 1
            """).fetchall()

        for r in rows:
            job_id = self._build_job_id(r["user_id"], r["habit_id"])

            trigger = self._build_trigger(
                day=r["day"],
                hour=r["hour"],
                minute=r["minute"]
            )

            self.scheduler.add_job(
                func=test_job_func,
                trigger=trigger,
                id=job_id,
                args=[r["user_id"], r["habit_id"]],
                replace_existing=True
            )

    def print_active_jobs(self, user_id: int):
        jobs = self.scheduler.get_jobs()

        for job in jobs:
            if job.id.startswith(f"{user_id}:"):
                print(f"Job ID: {job.id} | Next run: {job.next_run_time}")

    # ------------------------
    # Testing
    # ------------------------

    @test_only
    def schedule_test_habit(self, user_id: int):
        from apscheduler.triggers.date import DateTrigger
        from datetime import datetime, timedelta

        run_time = datetime.now(self.scheduler.timezone) + timedelta(seconds=10)

        self.scheduler.add_job(
            func=test_job_func,
            trigger=DateTrigger(run_date=run_time),
            id=f"test:{user_id}",
            args=[user_id, 0],
            replace_existing=True
        )