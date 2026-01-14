from objects.habitrepository import HabitRepository
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from db.sqlite import get_connection
from config import scheduler
from utils.singleton import _SingletonWrapper
from utils.decorators import *

def test_job_func(text):
    print(f"Hello {text}!")

@_SingletonWrapper.singleton
class HabitScheduler:
    scheduler = BackgroundScheduler(timezone="EST")
    
    def __init__(self):
        pass
    
    def start(self):
        self.scheduler.start()
    
    def schedule_habit(self, user_id: int, habit_id: int):
        self.scheduler.add_job(
            func=test_job_func,
            trigger=CronTrigger()
        )
    
    def reschedule_habit(self, user_id: int):
        return
    
    def pause_habit(self, user_id: int):
        return
        
    def activate_habit(self, user_id: int):
        return
    
    def restore_jobs(self):
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT user_id, habit_name, day, hour, minute
                FROM habit_rules
                WHERE active = 1
            """).fetchall()

            for r in rows:
                self.scheduler.add_job(
                    func=test_job_func,
                    trigger=CronTrigger(
                        day=r["day"],
                        hour=r["hour"],
                        minute=r["minute"],
                    ),
                    id=r["user_id"],
                    name=r["habit_name"],
                )

            
    @test_only
    def schedule_test_habit(self, user_id: int):
        return