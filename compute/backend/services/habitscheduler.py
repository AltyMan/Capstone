from models.habitrepository import HabitRepository
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from db.sqlite import get_connection
from config import scheduler
from utils.singleton import _SingletonWrapper
from utils.decorators import *

@_SingletonWrapper.singleton
class HabitScheduler:
    scheduler = BackgroundScheduler(timezone="EST")
    
    def __init__(self):
        pass
    
    def start(self):
        self.scheduler.start()
    
    def schedule_habit(user_id: int):
        return
    
    def reschedule_habit(user_id: int):
        return
    
    def pause_habit(user_id: int):
        return
        
    def activate_habit(user_id: int):
        return  
            
    @test_only
    def schedule_test_habit(user_id: int):
        return