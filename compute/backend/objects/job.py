from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

class Job:
    func: function = None
    trigger: CronTrigger | DateTrigger = None
    id: str = None
    name: str = None
    args: any | None = None
    
    def __init__(self):
        pass